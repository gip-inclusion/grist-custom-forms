(function (global) {
  "use strict";

  var ANALYTICS_HEALTH_URL = "/api/fagerh-analytics/v1/health";
  var ANALYTICS_DASHBOARD_URL = "/api/fagerh-analytics/v1/dashboard";
  var DEFAULT_TAB_ID = "section-overview";
  var TAB_ORDER = [
    "section-overview",
    "section-activity",
    "section-network-overview",
    "section-modalites",
    "section-insertion",
    "section-participation",
    "section-internal"
  ];
  var LEGACY_HASHES = {
    "#section-overview": "section-overview",
    "#overview": "section-overview",
    "#section-activity": "section-activity",
    "#activity": "section-activity",
    "#section-network-overview": "section-network-overview",
    "#network": "section-network-overview",
    "#section-modalites": "section-modalites",
    "#modalites": "section-modalites",
    "#section-insertion": "section-insertion",
    "#insertion": "section-insertion",
    "#section-participation": "section-participation",
    "#participation": "section-participation",
    "#section-internal": "section-internal",
    "#internal": "section-internal"
  };

  function buildDashboardFilters(raw) {
    var filters = {};
    var completionScope = String((raw && raw.completion_scope) || "all").trim();
    filters.completion_scope = completionScope || "all";

    var regionCode = String((raw && raw.region_code) || "").trim();
    if (regionCode) {
      filters.region_code = regionCode;
    }

    var departmentCode = String((raw && raw.department_code) || "").trim();
    if (departmentCode) {
      filters.department_code = departmentCode;
    }

    var finess = String((raw && raw.finess_main) || "").trim();
    if (finess) {
      filters.finess_main = finess;
    }

    var dispositif = String((raw && raw.dispositifs) || "").trim();
    if (dispositif) {
      filters.dispositifs = dispositif;
    }

    return filters;
  }

  function buildOverviewModel(args) {
    var dashboard = args && args.dashboard ? args.dashboard : {};
    var overview = dashboard.overview || {};
    var indicators = overview.indicators || {};
    var activity = dashboard.activity || {};
    var otherEvaluations = activity.other_evaluations || {};
    return {
      title: overview.title || "Vue d’ensemble",
      questionnaireCount: overview.questionnaire_count || 0,
      totalValue: readValue(indicators.total),
      totalLabel: readLabel(indicators.total, "Nombre de personnes reçues toutes catégories confondues"),
      totalUnit: readUnit(indicators.total, "personnes déclarées"),
      formula: overview.formula || "",
      completionNotice: overview.completion_notice || "",
      components: [
        normalizeMetric(indicators.esrp, "ESRP"),
        normalizeMetric(indicators.espo, "ESPO"),
        normalizeMetric(indicators.ueros, "UEROS"),
        normalizeMetric(indicators.pec, "PEC"),
        normalizeMetric(indicators.other_eval, "Autres dispositifs d’évaluation")
      ],
      preliminaryEvaluations: normalizeMetric(indicators.preliminary_evaluations, "Évaluations préliminaires"),
      otherEvaluationDetails: Array.isArray(otherEvaluations.items) ? otherEvaluations.items.map(function (item) {
        return normalizeMetric(item, item && item.label ? item.label : "Autres évaluations");
      }) : [],
      deac: overview.deac || {},
      indicators: indicators
    };
  }

  function buildNetworkOverviewModel(args) {
    var dashboard = args && args.dashboard ? args.dashboard : {};
    var network = dashboard.network_overview || {};
    return {
      title: network.title || "Le réseau en un regard",
      status: network.status || "available",
      message: network.message || "",
      devices: Array.isArray(network.devices) ? network.devices : []
    };
  }

  function renderOverviewMarkup(model) {
    return {
      total: model.totalValue === null ? "Non alimenté" : formatNumber(model.totalValue),
      breakdownHtml: model.components.map(function (item, index) {
        return renderMetricCard(item, { compact: index > 1 });
      }).join(""),
      otherEvaluationDetailsHtml: model.otherEvaluationDetails.map(function (item) {
        return "<li>" + escapeHtml(item.label) + " : <strong>" + escapeHtml(item.value === null ? "Donnée non disponible" : formatNumber(item.value)) + "</strong></li>";
      }).join("")
    };
  }

  function resolveTabId(hash) {
    var normalized = String(hash || "").trim();
    if (!normalized) {
      return DEFAULT_TAB_ID;
    }
    if (LEGACY_HASHES[normalized]) {
      return LEGACY_HASHES[normalized];
    }
    if (normalized.charAt(0) !== "#") {
      normalized = "#" + normalized;
    }
    return LEGACY_HASHES[normalized] || DEFAULT_TAB_ID;
  }

  async function loadDashboard() {
    var elements = getElements();
    setGlobalStatus(elements, "Chargement du tableau de bord…", "loading");
    clearError(elements);
    try {
      var filters = buildDashboardFilters(readFormState(elements));
      var responses = await Promise.all([
        fetchJson(ANALYTICS_HEALTH_URL),
        fetchJson(ANALYTICS_DASHBOARD_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ filters: filters })
        })
      ]);
      var health = responses[0];
      var dashboardResponse = responses[1];
      if ((dashboardResponse.status || "") !== "success") {
        throw createApiError(dashboardResponse);
      }
      syncCapabilityDrivenFilters(elements, health);
      renderDashboard(elements, health, dashboardResponse);
      setGlobalStatus(elements, "Tableau de bord chargé.", "success");
    } catch (error) {
      renderFatalError(elements, error);
    }
  }

  function renderDashboard(elements, health, response) {
    var result = response.result || {};
    var overview = result.overview || {};
    var model = buildOverviewModel({ dashboard: result });
    var rendered = renderOverviewMarkup(model);

    renderHeaderMeta(elements, overview, health);

    elements.overviewStatus.textContent = (health.analytics_status === "available")
      ? "Source disponible."
      : "Source indisponible.";
    elements.overviewStatus.className = "status-banner is-" + (health.analytics_status === "available" ? "success" : "warning");

    if (overview.status === "error") {
      elements.totalValue.textContent = "Donnée non disponible";
      elements.totalUnit.textContent = "";
      elements.breakdown.innerHTML = renderPlaceholderCard("Vue d’ensemble", overview.message || "Vue d’ensemble indisponible pour le moment.");
      elements.preliminaryCard.innerHTML = "";
      elements.otherEvalCard.innerHTML = "";
      elements.deacCard.innerHTML = "";
      elements.formula.textContent = "";
    } else {
      elements.totalValue.textContent = rendered.total;
      elements.totalUnit.textContent = model.totalUnit;
      elements.breakdown.innerHTML = rendered.breakdownHtml;
      elements.preliminaryCard.innerHTML = renderDetailMetric(model.preliminaryEvaluations, "Évaluations préliminaires");
      elements.otherEvalCard.innerHTML = (
        "<article class=\"analytics-detail-card\">" +
          "<h3>Autres dispositifs d’évaluation</h3>" +
          "<p class=\"analytics-section-help\">Détail du total autres dispositifs d’évaluation.</p>" +
          "<ul class=\"analytics-list\">" + rendered.otherEvaluationDetailsHtml + "</ul>" +
        "</article>"
      );
      elements.deacCard.innerHTML = renderDeacCard(model.deac);
      elements.formula.textContent = model.formula;
    }

    if (model.completionNotice) {
      elements.notice.hidden = false;
      elements.notice.textContent = model.completionNotice;
    } else {
      elements.notice.hidden = true;
      elements.notice.textContent = "";
    }

    renderOverviewMeta(elements, overview, health);
    renderNetworkOverview(elements, result.network_overview || {});
    renderActiveFilters(elements, result.filters || {});
    renderActivity(elements, result.activity || {}, overview);
    renderModalites(elements, result.modalites || {});
    renderInsertion(elements, result.insertion || {});
    renderParticipation(elements, result.participation_institutionnelle || {});
    renderGeography(elements, result.geography || {}, readFormState(elements));
    renderEstablishments(elements, result.establishments || {});
    renderInternal(elements, result.internal || {});
    renderQuality(elements, result.quality || {});
  }

  function renderHeaderMeta(elements, overview, health) {
    var statusLabel = String(health.analytics_status || "unknown");
    var counts = overview.questionnaire_status_counts || {};
    elements.dataStatus.textContent = health.generated_at
      ? "Dernière vérification de la source : " + health.generated_at
      : "Source Analytics en lecture seule.";
    elements.headerFreshness.textContent = health.generated_at
      ? "Actualisation : " + health.generated_at
      : "Actualisation : en attente";
    elements.headerSourceStatus.textContent = "Source : " + statusLabel;
    elements.headerScope.textContent = "Périmètre : " + humanCompletionScope(readFormState(elements).completion_scope || "all");
    elements.headerCounts.innerHTML = [
      renderStatChip("Questionnaires", formatNumber(overview.questionnaire_count || 0)),
      renderStatChip("Terminés", formatNumber(counts.completed || 0)),
      renderStatChip("En cours", formatNumber(counts.in_progress || 0))
    ].join("");
  }

  function renderOverviewMeta(elements, overview, health) {
    var count = overview.questionnaire_count || 0;
    var lineCount = overview.analytics_line_count || 0;
    var statusLabel = String(health.analytics_status || "unknown");
    elements.overviewMeta.innerHTML = [
      renderStatChip("Questionnaires", formatNumber(count)),
      renderStatChip("Lignes analytiques", formatNumber(lineCount)),
      renderStatChip("Source", statusLabel)
    ].join("");
  }

  function renderNetworkOverview(elements, networkOverview) {
    var model = buildNetworkOverviewModel({ dashboard: { network_overview: networkOverview } });
    if ((networkOverview || {}).status === "error") {
      elements.networkOverviewStatus.textContent = networkOverview.message || "Comparatif des dispositifs indisponible pour le moment.";
      elements.networkOverviewStatus.className = "status-banner is-error";
      elements.networkOverviewGrid.innerHTML = renderPlaceholderCard("Le réseau en un regard", networkOverview.message || "Comparatif des dispositifs indisponible pour le moment.");
      return;
    }
    elements.networkOverviewStatus.textContent = model.message || "Comparatif dynamique chargé.";
    elements.networkOverviewStatus.className = "status-banner is-success";
    if (!model.devices.length) {
      elements.networkOverviewGrid.innerHTML = renderPlaceholderCard(
        "Le réseau en un regard",
        model.message || "Aucun dispositif comparable dans le périmètre courant."
      );
      return;
    }
    elements.networkOverviewGrid.innerHTML = model.devices.map(function (device) {
      return renderNetworkDeviceCard(device);
    }).join("");
  }

  function renderActivity(elements, activity, overview) {
    var cards = Array.isArray(activity.cards) ? activity.cards : [];
    var details = Array.isArray(activity.details) ? activity.details : [];
    if ((activity || {}).status === "error") {
      elements.activityGrid.innerHTML = renderPlaceholderCard("Activité", activity.message || "Activité indisponible pour le moment.");
      elements.activityPreliminaryHighlights.innerHTML = "";
      elements.activityEtpGrid.innerHTML = "";
      elements.activityEtpDetails.innerHTML = "";
      elements.activityEtpMetiers.innerHTML = "";
      elements.activityDetails.innerHTML = "";
      elements.statusComparisonTableBody.innerHTML = "";
      return;
    }

    var primaryIds = {
      "people.received.esrp": true,
      "people.received.espo": true,
      "people.received.ueros": true,
      "people.received.pec": true,
      "people.received.other_eval": true
    };
    var activityPrimaryCards = cards.filter(function (item) {
      return !!primaryIds[item.id];
    });
    elements.activityGrid.innerHTML = activityPrimaryCards.map(function (item) {
      return renderMetricCard(normalizeMetric(item, item.label || ""), { compact: false });
    }).join("");

    var indicators = (overview || {}).indicators || {};
    var preliminaryCards = [
      indicators.preliminary_evaluations ? renderDetailCard({
        label: indicators.preliminary_evaluations.label,
        value: indicators.preliminary_evaluations.value,
        unit: indicators.preliminary_evaluations.unit,
        definition: "PEC + autres dispositifs d’évaluation.",
        children: indicators.preliminary_evaluations.children || []
      }) : "",
      indicators.other_eval_professional ? renderMetricCard(normalizeMetric(indicators.other_eval_professional, indicators.other_eval_professional.label || "Évaluations professionnelles"), { compact: true }) : "",
      indicators.other_eval_without_orp ? renderMetricCard(normalizeMetric(indicators.other_eval_without_orp, indicators.other_eval_without_orp.label || "Sans ORP CDAPH"), { compact: true }) : "",
      indicators.other_eval_with_orp ? renderMetricCard(normalizeMetric(indicators.other_eval_with_orp, indicators.other_eval_with_orp.label || "Avec ORP CDAPH"), { compact: true }) : ""
    ].filter(Boolean);
    elements.activityPreliminaryHighlights.innerHTML = preliminaryCards.join("");

    var etpAnalysis = activity.etp_analysis || {};
    var etpCards = Array.isArray(etpAnalysis.cards) ? etpAnalysis.cards : [];
    elements.activityEtpGrid.innerHTML = etpCards.map(function (item) {
      return renderMetricCard(normalizeMetric(item, item.label || ""), { compact: false });
    }).join("");

    var etpDetails = Array.isArray(etpAnalysis.details) ? etpAnalysis.details : [];
    elements.activityEtpDetails.innerHTML = etpDetails.map(function (item) {
      return renderDetailCard(item);
    }).join("");

    var etpMetiers = Array.isArray(etpAnalysis.top_metiers) ? etpAnalysis.top_metiers : [];
    elements.activityEtpMetiers.innerHTML = etpMetiers.length
      ? etpMetiers.map(function (item) {
          return renderDetailCard(item);
        }).join("")
      : renderPlaceholderCard("Répartition métiers", "Aucune répartition métiers exploitable dans le périmètre courant.");

    var esrpCards = cards.filter(function (item) {
      return item.id === "activity.esrp.certifying" || item.id === "activity.esrp.sociopro";
    }).map(function (item) {
      return renderMetricCard(normalizeMetric(item, item.label || ""), { compact: false });
    });
    elements.activityDetails.innerHTML = esrpCards.concat(details.map(function (item) {
      return renderDetailCard(item);
    })).join("");

    var rows = (activity.status_comparison && activity.status_comparison.rows) || [];
    elements.statusComparisonTableBody.innerHTML = rows.map(function (row) {
      return (
        "<tr>" +
          "<th scope=\"row\">" + escapeHtml(row.label) + "</th>" +
          "<td>" + escapeHtml(formatNumber(row.all)) + "</td>" +
          "<td>" + escapeHtml(formatNumber(row.completed)) + "</td>" +
          "<td>" + escapeHtml(formatNumber(row.in_progress)) + "</td>" +
          "<td>" + escapeHtml(formatPercent(row.in_progress_share)) + "</td>" +
        "</tr>"
      );
    }).join("");
  }

  function renderModalites(elements, modalites) {
    if ((modalites || {}).status === "error") {
      elements.modalitesGrid.innerHTML = renderPlaceholderCard("Modalités d’accompagnement", modalites.message || "Modalités indisponibles pour le moment.");
      return;
    }
    var items = Array.isArray(modalites.items) ? modalites.items : [];
    elements.modalitesGrid.innerHTML = items.map(function (item) {
      return renderDetailCard(item);
    }).join("");
  }

  function renderInsertion(elements, insertion) {
    if ((insertion || {}).status === "error") {
      elements.insertionGrid.innerHTML = renderPlaceholderCard("Insertion professionnelle", insertion.message || "Insertion professionnelle indisponible pour le moment.");
      return;
    }
    var items = Array.isArray(insertion.items) ? insertion.items : [];
    elements.insertionGrid.innerHTML = items.map(function (item) {
      return renderDetailCard(item);
    }).join("");
  }

  function renderParticipation(elements, participation) {
    if ((participation || {}).status === "error") {
      elements.participationGrid.innerHTML = renderPlaceholderCard("Participation institutionnelle", participation.message || "Participation institutionnelle indisponible pour le moment.");
      return;
    }
    var items = Array.isArray(participation.items) ? participation.items : [];
    elements.participationGrid.innerHTML = items.map(function (item) {
      return item.value === undefined
        ? renderPlaceholderCard(item.label, item.message || "Source à cartographier")
        : renderMetricCard(normalizeMetric(item, item.label || ""), { compact: false });
    }).join("");
  }

  function renderGeography(elements, geography, currentFilters) {
    if ((geography || {}).status === "error") {
      elements.regionsTableBody.innerHTML = "";
      elements.departmentsTableBody.innerHTML = "";
      elements.unknownDepartments.hidden = false;
      elements.unknownDepartments.innerHTML = renderPlaceholderCard("Territoires", geography.message || "Territoires indisponibles pour le moment.");
      return;
    }
    populateRegionOptions(elements, geography.regions || [], currentFilters.region_code || "");
    populateDepartmentOptions(elements, geography.departments || [], currentFilters.department_code || "", currentFilters.region_code || "");

    elements.regionsTableBody.innerHTML = (geography.regions || []).map(function (row) {
      return (
        "<tr>" +
          "<th scope=\"row\"><button class=\"link-button\" data-region=\"" + escapeHtml(row.region_code) + "\">" + escapeHtml(row.label) + "</button></th>" +
          "<td>" + escapeHtml(row.region_code || "") + "</td>" +
          "<td>" + escapeHtml(formatNumber(row.questionnaire_count || 0)) + "</td>" +
          "<td>" + escapeHtml(formatNumber(row.total || 0)) + "</td>" +
        "</tr>"
      );
    }).join("");

    elements.departmentsTableBody.innerHTML = (geography.departments || []).map(function (row) {
      return (
        "<tr>" +
          "<th scope=\"row\"><button class=\"link-button\" data-department=\"" + escapeHtml(row.department_code) + "\">" + escapeHtml(row.department_code || "") + "</button></th>" +
          "<td>" + escapeHtml(row.region_code || "") + "</td>" +
          "<td>" + escapeHtml(formatNumber(row.questionnaire_count || 0)) + "</td>" +
          "<td>" + escapeHtml(formatNumber(row.total || 0)) + "</td>" +
        "</tr>"
      );
    }).join("");

    var unknown = Array.isArray(geography.unknown_departments) ? geography.unknown_departments : [];
    if (unknown.length) {
      elements.unknownDepartments.hidden = false;
      elements.unknownDepartments.innerHTML = (
        "<article class=\"analytics-detail-card\">" +
          "<h3>Territoires non résolus</h3><ul class=\"analytics-list\">" +
          unknown.map(function (item) {
            return "<li>" + escapeHtml(item.value) + " : " + escapeHtml(formatNumber(item.questionnaire_count)) + " questionnaire(s)</li>";
          }).join("") +
          "</ul>" +
        "</article>"
      );
    } else {
      elements.unknownDepartments.hidden = true;
      elements.unknownDepartments.innerHTML = "";
    }
  }

  function renderEstablishments(elements, establishments) {
    if ((establishments || {}).status === "error") {
      elements.establishmentsTableBody.innerHTML = "";
      elements.establishmentsNote.hidden = false;
      elements.establishmentsNote.textContent = establishments.message || "Établissements et services indisponibles pour le moment.";
      return;
    }
    var rows = Array.isArray(establishments.items) ? establishments.items : [];
    elements.establishmentsTableBody.innerHTML = rows.map(function (row) {
      return (
        "<tr>" +
          "<th scope=\"row\">" + escapeHtml(row.finess_main || "") + "</th>" +
          "<td>" + escapeHtml((row.dispositifs || []).join(", ")) + "</td>" +
          "<td>" + escapeHtml(row.department_code || "") + "</td>" +
          "<td>" + escapeHtml(row.region_label || row.region_code || "") + "</td>" +
          "<td>" + escapeHtml((row.statuses || []).join(", ")) + "</td>" +
          "<td>" + escapeHtml(formatNumber(row.questionnaire_count || 0)) + "</td>" +
          "<td>" + escapeHtml(formatNumber((row.totals || {}).total || 0)) + "</td>" +
          "<td>" + escapeHtml(formatNumber((row.totals || {}).esrp || 0)) + "</td>" +
          "<td>" + escapeHtml(formatNumber((row.totals || {}).espo || 0)) + "</td>" +
          "<td>" + escapeHtml(formatNumber((row.totals || {}).ueros || 0)) + "</td>" +
          "<td>" + escapeHtml(formatNumber((row.totals || {}).pec || 0)) + "</td>" +
          "<td>" + escapeHtml(formatNumber((row.totals || {}).other_eval || 0)) + "</td>" +
        "</tr>"
      );
    }).join("");
    if (establishments.truncated) {
      elements.establishmentsNote.hidden = false;
      elements.establishmentsNote.textContent = "Affichage limité aux 50 premiers établissements et services triés par total.";
    } else {
      elements.establishmentsNote.hidden = true;
      elements.establishmentsNote.textContent = "";
    }
  }

  function renderInternal(elements, internal) {
    if ((internal || {}).status === "error") {
      elements.duiSummary.innerHTML = "<p>Informations internes indisponibles pour le moment.</p>";
      elements.duiTools.innerHTML = "";
      elements.remunerationSummary.innerHTML = "<li>" + escapeHtml(internal.message || "Informations internes indisponibles pour le moment.") + "</li>";
      return;
    }
    var dui = internal.dui || {};
    elements.duiSummary.innerHTML = [
      renderSimpleStat("Utilisent un DUI", dui.yes || 0),
      renderSimpleStat("N’utilisent pas de DUI", dui.no || 0),
      renderSimpleStat("Inconnus", dui.unknown || 0)
    ].join("");
    elements.duiTools.innerHTML = (dui.tools || []).length
      ? dui.tools.map(function (item) {
          return "<li>" + escapeHtml(item.label) + " : " + escapeHtml(formatNumber(item.count)) + "</li>";
        }).join("")
      : "<li>Aucun DUI exploitable dans le périmètre courant.</li>";

    var remuneration = internal.remuneration || {};
    elements.remunerationSummary.innerHTML = [
      "<li>Docaposte : " + escapeHtml(formatNumber(remuneration.docaposte || 0)) + "</li>",
      "<li>ASP : " + escapeHtml(formatNumber(remuneration.asp || 0)) + "</li>",
      "<li>Docaposte et ASP : " + escapeHtml(formatNumber(remuneration.docaposte_and_asp || 0)) + "</li>",
      "<li>Autre : " + escapeHtml(formatNumber(remuneration.other || 0)) + "</li>",
      "<li>Ni l’un ni l’autre : " + escapeHtml(formatNumber(remuneration.none || 0)) + "</li>",
      "<li>Inconnu : " + escapeHtml(formatNumber(remuneration.unknown || 0)) + "</li>"
    ].join("");
  }

  function renderQuality(elements, quality) {
    if ((quality || {}).status === "error") {
      elements.qualityLevel.textContent = "Indisponible";
      elements.qualityLevel.className = "quality-level quality-level-information";
      elements.qualityStatus.textContent = quality.message || "Qualité des données indisponible pour le moment.";
      elements.qualityInvalidFiness.textContent = "--";
      elements.qualityUnknownDepartments.textContent = "--";
      elements.qualityUnresolvedRegions.textContent = "--";
      elements.qualityNormalizedFiness.textContent = "--";
      elements.qualityMessages.innerHTML = "<li>" + escapeHtml(quality.message || "Qualité des données indisponible pour le moment.") + "</li>";
      return;
    }
    var summary = quality.summary || {};
    elements.qualityLevel.textContent = summary.global_level || "Information";
    elements.qualityLevel.className = "quality-level quality-level-" + ((summary.global_level || "neutral").toLowerCase());
    elements.qualityStatus.textContent = "Aucune modification de la source Grist n’est réalisée par ce tableau de bord.";
    elements.qualityInvalidFiness.textContent = formatNumber(summary.invalid_finess_count || 0);
    elements.qualityUnknownDepartments.textContent = formatNumber(summary.unknown_department_count || 0);
    elements.qualityUnresolvedRegions.textContent = formatNumber(summary.unresolved_region_count || 0);
    elements.qualityNormalizedFiness.textContent = formatNumber(summary.normalized_finess_count || 0);
    elements.qualityMessages.innerHTML = (quality.messages || []).map(function (message) {
      return "<li>" + escapeHtml(message) + "</li>";
    }).join("");
  }

  function renderActiveFilters(elements, filtersPayload) {
    var applied = filtersPayload.applied || {};
    var labels = [];
    labels.push("Périmètre : " + humanCompletionScope(applied.completion_scope || "all"));
    if (applied.region_code) {
      labels.push("Région : " + applied.region_code);
    }
    if (applied.department_code) {
      labels.push("Département : " + applied.department_code);
    }
    if (applied.finess_main) {
      labels.push("FINESS : " + applied.finess_main);
    }
    if (applied.dispositifs) {
      labels.push("Dispositif : " + humanDispositif(applied.dispositifs));
    }
    elements.activeFilters.innerHTML = labels.map(function (label) {
      return "<span class=\"analytics-chip\">" + escapeHtml(label) + "</span>";
    }).join("");
  }

  function populateRegionOptions(elements, regions, selectedValue) {
    var current = selectedValue || "";
    elements.regionSelect.innerHTML = "<option value=\"\">Toutes les régions</option>" + regions.map(function (item) {
      return "<option value=\"" + escapeHtml(item.region_code) + "\"" + (item.region_code === current ? " selected" : "") + ">" + escapeHtml(item.label + " (" + item.region_code + ")") + "</option>";
    }).join("");
  }

  function populateDepartmentOptions(elements, departments, selectedValue, regionCode) {
    var current = selectedValue || "";
    var filtered = departments.filter(function (item) {
      return !regionCode || item.region_code === regionCode;
    });
    elements.departmentSelect.innerHTML = "<option value=\"\">Tous les départements</option>" + filtered.map(function (item) {
      return "<option value=\"" + escapeHtml(item.department_code) + "\"" + (item.department_code === current ? " selected" : "") + ">" + escapeHtml(item.department_code) + "</option>";
    }).join("");
  }

  function renderMetricCard(item, options) {
    var classes = ["analytics-kpi-card"];
    if (options && options.compact) {
      classes.push("is-compact");
    }
    if (options && options.primary) {
      classes.push("is-primary");
    }
    return (
      "<article class=\"" + classes.join(" ") + "\">" +
        "<h3>" + escapeHtml(item.label) + "</h3>" +
        "<p class=\"analytics-kpi-card-value\">" + escapeHtml(item.value === null ? "Donnée non disponible" : formatNumber(item.value)) + "</p>" +
        "<p class=\"analytics-section-help\">" + escapeHtml(item.unit || "") + "</p>" +
        (item.definition ? "<p class=\"analytics-section-help\">" + escapeHtml(item.definition) + "</p>" : "") +
      "</article>"
    );
  }

  function renderDetailMetric(item, title) {
    return (
      "<article class=\"analytics-detail-card\">" +
        "<h3>" + escapeHtml(title || item.label || "") + "</h3>" +
        "<p class=\"analytics-inline-value\">" + escapeHtml(item.value === null ? "Donnée non disponible" : formatNumber(item.value)) + "</p>" +
        "<ul class=\"analytics-list\">" + (item.children || []).map(function (child) {
          return "<li>" + escapeHtml(child.label) + " : " + escapeHtml(formatNumber(child.value)) + "</li>";
        }).join("") + "</ul>" +
      "</article>"
    );
  }

  function renderDeacCard(deac) {
    var value = typeof (deac && deac.value) === "number"
      ? formatNumber(deac.value)
      : "Donnée non disponible";
    return (
      "<article class=\"analytics-detail-card\">" +
        "<h3>DEAc</h3>" +
        "<p class=\"analytics-inline-value\">" + escapeHtml(value) + "</p>" +
        (deac && deac.unit ? "<p class=\"analytics-section-help\">" + escapeHtml(deac.unit) + "</p>" : "") +
        "<p class=\"analytics-section-help\">" + escapeHtml((deac && deac.message) || "DEAc est affiché séparément du total général.") + "</p>" +
      "</article>"
    );
  }

  function renderNetworkDeviceCard(device) {
    return (
      "<article class=\"analytics-network-card" + (device && device.focused ? " is-focused" : "") + "\" data-device=\"" + escapeHtml((device && device.id) || "") + "\">" +
        "<header class=\"analytics-network-header\">" +
          "<p class=\"analytics-kicker\">" + escapeHtml((device && device.label) || "") + "</p>" +
          "<h3>" + escapeHtml((device && device.subtitle) || "") + "</h3>" +
        "</header>" +
        renderNetworkThemeBlock("Public", device && device.public) +
        renderNetworkThemeBlock("Dispositifs", device && device.dispositifs) +
        renderNetworkThemeBlock("Objectifs", device && device.objectives) +
        renderNetworkResultsBlock(device && device.results) +
      "</article>"
    );
  }

  function renderNetworkThemeBlock(title, section) {
    var text = section && section.text ? "<p class=\"analytics-section-help\">" + escapeHtml(section.text) + "</p>" : "";
    var metrics = Array.isArray(section && section.metrics) ? section.metrics : [];
    var items = Array.isArray(section && section.items) ? section.items : [];
    return (
      "<section class=\"analytics-network-theme\">" +
        "<h4>" + escapeHtml(title) + "</h4>" +
        text +
        (metrics.length ? "<ul class=\"analytics-network-metrics\">" + metrics.map(renderNetworkMetricItem).join("") + "</ul>" : "") +
        (items.length ? "<ul class=\"analytics-list\">" + items.map(function (item) {
          return "<li>" + escapeHtml(item) + "</li>";
        }).join("") + "</ul>" : "") +
      "</section>"
    );
  }

  function renderNetworkResultsBlock(section) {
    var items = Array.isArray(section && section.items) ? section.items : [];
    return (
      "<section class=\"analytics-network-theme\">" +
        "<h4>Résultats</h4>" +
        "<div class=\"analytics-network-results\">" + items.map(function (item) {
          return renderDetailCard(item);
        }).join("") + "</div>" +
      "</section>"
    );
  }

  function renderNetworkMetricItem(item) {
    var value = item && item.display_value
      ? item.display_value
      : (typeof (item && item.value) === "number" ? formatNumber(item.value) : placeholderValueForMessage(item && item.message));
    return (
      "<li class=\"analytics-network-metric\">" +
        "<span class=\"analytics-network-metric-label\">" + escapeHtml((item && item.label) || "") + "</span>" +
        "<strong class=\"analytics-network-metric-value\">" + escapeHtml(value) + "</strong>" +
        ((item && item.unit) ? "<span class=\"analytics-network-metric-unit\">" + escapeHtml(item.unit) + "</span>" : "") +
        ((item && item.message) ? "<span class=\"analytics-network-metric-help\">" + escapeHtml(item.message) + "</span>" : "") +
      "</li>"
    );
  }

  function renderDetailCard(item) {
    if (item.value === undefined && (!item.children || !item.children.length)) {
      return renderPlaceholderCard(item.label, item.message || "Donnée non disponible", item.source_hint || "");
    }
    return (
      "<article class=\"analytics-detail-card\">" +
        "<h3>" + escapeHtml(item.label || "") + "</h3>" +
        (item.value !== undefined ? "<p class=\"analytics-inline-value\">" + escapeHtml(item.value === null ? "Donnée non disponible" : formatNumber(item.value)) + "</p>" : "") +
        (item.unit ? "<p class=\"analytics-section-help\">" + escapeHtml(item.unit) + "</p>" : "") +
        (item.definition ? "<p class=\"analytics-section-help\">" + escapeHtml(item.definition) + "</p>" : "") +
        ((item.children || []).length ? "<ul class=\"analytics-list\">" + item.children.map(function (child) {
          return "<li>" + escapeHtml(child.label) + " : " + escapeHtml(formatNumber(child.value)) + (child.unit ? " " + escapeHtml(child.unit) : "") + "</li>";
        }).join("") + "</ul>" : "") +
      "</article>"
    );
  }

  function renderPlaceholderCard(label, message, helper) {
    var placeholderValue = placeholderValueForMessage(message);
    return (
      "<article class=\"analytics-detail-card\">" +
        "<h3>" + escapeHtml(label) + "</h3>" +
        "<p class=\"analytics-inline-value\">" + escapeHtml(placeholderValue) + "</p>" +
        "<p class=\"analytics-section-help\">" + escapeHtml(message || "Donnée non disponible") + "</p>" +
        (helper ? "<p class=\"analytics-section-help\">" + escapeHtml(helper) + "</p>" : "") +
      "</article>"
    );
  }

  function syncCapabilityDrivenFilters(elements, health) {
    var unavailable = Array.isArray(health && health.unavailable_capabilities)
      ? health.unavailable_capabilities
      : [];
    var campaignUnavailable = unavailable.indexOf("campaign") !== -1;
    if (!elements.campaignField || !elements.campaignInput) {
      return;
    }
    if (campaignUnavailable) {
      elements.campaignInput.value = "";
      elements.campaignInput.disabled = true;
      elements.campaignInput.setAttribute("aria-disabled", "true");
      elements.campaignField.hidden = true;
      toggleClass(elements.campaignField, "is-disabled", true);
      return;
    }
    elements.campaignInput.disabled = false;
    elements.campaignInput.removeAttribute("aria-disabled");
    elements.campaignField.hidden = false;
    toggleClass(elements.campaignField, "is-disabled", false);
  }

  async function fetchJson(url, options) {
    var response = await global.fetch(url, Object.assign({ credentials: "same-origin" }, options || {}));
    var payload = await response.json();
    if (!response.ok) {
      throw createApiError(payload);
    }
    return payload;
  }

  function createApiError(payload) {
    var error = new Error((((payload || {}).error) || {}).message || "API request failed");
    error.isApiError = true;
    error.payload = payload;
    return error;
  }

  function renderFatalError(elements, error) {
    elements.overviewStatus.textContent = error && error.message ? String(error.message) : "Le tableau de bord n’a pas pu être chargé.";
    elements.overviewStatus.className = "status-banner is-error";
    elements.totalValue.textContent = "Donnée non disponible";
    elements.totalUnit.textContent = "";
    elements.breakdown.innerHTML = renderPlaceholderCard("Vue d’ensemble", "Les statistiques FAGERH ne sont pas disponibles actuellement.");
    elements.networkOverviewStatus.textContent = "Le comparatif des dispositifs n’a pas pu être chargé.";
    elements.networkOverviewStatus.className = "status-banner is-error";
    elements.networkOverviewGrid.innerHTML = renderPlaceholderCard("Le réseau en un regard", "Les statistiques FAGERH ne sont pas disponibles actuellement.");
    if (global.console && typeof global.console.error === "function") {
      global.console.error("FAGERH dashboard failed", sanitizeError(error));
    }
  }

  function setGlobalStatus(elements, message, variant) {
    elements.overviewStatus.textContent = message;
    elements.overviewStatus.className = "status-banner is-" + variant;
  }

  function clearError(elements) {
    elements.overviewStatus.className = "status-banner";
  }

  function readFormState(elements) {
    return {
      completion_scope: elements.completionScope.value,
      region_code: elements.regionSelect.value,
      department_code: elements.departmentSelect.value,
      finess_main: elements.finessInput.value,
      dispositifs: elements.dispositifSelect.value
    };
  }

  function activateTab(elements, tabId, options) {
    var targetId = resolveTabId("#" + String(tabId || DEFAULT_TAB_ID).replace(/^#/, ""));
    elements.tabs.forEach(function (tab, index) {
      var isActive = tab.getAttribute("aria-controls") === targetId;
      tab.setAttribute("aria-selected", isActive ? "true" : "false");
      tab.tabIndex = isActive ? 0 : -1;
      if (isActive && options && options.focusTab) {
        tab.focus();
      }
    });
    elements.panels.forEach(function (panel) {
      panel.hidden = panel.id !== targetId;
    });
    if (!(options && options.skipHash) && global.history && typeof global.history.pushState === "function") {
      var method = options && options.replaceHash ? "replaceState" : "pushState";
      global.history[method](null, "", "#" + targetId);
    }
  }

  function handleTabKeydown(elements, event) {
    var currentIndex = elements.tabs.indexOf(event.currentTarget);
    if (currentIndex === -1) {
      return;
    }
    var nextIndex = currentIndex;
    if (event.key === "ArrowRight") {
      nextIndex = (currentIndex + 1) % elements.tabs.length;
    } else if (event.key === "ArrowLeft") {
      nextIndex = (currentIndex - 1 + elements.tabs.length) % elements.tabs.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = elements.tabs.length - 1;
    } else {
      return;
    }
    event.preventDefault();
    activateTab(elements, elements.tabs[nextIndex].getAttribute("aria-controls"), { focusTab: true });
  }

  function toggleFiltersPanel(elements, forceOpen) {
    var shouldOpen = typeof forceOpen === "boolean"
      ? forceOpen
      : !elements.filtersCard.classList.contains("is-open");
    toggleClass(elements.filtersCard, "is-open", shouldOpen);
    elements.filtersToggle.setAttribute("aria-expanded", shouldOpen ? "true" : "false");
  }

  function renderSimpleStat(label, value) {
    return "<p><strong>" + escapeHtml(label) + " :</strong> " + escapeHtml(formatNumber(value)) + "</p>";
  }

  function wireOverviewPage() {
    if (!global.document || !global.document.getElementById("filters-form")) {
      return;
    }
    var elements = getElements();
    elements.form.addEventListener("submit", function (event) {
      event.preventDefault();
      loadDashboard();
    });
    elements.refreshButton.addEventListener("click", function () {
      loadDashboard();
    });
    elements.resetButton.addEventListener("click", function () {
      elements.form.reset();
      elements.completionScope.value = "all";
      loadDashboard();
    });
    elements.filtersToggle.addEventListener("click", function () {
      toggleFiltersPanel(elements);
    });
    elements.regionSelect.addEventListener("change", function () {
      if (!elements.regionSelect.value) {
        elements.departmentSelect.value = "";
      }
    });
    elements.regionsTable.addEventListener("click", function (event) {
      var button = event.target.closest("[data-region]");
      if (!button) {
        return;
      }
      elements.regionSelect.value = button.getAttribute("data-region") || "";
      elements.departmentSelect.value = "";
      activateTab(elements, "section-network-overview", { replaceHash: true });
      loadDashboard();
    });
    elements.departmentsTable.addEventListener("click", function (event) {
      var button = event.target.closest("[data-department]");
      if (!button) {
        return;
      }
      elements.departmentSelect.value = button.getAttribute("data-department") || "";
      activateTab(elements, "section-network-overview", { replaceHash: true });
      loadDashboard();
    });
    elements.tabs.forEach(function (tab) {
      tab.addEventListener("click", function () {
        activateTab(elements, tab.getAttribute("aria-controls"));
      });
      tab.addEventListener("keydown", function (event) {
        handleTabKeydown(elements, event);
      });
    });
    global.addEventListener("hashchange", function () {
      activateTab(elements, resolveTabId(global.location.hash), { skipHash: true });
    });
    activateTab(elements, resolveTabId(global.location.hash), { skipHash: true });
    if (global.matchMedia && global.matchMedia("(max-width: 768px)").matches) {
      toggleFiltersPanel(elements, false);
    }
    loadDashboard();
  }

  function getElements() {
    var tabs = Array.prototype.slice.call(global.document.querySelectorAll("[role='tab']"));
    return {
      form: global.document.getElementById("filters-form"),
      refreshButton: global.document.getElementById("refresh-btn"),
      resetButton: global.document.getElementById("reset-btn"),
      filtersCard: global.document.querySelector(".analytics-filters-card"),
      filtersToggle: global.document.getElementById("filters-toggle"),
      campaignField: global.document.getElementById("campaign-field"),
      campaignInput: global.document.getElementById("campaign-year"),
      completionScope: global.document.getElementById("completion-scope"),
      regionSelect: global.document.getElementById("region-code"),
      departmentSelect: global.document.getElementById("department-code"),
      finessInput: global.document.getElementById("finess-main"),
      dispositifSelect: global.document.getElementById("dispositif-filter"),
      activeFilters: global.document.getElementById("active-filters"),
      dataStatus: global.document.getElementById("data-status"),
      headerScope: global.document.getElementById("header-scope"),
      headerFreshness: global.document.getElementById("header-freshness"),
      headerSourceStatus: global.document.getElementById("header-source-status"),
      headerCounts: global.document.getElementById("header-counts"),
      tabs: tabs,
      panels: Array.prototype.slice.call(global.document.querySelectorAll("[role='tabpanel']")),
      overviewMeta: global.document.getElementById("overview-meta"),
      overviewStatus: global.document.getElementById("overview-status"),
      networkOverviewStatus: global.document.getElementById("network-overview-status"),
      networkOverviewGrid: global.document.getElementById("network-overview-grid"),
      notice: global.document.getElementById("overview-notice"),
      totalValue: global.document.getElementById("total-value"),
      totalUnit: global.document.getElementById("total-unit"),
      formula: global.document.getElementById("overview-formula"),
      breakdown: global.document.getElementById("breakdown-grid"),
      preliminaryCard: global.document.getElementById("preliminary-card"),
      otherEvalCard: global.document.getElementById("other-eval-card"),
      deacCard: global.document.getElementById("deac-card"),
      activityGrid: global.document.getElementById("activity-grid"),
      activityPreliminaryHighlights: global.document.getElementById("activity-preliminary-highlights"),
      activityEtpGrid: global.document.getElementById("activity-etp-grid"),
      activityEtpDetails: global.document.getElementById("activity-etp-details"),
      activityEtpMetiers: global.document.getElementById("activity-etp-metiers"),
      activityDetails: global.document.getElementById("activity-details"),
      statusComparisonTableBody: global.document.querySelector("#status-comparison-table tbody"),
      modalitesGrid: global.document.getElementById("modalites-grid"),
      insertionGrid: global.document.getElementById("insertion-grid"),
      participationGrid: global.document.getElementById("participation-grid"),
      regionsTable: global.document.getElementById("regions-table"),
      regionsTableBody: global.document.querySelector("#regions-table tbody"),
      departmentsTable: global.document.getElementById("departments-table"),
      departmentsTableBody: global.document.querySelector("#departments-table tbody"),
      unknownDepartments: global.document.getElementById("unknown-departments"),
      establishmentsNote: global.document.getElementById("establishments-note"),
      establishmentsTableBody: global.document.querySelector("#establishments-table tbody"),
      duiSummary: global.document.getElementById("dui-summary"),
      duiTools: global.document.getElementById("dui-tools"),
      remunerationSummary: global.document.getElementById("remuneration-summary"),
      qualityLevel: global.document.getElementById("quality-level"),
      qualityStatus: global.document.getElementById("quality-status"),
      qualityInvalidFiness: global.document.getElementById("quality-invalid-finess"),
      qualityUnknownDepartments: global.document.getElementById("quality-unknown-departments"),
      qualityUnresolvedRegions: global.document.getElementById("quality-unresolved-regions"),
      qualityNormalizedFiness: global.document.getElementById("quality-normalized-finess"),
      qualityMessages: global.document.getElementById("quality-messages")
    };
  }

  function normalizeMetric(item, fallbackLabel) {
    return {
      id: item && item.id ? item.id : "",
      label: item && item.label ? item.label : fallbackLabel,
      definition: item && item.definition ? item.definition : "",
      unit: item && item.unit ? item.unit : "",
      value: typeof (item && item.value) === "number" ? item.value : null,
      children: item && item.children ? item.children : []
    };
  }

  function readValue(item) {
    return typeof (item && item.value) === "number" ? item.value : null;
  }

  function readLabel(item, fallback) {
    return item && item.label ? item.label : fallback;
  }

  function readUnit(item, fallback) {
    return item && item.unit ? item.unit : fallback;
  }

  function renderStatChip(label, value) {
    return "<span class=\"analytics-meta-pill\"><strong>" + escapeHtml(label) + " :</strong> " + escapeHtml(value) + "</span>";
  }

  function humanCompletionScope(value) {
    if (value === "completed") {
      return "Questionnaires terminés";
    }
    if (value === "in_progress") {
      return "Questionnaires en cours";
    }
    return "Tous les questionnaires";
  }

  function humanDispositif(value) {
    if (value === "esrp") {
      return "ESRP";
    }
    if (value === "espo") {
      return "ESPO";
    }
    if (value === "ueros") {
      return "UEROS";
    }
    if (value === "deac") {
      return "DEAc";
    }
    return String(value || "");
  }

  function formatNumber(value) {
    return new Intl.NumberFormat("fr-FR").format(Number(value || 0));
  }

  function formatPercent(value) {
    return new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 0, maximumFractionDigits: 1 }).format(Number(value || 0)) + " %";
  }

  function sanitizeError(error) {
    return {
      message: error && error.message ? String(error.message) : "unknown"
    };
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function placeholderValueForMessage(message) {
    var normalized = String(message || "").toLowerCase();
    if (normalized.indexOf("définition métier à confirmer") !== -1) {
      return "Définition métier à confirmer";
    }
    if (normalized.indexOf("cartographier") !== -1) {
      return "Source à cartographier";
    }
    if (normalized.indexOf("non aliment") !== -1) {
      return "Non alimenté";
    }
    return "Donnée non disponible";
  }

  function toggleClass(element, className, shouldAdd) {
    if (!element) {
      return;
    }
    if (element.classList && typeof element.classList.add === "function" && typeof element.classList.remove === "function") {
      if (shouldAdd) {
        element.classList.add(className);
      } else {
        element.classList.remove(className);
      }
      return;
    }
    var classes = String(element.className || "").split(/\s+/).filter(Boolean);
    var nextClasses = classes.filter(function (item) {
      return item !== className;
    });
    if (shouldAdd) {
      nextClasses.push(className);
    }
    element.className = nextClasses.join(" ");
  }

  var exported = {
    ANALYTICS_DASHBOARD_URL: ANALYTICS_DASHBOARD_URL,
    buildDashboardFilters: buildDashboardFilters,
    buildNetworkOverviewModel: buildNetworkOverviewModel,
    buildOverviewModel: buildOverviewModel,
    renderOverviewMarkup: renderOverviewMarkup,
    resolveTabId: resolveTabId,
    syncCapabilityDrivenFilters: syncCapabilityDrivenFilters
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = exported;
  }
  global.FagerhAnalyticsOverview = exported;

  if (global.document) {
    if (global.document.readyState === "loading") {
      global.document.addEventListener("DOMContentLoaded", wireOverviewPage);
    } else {
      wireOverviewPage();
    }
  }
})(typeof window !== "undefined" ? window : globalThis);
