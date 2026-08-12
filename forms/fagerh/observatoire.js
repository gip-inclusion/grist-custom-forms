(function () {
  "use strict";
  var dashboardUrl = "/api/fagerh-analytics/v1/dashboard";
  var observatoryUrl = "/api/fagerh-analytics/v1/observatoire/";
  var regionSelect = document.getElementById("region-select");
  var completionSelect = document.getElementById("completion-select");
  var deviceSelect = document.getElementById("device-select");
  var generateButton = document.getElementById("generate-button");
  var printButton = document.getElementById("print-button");
  var status = document.getElementById("status");
  var report = document.getElementById("report");

  function esc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (char) {
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char];
    });
  }
  function number(value) {
    return value == null ? "Non disponible" : new Intl.NumberFormat("fr-FR", {maximumFractionDigits: 1}).format(value);
  }
  function percent(value) {
    return value == null ? "Non disponible" : new Intl.NumberFormat("fr-FR", {style:"percent", maximumFractionDigits:1}).format(value);
  }
  async function json(url, options) {
    var response = await fetch(url, Object.assign({credentials: "same-origin"}, options || {}));
    var payload = await response.json();
    if (!response.ok || payload.status === "error") {
      throw new Error((payload.error && payload.error.message) || "Chargement impossible.");
    }
    return payload;
  }
  async function dashboard(filters) {
    return json(dashboardUrl, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({filters: filters})
    });
  }
  function metricCards(items) {
    if (!Array.isArray(items) || !items.length) return '<p class="muted">Donnée non disponible.</p>';
    return items.map(function (item) {
      var children = Array.isArray(item.children) && item.children.length
        ? "<ul>" + item.children.map(function (child) {
            return "<li>" + esc(child.label) + " : <strong>" + esc(number(child.value)) + "</strong></li>";
          }).join("") + "</ul>" : "";
      return '<section class="card"><h3>' + esc(item.label || "Indicateur") + '</h3>' +
        (item.value !== undefined ? '<p class="card-value">' + esc(number(item.value)) + '</p>' : "") +
        (item.unit ? "<small>" + esc(item.unit) + "</small>" : "") + children + "</section>";
    }).join("");
  }
  function bars(labels, counts, rates, limit, showValues) {
    var rows = labels.map(function (label, index) {
      var value = counts[index] || 0;
      var rate = rates ? rates[index] : null;
      return {label: label, value: value, rate: rate == null ? 0 : rate};
    }).filter(function (row) { return row.value > 0; })
      .sort(function (a, b) { return b.value - a.value; })
      .slice(0, limit || labels.length);
    var total = counts.reduce(function (sum, value) { return sum + (Number(value) || 0); }, 0);
    return rows.map(function (row) {
      var share = rates ? row.rate : (total ? row.value / total : 0);
      var displayedValue = showValues
        ? '<span class="bar-absolute">' + esc(number(row.value)) + ' ETP</span><span class="bar-percentage">' + esc(percent(share)) + '</span>'
        : esc(percent(share));
      return '<div class="bar-row"><span>' + esc(row.label) + '</span><span class="bar-track"><span class="bar-fill" style="width:' +
        Math.min(100, share * 100) + '%"></span></span><strong class="bar-values">' + displayedValue + '</strong></div>';
    }).join("") || '<p class="muted">Donnée non disponible.</p>';
  }
  function networkCards(network, deviceFocus, focusedValue, establishmentCount) {
    var devices = (network.devices || []).filter(function (device) {
      return deviceFocus === "all" || device.id === deviceFocus;
    });
    if (!devices.length && deviceFocus !== "all") {
      var labels = {deac:"DEAc", pec:"PEC", other_eval:"Autres évaluations"};
      return '<section class="card"><h3>' + esc(labels[deviceFocus] || deviceFocus.toUpperCase()) + '</h3>' +
        '<p><strong>' + esc(number(focusedValue)) + '</strong> personnes déclarées</p>' +
        '<p><strong>' + esc(number(establishmentCount)) + '</strong> établissement(s) concerné(s)</p></section>';
    }
    return devices.map(function (device) {
      var publicMetrics = ((device.public || {}).metrics || []);
      return '<section class="card"><h3>' + esc(device.label) + '</h3><p>' + esc(device.subtitle || "") + '</p>' +
        publicMetrics.map(function (metric) {
          return '<p><strong>' + esc(metric.display_value || number(metric.value)) + '</strong> ' + esc(metric.label) + '</p>';
        }).join("") + "</section>";
    }).join("");
  }
  function establishmentRows(section, deviceFocus) {
    var rows = (section && section.items) || [];
    if (deviceFocus === "all") return rows;
    var expected = {esrp:"ESRP", espo:"ESPO", ueros:"UEROS", deac:"DEAC", pec:"PEC", other_eval:"AUTRES ÉVALUATIONS"}[deviceFocus];
    return rows.filter(function (row) {
      return (row.dispositifs || []).map(function (value) { return String(value).toUpperCase(); }).indexOf(expected) >= 0;
    });
  }
  function renderEstablishments(section, deviceFocus) {
    var rows = establishmentRows(section, deviceFocus);
    if (!rows.length) return '<p class="muted">Aucun établissement exploitable dans ce périmètre.</p>';
    var labels = {esrp:"ESRP", espo:"ESPO", ueros:"UEROS", deac:"DEAc", pec:"PEC", other_eval:"Autres évaluations"};
    return '<div class="cards">' + rows.slice(0, 24).map(function (row) {
      var statuses = (row.statuses || []).map(function (statusValue) {
        return statusValue === "completed" ? "Terminé" : statusValue === "in_progress" ? "Non terminé" : statusValue;
      }).join(" · ");
      var volumes = Object.keys(labels).filter(function (key) {
        return row.totals && Number(row.totals[key]) > 0;
      }).map(function (key) {
        return "<li>" + esc(labels[key]) + " : <strong>" + esc(number(row.totals[key])) + " personnes</strong></li>";
      }).join("");
      return '<section class="card establishment-card"><h3>' + esc(row.name || "Établissement FINESS " + row.finess_main) + '</h3>' +
        '<p>Département ' + esc(row.department_code || "non renseigné") + '</p>' +
        '<p><small>FINESS : ' + esc(row.finess_main || "non renseigné") + '</small></p>' +
        ((row.dispositifs || []).length ? '<p><strong>Dispositifs :</strong> ' + esc(row.dispositifs.join(" · ")) + '</p>' : "") +
        (statuses ? '<p><strong>Questionnaire :</strong> ' + esc(statuses) + '</p>' : "") +
        (volumes ? '<ul>' + volumes + '</ul>' : '<p class="muted">Aucun volume déclaré.</p>') +
        '</section>';
    }).join("") + "</div>";
  }
  function findIndicator(indicators, id) {
    return indicators && indicators[id] ? indicators[id].value : null;
  }
  function focusValue(overview, deviceFocus) {
    var indicators = overview.indicators || {};
    if (deviceFocus === "deac") return overview.deac ? overview.deac.value : null;
    if (deviceFocus === "all") return findIndicator(indicators, "total");
    return findIndicator(indicators, deviceFocus);
  }
  function focusedActivityCards(activity, overview, deviceFocus) {
    var cards = (activity && activity.cards) || [];
    if (deviceFocus === "all") return cards;
    var indicator = (overview.indicators || {})[deviceFocus];
    if (deviceFocus === "deac") {
      return [{id:"people.received.deac", label:"Personnes accompagnées en DEAc", value:(overview.deac || {}).value, unit:"personnes"}];
    }
    if (deviceFocus === "pec" || deviceFocus === "other_eval") {
      return [{id:"people.received." + deviceFocus, label:deviceFocus === "pec" ? "Personnes reçues en PEC" : "Personnes reçues dans les autres évaluations", value:indicator ? indicator.value : 0, unit:"personnes"}];
    }
    return cards.filter(function (card) {
      return String(card.id || "").indexOf(deviceFocus) >= 0;
    });
  }
  function render(dashboardPayload, regionalPayload, generatedAt, isFrance, deviceFocus) {
    var overview = dashboardPayload.overview || {};
    var indicators = overview.indicators || {};
    var selectedValue = focusValue(overview, deviceFocus);
    var selectedEstablishments = establishmentRows(dashboardPayload.establishments || {}, deviceFocus);
    var focusLabels = {esrp:"ESRP", espo:"ESPO", ueros:"UEROS", deac:"DEAc", pec:"PEC", other_eval:"autres évaluations"};
    document.getElementById("report-title").textContent = "Observatoire 2025 — " + regionalPayload.region.label;
    document.getElementById("total-people").textContent = number(selectedValue);
    document.getElementById("total-people-label").textContent =
      deviceFocus === "pec" || deviceFocus === "other_eval"
        ? "personnes reçues en " + focusLabels[deviceFocus]
        : deviceFocus === "all"
          ? "volumes de personnes déclarés, non dédupliqués"
          : "personnes accompagnées en " + focusLabels[deviceFocus];
    var focusNotice = document.getElementById("device-focus-notice");
    focusNotice.hidden = deviceFocus === "all";
    focusNotice.textContent = deviceFocus === "all" ? "" :
      "Focalisation : " + focusLabels[deviceFocus] + ". Seules les données rattachables à ce dispositif sont affichées.";
    document.getElementById("questionnaire-count").textContent = number(
      deviceFocus === "all" ? regionalPayload.questionnaire_count : selectedEstablishments.length
    );
    document.getElementById("questionnaire-count-label").textContent =
      deviceFocus === "all" ? (regionalPayload.completion_scope_label || "Questionnaires") : "Établissements concernés";
    document.getElementById("completion-scope-summary").textContent =
      (regionalPayload.completion_scope_label || "Tous les questionnaires") + ", sans extrapolation";
    document.getElementById("freshness").textContent = dashboardPayload.freshness_at ? new Date(dashboardPayload.freshness_at).toLocaleString("fr-FR") : "Non indiquée";
    document.getElementById("network-cards").innerHTML = networkCards(dashboardPayload.network_overview || {}, deviceFocus, selectedValue, selectedEstablishments.length);
    document.getElementById("establishments-section").hidden = isFrance;
    document.getElementById("establishments").innerHTML = isFrance ? "" : renderEstablishments(dashboardPayload.establishments || {}, deviceFocus);
    document.getElementById("profile-section").hidden = deviceFocus !== "all";
    document.getElementById("information-section").hidden = deviceFocus !== "all";
    document.getElementById("institutional-section").hidden = deviceFocus !== "all";
    document.getElementById("health-section").hidden = deviceFocus !== "all";
    document.getElementById("mean-age").textContent = regionalPayload.age.estimated_mean == null ? "Non disponible" : number(regionalPayload.age.estimated_mean) + " ans";
    document.getElementById("age-bars").innerHTML = bars(regionalPayload.age.labels, regionalPayload.age.counts, null, 12);
    document.getElementById("low-level-rate").textContent = percent(regionalPayload.education.level_4_or_less_rate);
    document.getElementById("level-bars").innerHTML = bars(regionalPayload.education.labels, regionalPayload.education.counts, null, 7);
    document.getElementById("handicap-bars").innerHTML = bars(regionalPayload.main_disability.labels, regionalPayload.main_disability.counts, regionalPayload.main_disability.rates, 7);
    document.getElementById("age-method").textContent = regionalPayload.methodology.age;
    document.getElementById("insertion-section").hidden = deviceFocus !== "all" && deviceFocus !== "esrp";
    document.getElementById("insertion-cards").innerHTML = metricCards((dashboardPayload.insertion || {}).items);
    document.getElementById("activity-cards").innerHTML = metricCards(focusedActivityCards(dashboardPayload.activity || {}, overview, deviceFocus));
    document.getElementById("modalites-cards").innerHTML = metricCards((dashboardPayload.modalites || {}).items);
    document.getElementById("orientation-cards").innerHTML = metricCards(((dashboardPayload.network_overview || {}).devices || []).filter(function (device) {
      return deviceFocus === "all" || device.id === deviceFocus;
    }).flatMap(function (device) {
      return ((device.results || {}).items || []).filter(function (item) { return String(item.id || "").indexOf("precon") >= 0; });
    }));
    document.getElementById("participation-cards").innerHTML = metricCards((dashboardPayload.participation_institutionnelle || {}).items);
    var institutions = (regionalPayload.institutional_network || {}).items || [];
    document.getElementById("institutional-network-cards").innerHTML = institutions.map(function (item) {
      return '<section class="card"><h3>' + esc(item.label) + '</h3><ul>' +
        '<li>Participation directe : <strong>' + esc(number(item.direct)) + '</strong></li>' +
        '<li>Représentation FAGERH : <strong>' + esc(number(item.represented)) + '</strong></li>' +
        '<li>Non : <strong>' + esc(number(item.no)) + '</strong></li>' +
        (item.unknown ? '<li>Non renseigné : <strong>' + esc(number(item.unknown)) + '</strong></li>' : "") +
        '</ul></section>';
    }).join("");
    var health = regionalPayload.health_support || {};
    var healthCategories = health.categories || [];
    document.getElementById("health-method").textContent = health.method || "";
    document.getElementById("health-support-bars").innerHTML = bars(
      healthCategories.map(function (item) { return item.label; }),
      healthCategories.map(function (item) { return item.value; }),
      null,
      8,
      true
    );
    var accommodation = regionalPayload.accommodation || {};
    document.getElementById("accommodation-cards").innerHTML = metricCards([
      {label: "Personnes hébergées", value: accommodation.people, unit: "personnes"}
    ]);
    document.getElementById("unavailable-cards").innerHTML = regionalPayload.unavailable_indicators.map(function (item) {
      return '<section class="card unavailable"><h3>' + esc(item.label) + '</h3><p class="card-value">Non disponible</p><small>' + esc(item.reason) + '</small></section>';
    }).join("");
    document.getElementById("scope-method").textContent = regionalPayload.methodology.scope;
    document.getElementById("generated-at").textContent = "Rapport généré le " + new Date(generatedAt || Date.now()).toLocaleString("fr-FR") + ".";
    report.hidden = false;
    printButton.disabled = false;
  }
  async function loadRegions() {
    try {
      var response = await dashboard({completion_scope: "all"});
      var regions = (((response.result || {}).geography || {}).regions || [])
        .filter(function (item) { return item.questionnaire_count > 0; })
        .sort(function (a, b) { return a.label.localeCompare(b.label, "fr"); });
      regionSelect.innerHTML = '<option value="france">France entière</option>' + regions.map(function (item) {
        return '<option value="' + esc(item.region_code) + '">' + esc(item.label) + " — " + esc(item.questionnaire_count) + " questionnaire(s)</option>";
      }).join("");
      regionSelect.value = "france";
      regionSelect.disabled = false;
      generateButton.disabled = false;
      status.textContent = "Chargement du rapport France entière…";
      await generate();
    } catch (error) {
      status.textContent = error.message;
      status.className = "status error";
    }
  }
  async function generate() {
    var code = regionSelect.value;
    var completionScope = completionSelect.value || "all";
    var deviceFocus = deviceSelect.value || "all";
    if (!code) {
      status.textContent = "Sélectionnez d’abord une région.";
      return;
    }
    generateButton.disabled = true;
    printButton.disabled = true;
    status.className = "status";
    status.textContent = "Calcul du rapport régional…";
    try {
      var dashboardFilters = {completion_scope: completionScope};
      if (code !== "france") {
        dashboardFilters.region_code = code;
      }
      var responses = await Promise.all([
        dashboard(dashboardFilters),
        json(observatoryUrl + encodeURIComponent(code) + "?completion_scope=" + encodeURIComponent(completionScope))
      ]);
      render(responses[0].result || {}, responses[1].result || {}, responses[0].generated_at, code === "france", deviceFocus);
      status.textContent = "Rapport prêt. « Proposer le PDF » ouvre l’impression ; choisissez « Enregistrer au format PDF ».";
    } catch (error) {
      status.textContent = error.message;
      status.className = "status error";
    } finally {
      generateButton.disabled = false;
    }
  }
  generateButton.addEventListener("click", generate);
  printButton.addEventListener("click", function () { window.print(); });
  loadRegions();
}());
