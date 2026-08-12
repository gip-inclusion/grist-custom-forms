(function () {
  "use strict";
  var fields = ["regional_intro","public_comment","espo_comment","ueros_comment","ueros_places","evaluation_comment","information_actions","dfa","network"];
  var state = {validated:{}, payload:null};
  var region = document.getElementById("region");
  var completion = document.getElementById("completion");
  var status = document.getElementById("status");
  var pdfButton = document.getElementById("pdf");
  var booklet = document.getElementById("booklet");
  var bookNavigation = document.getElementById("book-navigation");
  var bookPosition = document.getElementById("book-position");
  var bookPrev = document.getElementById("book-prev");
  var bookNext = document.getElementById("book-next");
  var bookPages = Array.from(document.querySelectorAll(".sheet[data-page]")).sort(function(a,b){
    return Number(a.dataset.page)-Number(b.dataset.page);
  });
  var bookMedia = window.matchMedia("(max-width: 800px)");
  var spreadIndex = 0;
  var officialRegionalDirectory = {
    "84": [
      "Centre Ressources pour Lésés Cérébraux (CRLC)",
      "COS CREPSE",
      "EPNAK - ESRP Lyon",
      "EPNAK PAOFIP Grenoble",
      "EPNAK PAOFIP Villefranche-sur-Saône",
      "ESRP CRDV - déficients visuels",
      "ESRP La Mothe",
      "ESRP ORSAC",
      "ESRP-ESPO de Saint-Amant-Tallende",
      "LADAPT Ain-Savoie",
      "LADAPT Drôme-Ardèche",
      "LADAPT Haute-Savoie - ESRP Jean Foa",
      "LADAPT Rhône-Métropole de Lyon",
      "OFIL Annecy - La Passerelle",
      "OFIL Cluses - L’Englennaz"
    ]
  };
  var officialRegionalDeviceCounts = {
    "84": {ueros:3}
  };

  function number(value) { return new Intl.NumberFormat("fr-FR",{maximumFractionDigits:1}).format(Number(value)||0); }
  function percent(value) { return new Intl.NumberFormat("fr-FR",{style:"percent",maximumFractionDigits:1}).format(Number(value)||0); }
  function esc(value) { return String(value==null?"":value).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];}); }
  async function json(url, options) {
    var response = await fetch(url, Object.assign({credentials:"same-origin"},options||{}));
    var payload = await response.json();
    if (!response.ok || payload.status === "error") throw new Error((payload.error&&payload.error.message)||"Chargement impossible.");
    return payload;
  }
  function storageKey() { return "fagerh-livret-v6-2025-" + region.value + "-" + completion.value; }
  function save() {
    var content = {};
    document.querySelectorAll(".manual-block").forEach(function(block){content[block.dataset.field]=block.querySelector(".editable").innerHTML;});
    localStorage.setItem(storageKey(),JSON.stringify({content:content,validated:state.validated}));
  }
  function restore() {
    state.validated = {};
    var saved = JSON.parse(localStorage.getItem(storageKey())||"{}");
    document.querySelectorAll(".manual-block").forEach(function(block){
      var key=block.dataset.field;
      if(saved.content&&saved.content[key]) block.querySelector(".editable").innerHTML=saved.content[key];
      state.validated[key]=Boolean(saved.validated&&saved.validated[key]);
      block.classList.toggle("validated",state.validated[key]);
      block.querySelector(".validate").textContent=state.validated[key]?"Validation retirée":"Valider ce contenu";
    });
    updateValidation();
  }
  function updateValidation() {
    var summary=document.getElementById("validation-summary");
    summary.innerHTML=fields.map(function(key){
      return '<div class="validation-row"><span>'+esc(key.replaceAll("_"," "))+'</span><strong class="'+(state.validated[key]?"ok":"pending")+'">'+(state.validated[key]?"Validé":"À valider")+"</strong></div>";
    }).join("");
    pdfButton.disabled=!fields.every(function(key){return state.validated[key];});
  }
  function indicator(overview,key) { return overview.indicators&&overview.indicators[key]?overview.indicators[key].value:0; }
  function itemById(section, id) {
    return ((section||{}).items||[]).find(function(item){return item.id===id;})||{};
  }
  function childValue(item, label) {
    var child=((item||{}).children||[]).find(function(entry){return entry.label===label;});
    return Number(child&&child.value)||0;
  }
  function renderKnownNarrative(dashboard, observatory) {
    var overview=dashboard.overview||{};
    document.getElementById("official-regional-establishments").textContent=number((officialRegionalDirectory[region.value]||[]).length);
    document.getElementById("regional-establishments").textContent=number((dashboard.establishments||{}).total_items);
    document.getElementById("regional-received-total").textContent=number(indicator(overview,"total"));
    var disability=(observatory.main_disability||{});
    var total=(disability.counts||[]).reduce(function(sum,value){return sum+(Number(value)||0);},0);
    var ranked=(disability.labels||[]).map(function(label,index){
      return {label:label,value:Number((disability.counts||[])[index])||0};
    }).filter(function(item){return item.value>0;}).sort(function(a,b){return b.value-a.value;}).slice(0,5);
    document.getElementById("disability-breakdown").innerHTML=ranked.length
      ?"Concernant la déficience principale, les catégories les plus représentées en 2025 sont : "+ranked.map(function(item){return "<strong>"+esc(item.label)+"</strong> ("+percent(total?item.value/total:0)+")";}).join(", ")+"."
      :"La ventilation 2025 des déficiences principales n’est pas disponible pour ce périmètre.";

    var insertion=dashboard.insertion||{};
    var access=itemById(insertion,"employment.access_rate");
    var contracts=itemById(insertion,"employment_contracts");
    var respondents=childValue(access,"Dénominateur");
    var cdi=childValue(contracts,"CDI");
    var longCdd=childValue(contracts,"CDD de plus de 6 mois");
    var accessRate=Number(access.value)||0;
    document.getElementById("employment-respondents").textContent=number(respondents);
    document.getElementById("employment-summary").textContent=respondents
      ?"Parmi les "+number(respondents)+" répondants au suivi emploi 2025, "+number(accessRate)+" % ont accédé à l’emploi dans les 12 mois suivant leur sortie, dont "+number(cdi)+" CDI ("+number((cdi*100)/respondents)+" %) et "+number(longCdd)+" CDD de plus de six mois ("+number((longCdd*100)/respondents)+" %)."
      :"Aucune donnée de suivi emploi 2025 exploitable n’est disponible pour ce périmètre.";

    var people=itemById(dashboard.modalites,"info_people");
    var partners=itemById(dashboard.modalites,"info_partners");
    var training=itemById(dashboard.modalites,"info_training");
    var peopleCollective=childValue(people,"Personnes reçues en collectif");
    var peopleDays=childValue(people,"Journées d’information collectives");
    var peopleHours=childValue(people,"Information individuelle");
    document.getElementById("info-people-collective").textContent=number(peopleCollective);
    document.getElementById("info-people-days").textContent=number(peopleDays);
    document.getElementById("info-people-hours").textContent=number(peopleHours);

    var trainingCollective=childValue(training,"Organismes concernés en collectif");
    var trainingIndividual=childValue(training,"Organismes concernés en individuel");
    document.getElementById("info-training-total").textContent=number(trainingCollective+trainingIndividual);
    document.getElementById("info-training-detail").textContent=
      number(trainingCollective)+" en collectif sur "+number(childValue(training,"Journées collectives"))+" journées, et "+
      number(trainingIndividual)+" en individuel sur "+number(childValue(training,"Information individuelle"))+" heures";

    var partnersCollective=childValue(partners,"Partenaires concernés en collectif");
    var partnersIndividual=childValue(partners,"Partenaires concernés en individuel");
    document.getElementById("info-partners-total").textContent=number(partnersCollective+partnersIndividual);
    document.getElementById("info-partners-detail").textContent=
      number(partnersCollective)+" en collectif sur "+number(childValue(partners,"Journées collectives"))+" journées, et "+
      number(partnersIndividual)+" en individuel sur "+number(childValue(partners,"Information individuelle"))+" heures";
  }
  function singlePageMode() { return bookMedia.matches; }
  function spreadCount() { return singlePageMode()?bookPages.length:1+Math.ceil(Math.max(0,bookPages.length-1)/2); }
  function renderSpread() {
    var visible=singlePageMode()?[spreadIndex]:(spreadIndex===0?[0]:[spreadIndex*2-1,spreadIndex*2]);
    bookPages.forEach(function(page,index){
      var shown=visible.indexOf(index)>=0;
      page.classList.toggle("is-visible",shown);
      page.setAttribute("aria-hidden",shown?"false":"true");
    });
    booklet.classList.toggle("cover-view",spreadIndex===0);
    bookPrev.disabled=spreadIndex===0;
    bookNext.disabled=spreadIndex>=spreadCount()-1;
    if(spreadIndex===0) bookPosition.textContent="Couverture";
    else if(singlePageMode()) bookPosition.textContent="Page "+(spreadIndex+1)+" sur "+bookPages.length;
    else {
      var first=visible[0]+1, last=Math.min(visible[1]+1,bookPages.length);
      bookPosition.textContent="Pages "+first+(last>first?"–"+last:"")+" sur "+bookPages.length;
    }
  }
  function turnBook(direction) {
    var target=Math.max(0,Math.min(spreadCount()-1,spreadIndex+direction));
    if(target===spreadIndex) return;
    spreadIndex=target;
    renderSpread();
  }
  function render(dashboard, observatory) {
    var overview=dashboard.overview||{}, activity=dashboard.activity||{};
    document.getElementById("cover-region").textContent="Région "+observatory.region.label;
    document.getElementById("mean-age").textContent=observatory.age.estimated_mean==null?"—":number(observatory.age.estimated_mean)+" ans";
    document.getElementById("low-level").textContent=percent(observatory.education.level_4_or_less_rate);
    var disability=(observatory.main_disability.labels||[]).map(function(label,index){return {label:label,value:observatory.main_disability.counts[index]||0};}).sort(function(a,b){return b.value-a.value;})[0];
    document.getElementById("main-disability").textContent=disability?disability.label:"—";
    document.getElementById("esrp-total").textContent=number(indicator(overview,"esrp"));
    document.getElementById("espo-total").textContent=number(indicator(overview,"espo"));
    var uerosTotal=Number(indicator(overview,"ueros"))||0;
    var rehabilitationTotal=(Number(indicator(overview,"esrp"))||0)+(Number(indicator(overview,"espo"))||0)+uerosTotal;
    document.getElementById("ueros-total").textContent=number(uerosTotal);
    var officialUerosCount=((officialRegionalDeviceCounts[region.value]||{}).ueros);
    var usesOfficialUerosCount=officialUerosCount!=null;
    document.getElementById("ueros-establishments").textContent=number(
      usesOfficialUerosCount?officialUerosCount:(observatory.declared_services||{}).ueros
    );
    document.getElementById("ueros-establishments-label").innerHTML=usesOfficialUerosCount
      ?"Établissements et services UEROS<br><small>Annuaire officiel FAGERH</small>"
      :"Établissements répondants UEROS<br><small>Données de campagne</small>";
    document.getElementById("ueros-share").textContent=rehabilitationTotal?percent(uerosTotal/rehabilitationTotal):"—";
    var pecTotal=Number(indicator(overview,"pec"))||0;
    var otherEvaluationTotal=Number(indicator(overview,"other_eval"))||0;
    var overallActivityTotal=Number(indicator(overview,"total"))||0;
    document.getElementById("pec-total").textContent=number(pecTotal);
    document.getElementById("other-eval-total").textContent=number(otherEvaluationTotal);
    document.getElementById("evaluation-share").textContent=overallActivityTotal
      ?percent((pecTotal+otherEvaluationTotal)/overallActivityTotal)
      :"—";
    document.getElementById("accommodation-total").textContent=number((observatory.accommodation||{}).people);
    var directoryItems=officialRegionalDirectory[region.value];
    document.getElementById("establishment-list").classList.toggle("official-directory",Boolean(directoryItems));
    document.getElementById("establishment-list").innerHTML=directoryItems
      ?directoryItems.map(function(name,index){return '<article><span class="establishment-number">'+(index+1)+'</span><h3>'+esc(name)+"</h3></article>";}).join("")
      :((dashboard.establishments||{}).items||[]).map(function(item){
        return "<article><h3>"+esc(item.name||("FINESS "+item.finess_main))+"</h3><p>FINESS : "+esc(item.finess_main)+" · Département "+esc(item.department_code||"—")+"</p><p>"+esc((item.dispositifs||[]).join(" · "))+"</p></article>";
      }).join("")||"<p>Aucun établissement exploitable.</p>";
    document.getElementById("esrp-activity").innerHTML=((activity.cards||[]).filter(function(card){return String(card.id||"").indexOf("esrp")>=0;}).map(function(card){
      return "<article><strong>"+esc(number(card.value))+"</strong><p>"+esc(card.label)+"</p></article>";
    }).join(""));
    document.getElementById("health-list").innerHTML=((observatory.health_support||{}).categories||[]).slice(0,7).map(function(item){
      return "<div><span>"+esc(item.label)+"</span><strong>"+esc(number(item.value))+" ETP</strong></div>";
    }).join("");
    booklet.hidden=false;
    bookNavigation.hidden=false;
    restore();
    renderKnownNarrative(dashboard,observatory);
    renderSpread();
  }
  async function load() {
    status.textContent="Calcul et préparation du livret…";
    pdfButton.disabled=true;
    try {
      var filters={completion_scope:completion.value,region_code:region.value};
      var responses=await Promise.all([
        json("/api/fagerh-analytics/v1/dashboard",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({filters:filters})}),
        json("/api/fagerh-analytics/v1/observatoire/"+encodeURIComponent(region.value)+"?completion_scope="+encodeURIComponent(completion.value))
      ]);
      state.payload=responses;
      render(responses[0].result||{},responses[1].result||{});
      status.textContent="Brouillon prêt. Relisez les zones orange avant de générer le PDF.";
    } catch(error) { status.textContent=error.message; }
  }
  document.querySelectorAll(".manual-block").forEach(function(block){
    block.querySelector(".editable").addEventListener("input",function(){state.validated[block.dataset.field]=false;block.classList.remove("validated");save();updateValidation();});
    block.querySelector(".validate").addEventListener("click",function(){state.validated[block.dataset.field]=!state.validated[block.dataset.field];block.classList.toggle("validated",state.validated[block.dataset.field]);this.textContent=state.validated[block.dataset.field]?"Validation retirée":"Valider ce contenu";save();updateValidation();});
  });
  document.getElementById("refresh").addEventListener("click",load);
  bookPrev.addEventListener("click",function(){turnBook(-1);});
  bookNext.addEventListener("click",function(){turnBook(1);});
  document.addEventListener("keydown",function(event){
    var target=event.target;
    if(target&&((target.tagName==="INPUT")||(target.tagName==="SELECT")||target.isContentEditable)) return;
    if(event.key==="ArrowLeft") turnBook(-1);
    if(event.key==="ArrowRight") turnBook(1);
  });
  var touchStartX=null;
  booklet.addEventListener("touchstart",function(event){touchStartX=event.changedTouches[0].clientX;},{passive:true});
  booklet.addEventListener("touchend",function(event){
    if(touchStartX===null) return;
    var delta=event.changedTouches[0].clientX-touchStartX;
    if(Math.abs(delta)>55) turnBook(delta<0?1:-1);
    touchStartX=null;
  },{passive:true});
  bookMedia.addEventListener("change",function(){spreadIndex=0;renderSpread();});
  pdfButton.addEventListener("click",function(){if(!this.disabled)window.print();});
  load();
}());
