"""Central indicator catalog for the phase 1 MVP."""

from __future__ import annotations

from dataclasses import replace

from .filters import FILTER_NAMES
from .domain import IndicatorDefinition
from .schema import CAPABILITIES


CANONICAL_GRAINS = {
    "questionnaire",
    "establishment_service_device",
    "evaluation_activity",
    "composite",
}

CANONICAL_VISIBILITIES = {
    "internal",
    "observatory",
    "both",
}

CATALOG_VERSION = "1"

VISIBILITY_SORT_ORDER = {
    "internal": 0,
    "both": 1,
    "observatory": 2,
}

GRAIN_SORT_ORDER = {
    "questionnaire": 0,
    "establishment_service_device": 1,
    "evaluation_activity": 2,
    "composite": 3,
}

CAPABILITY_NAMES = {capability.name for capability in CAPABILITIES}


INDICATORS: dict[str, IndicatorDefinition] = {
    "questionnaires.count": IndicatorDefinition(
        id="questionnaires.count",
        label="Questionnaires",
        definition="Nombre de questionnaires distincts saisis pour la campagne et le périmètre demandés.",
        unit="count",
        grain="questionnaire",
        dataset_id="questionnaires",
        confidence_level="confirmed by the code",
        required_capabilities=("core",),
        source_fields=("uuid",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
        visibility="internal",
        double_counting_policy="Comptage technique des UUID de questionnaires distincts.",
        business_warnings=("Indicateur technique interne.",),
    ),
    "profile.dui.yes.count": IndicatorDefinition(
        id="profile.dui.yes.count",
        label="Établissements et services utilisant un DUI",
        definition="Nombre d'établissements et services déclarant utiliser un DUI.",
        unit="count",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by the code",
        required_capabilities=("core", "devices", "dui"),
        source_fields=("q38_dui",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="internal",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif.",
        business_warnings=("Indicateur interne.",),
    ),
    "profile.dui.no.count": IndicatorDefinition(
        id="profile.dui.no.count",
        label="Établissements et services n'utilisant pas de DUI",
        definition="Nombre d'établissements et services déclarant ne pas utiliser de DUI.",
        unit="count",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by the code",
        required_capabilities=("core", "devices", "dui"),
        source_fields=("q38_dui",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="internal",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif.",
        business_warnings=("Indicateur interne.",),
    ),
    "profile.remuneration.docaposte.count": IndicatorDefinition(
        id="profile.remuneration.docaposte.count",
        label="Établissements et services utilisant Docaposte",
        definition="Nombre d'établissements et services déclarant Docaposte comme opérateur de rémunération.",
        unit="count",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by the code",
        required_capabilities=("core", "devices", "remuneration"),
        source_fields=("q40_remuneration", "q40_operateur"),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="internal",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif.",
        business_warnings=("Indicateur interne.",),
    ),
    "profile.remuneration.asp.count": IndicatorDefinition(
        id="profile.remuneration.asp.count",
        label="Établissements et services utilisant l'ASP",
        definition="Nombre d'établissements et services déclarant l'ASP comme opérateur de rémunération.",
        unit="count",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by the code",
        required_capabilities=("core", "devices", "remuneration"),
        source_fields=("q40_remuneration", "q40_operateur"),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="internal",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif.",
        business_warnings=("Indicateur interne.",),
    ),
    "profile.remuneration.other.count": IndicatorDefinition(
        id="profile.remuneration.other.count",
        label="Établissements et services utilisant un autre opérateur",
        definition="Nombre d'établissements et services déclarant un autre opérateur de rémunération.",
        unit="count",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by the code",
        required_capabilities=("core", "devices", "remuneration"),
        source_fields=("q40_remuneration", "q40_operateur"),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="internal",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif.",
        business_warnings=("Indicateur interne.",),
    ),
    "profile.remuneration.none.count": IndicatorDefinition(
        id="profile.remuneration.none.count",
        label="Établissements et services sans opérateur",
        definition="Nombre d'établissements et services déclarant ne pas avoir d'opérateur de rémunération.",
        unit="count",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by the code",
        required_capabilities=("core", "devices", "remuneration"),
        source_fields=("q40_remuneration", "q40_operateur"),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="internal",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif.",
        business_warnings=("Indicateur interne.",),
    ),
    "profile.remuneration.unknown.count": IndicatorDefinition(
        id="profile.remuneration.unknown.count",
        label="Établissements et services — situation non renseignée",
        definition="Nombre d'établissements et services pour lesquels la situation de rémunération ne peut pas être classée.",
        unit="count",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by the code",
        required_capabilities=("core", "devices", "remuneration"),
        source_fields=("q40_remuneration", "q40_operateur"),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="internal",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif.",
        business_warnings=("Indicateur interne.",),
    ),
    "institution.mdph.epe.count": IndicatorDefinition(
        id="institution.mdph.epe.count",
        label="Participations aux EPE de la MDPH",
        definition="Nombre total de participations déclarées aux EPE de la MDPH dans le périmètre demandé.",
        unit="participations",
        grain="questionnaire",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "mdph_activities"),
        source_fields=("prestations_json",),
        source_paths=("indirect.rows.epe.origine", "indirect.rows.epe.limitrophes"),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
        visibility="observatory",
        double_counting_policy="Les valeurs représentent des participations et peuvent inclure plusieurs participations d'une même structure.",
        business_warnings=("Les participations multiples sont conservées.",),
    ),
    "institution.mdph.cdaph.count": IndicatorDefinition(
        id="institution.mdph.cdaph.count",
        label="Participations aux CDAPH",
        definition="Nombre total de participations déclarées aux CDAPH dans le périmètre demandé.",
        unit="participations",
        grain="questionnaire",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "mdph_activities"),
        source_fields=("prestations_json",),
        source_paths=("indirect.rows.cdaph.origine", "indirect.rows.cdaph.limitrophes"),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
        visibility="observatory",
        double_counting_policy="Les valeurs représentent des participations et peuvent inclure plusieurs participations d'une même structure.",
        business_warnings=("Les participations multiples sont conservées.",),
    ),
    "institution.mdph.working_groups.count": IndicatorDefinition(
        id="institution.mdph.working_groups.count",
        label="Participations aux groupes de travail MDPH",
        definition="Nombre total de participations déclarées aux groupes de travail MDPH dans le périmètre demandé.",
        unit="participations",
        grain="questionnaire",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "mdph_activities"),
        source_fields=("prestations_json",),
        source_paths=("indirect.rows.groupes_travail.origine", "indirect.rows.groupes_travail.limitrophes"),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
        visibility="observatory",
        double_counting_policy="Les valeurs représentent des participations et peuvent inclure plusieurs participations d'une même structure.",
        business_warnings=("Les participations multiples sont conservées.",),
    ),
    "people.received.esrp": IndicatorDefinition(
        id="people.received.esrp",
        label="Volume annuel déclaré de personnes accompagnées en ESRP",
        definition="Volume annuel déclaré de personnes accompagnées en ESRP.",
        unit="personnes déclarées",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "devices", "annual_volumes_esrp"),
        source_fields=("prestations_json", "prestations_details_json", "q53_accompagnes__esrp"),
        source_paths=("prestations_json.<conditional_id>.fileActive + prestations_json.<conditional_id>.sorties",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="observatory",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif ; la valeur JSON est prioritaire et le champ plat n'est utilisé qu'en fallback contrôlé.",
        business_warnings=("Les personnes comptées ne sont pas uniques.", "La valeur JSON est prioritaire sur le champ annuel plat."),
    ),
    "people.received.espo": IndicatorDefinition(
        id="people.received.espo",
        label="Volume annuel déclaré de personnes accompagnées en ESPO",
        definition="Volume annuel déclaré de personnes accompagnées en ESPO.",
        unit="personnes déclarées",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "devices", "annual_volumes_espo"),
        source_fields=("prestations_json", "prestations_details_json", "q53_accompagnes__espo"),
        source_paths=("prestations_json.<conditional_id>.fileActive + prestations_json.<conditional_id>.sorties",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="observatory",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif ; la valeur JSON est prioritaire et le champ plat n'est utilisé qu'en fallback contrôlé.",
        business_warnings=("Les personnes comptées ne sont pas uniques.", "La valeur JSON est prioritaire sur le champ annuel plat."),
    ),
    "people.received.ueros": IndicatorDefinition(
        id="people.received.ueros",
        label="Volume annuel déclaré de personnes accompagnées en UEROS",
        definition="Volume annuel déclaré de personnes accompagnées en UEROS.",
        unit="personnes déclarées",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "devices", "annual_volumes_ueros"),
        source_fields=("prestations_json", "prestations_details_json", "q53_accompagnes__ueros"),
        source_paths=("prestations_json.<conditional_id>.fileActive + prestations_json.<conditional_id>.sorties",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="observatory",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif ; la valeur JSON est prioritaire et le champ plat n'est utilisé qu'en fallback contrôlé.",
        business_warnings=("Les personnes comptées ne sont pas uniques.", "La valeur JSON est prioritaire sur le champ annuel plat."),
    ),
    "people.received.deac": IndicatorDefinition(
        id="people.received.deac",
        label="Volume annuel déclaré de personnes accompagnées en DEAc",
        definition="Volume annuel déclaré de personnes accompagnées en DEAc.",
        unit="personnes déclarées",
        grain="establishment_service_device",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "devices", "annual_volumes_deac"),
        source_fields=("prestations_json", "prestations_details_json", "q53_accompagnes__deac"),
        source_paths=("prestations_json.<conditional_id>.fileActive + prestations_json.<conditional_id>.sorties",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main", "dispositifs"),
        visibility="observatory",
        double_counting_policy="Le comptage est réalisé par campagne + FINESS + dispositif ; les volumes sont déclaratifs et ne sont pas dédupliqués entre catégories ou dispositifs.",
        business_warnings=("Les personnes comptées ne sont pas uniques.",),
    ),
    "people.received.pec": IndicatorDefinition(
        id="people.received.pec",
        label="Volume déclaré de personnes reçues en PEC",
        definition="Volume déclaré de personnes reçues dans le cadre des prestations d'évaluation et de conseil, sans déduplication individuelle.",
        unit="personnes déclarées",
        grain="evaluation_activity",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "evaluation_activities"),
        source_fields=("prestations_json", "prestations_details_json"),
        source_paths=(
            "prestations_json.<conditional_id>.fileActive",
            "prestations_json.<conditional_id>.directSansOrp.rows.pec.beneficiaires",
        ),
        aggregation_rule=(
            "Somme des blocs PEC avec et sans ORP CDAPH, sans addition de sous-totaux internes."
        ),
        provenance="prestations_json + prestations_details_json.runtime.conditionalDefs",
        visibility="observatory",
        double_counting_policy="Les volumes sont déclaratifs et ne sont pas dédupliqués entre catégories ou blocs.",
        business_warnings=("Les personnes comptées ne sont pas uniques.",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
    ),
    "people.received.other_eval": IndicatorDefinition(
        id="people.received.other_eval",
        label="Volume déclaré de personnes reçues dans les autres dispositifs d'évaluation",
        definition="Volume déclaré de personnes reçues dans les autres dispositifs d'évaluation, sans déduplication individuelle.",
        unit="personnes déclarées",
        grain="composite",
        dataset_id="questionnaires",
        confidence_level="confirmed by indicator composition",
        component_indicators=(
            "people.received.other_eval.professional_assessment",
            "people.received.other_eval.without_orp_cdaph",
            "people.received.other_eval.with_orp_cdaph",
        ),
        aggregation_rule=(
            "professional_assessment + without_orp_cdaph + with_orp_cdaph"
        ),
        provenance="composed from canonical other-evaluation indicators sourced from prestations_json",
        visibility="observatory",
        double_counting_policy="Les volumes sont déclaratifs et ne sont pas dédupliqués entre catégories ou blocs.",
        business_warnings=("Les personnes comptées ne sont pas uniques.",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
    ),
    "people.received.other_eval.professional_assessment": IndicatorDefinition(
        id="people.received.other_eval.professional_assessment",
        label="Évaluations professionnelles",
        definition="Volume déclaré de personnes reçues dans les évaluations professionnelles hors ORP CDAPH.",
        unit="personnes déclarées",
        grain="evaluation_activity",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "evaluation_activities"),
        source_fields=("prestations_json", "prestations_details_json"),
        source_paths=("prestations_json.<conditional_id>.directSansOrp.rows.pec.beneficiaires",),
        aggregation_rule="Somme du bloc Directes hors ORP CDAPH - Évaluations professionnelles.",
        provenance="prestations_json + prestations_details_json.runtime.conditionalDefs",
        visibility="observatory",
        double_counting_policy="Les volumes sont déclaratifs et additives dans la ventilation other_eval.",
        business_warnings=("Les personnes comptées ne sont pas uniques.",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
    ),
    "people.received.other_eval.without_orp_cdaph": IndicatorDefinition(
        id="people.received.other_eval.without_orp_cdaph",
        label="Autres évaluations sans ORP CDAPH",
        definition="Volume déclaré de personnes reçues dans les autres dispositifs d'évaluation sans ORP CDAPH.",
        unit="personnes déclarées",
        grain="evaluation_activity",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "evaluation_activities"),
        source_fields=("prestations_json", "prestations_details_json"),
        source_paths=("prestations_json.<conditional_id>.fileActive",),
        aggregation_rule="Somme du bloc Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH.",
        provenance="prestations_json + prestations_details_json.runtime.conditionalDefs",
        visibility="observatory",
        double_counting_policy="Les volumes sont déclaratifs et additives dans la ventilation other_eval.",
        business_warnings=("Les personnes comptées ne sont pas uniques.",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
    ),
    "people.received.other_eval.with_orp_cdaph": IndicatorDefinition(
        id="people.received.other_eval.with_orp_cdaph",
        label="Autres évaluations avec ORP CDAPH",
        definition="Volume déclaré de personnes reçues dans les autres dispositifs d'évaluation avec ORP CDAPH.",
        unit="personnes déclarées",
        grain="evaluation_activity",
        dataset_id="questionnaires",
        confidence_level="confirmed by questionnaire inspection",
        required_capabilities=("core", "evaluation_activities"),
        source_fields=("prestations_json", "prestations_details_json"),
        source_paths=("prestations_json.<conditional_id>.fileActive",),
        aggregation_rule="Somme du bloc Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH.",
        provenance="prestations_json + prestations_details_json.runtime.conditionalDefs",
        visibility="observatory",
        double_counting_policy="Les volumes sont déclaratifs et additives dans la ventilation other_eval.",
        business_warnings=("Les personnes comptées ne sont pas uniques.",),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
    ),
    "people.received.all": IndicatorDefinition(
        id="people.received.all",
        label="Volume déclaré de personnes reçues toutes catégories confondues",
        definition="Somme des volumes déclarés de personnes reçues en ESRP, ESPO, UEROS, PEC et autres dispositifs d'évaluation.",
        unit="volumes déclarés de personnes",
        grain="composite",
        dataset_id="questionnaires",
        confidence_level="confirmed by indicator composition",
        component_indicators=(
            "people.received.esrp",
            "people.received.espo",
            "people.received.ueros",
            "people.received.pec",
            "people.received.other_eval",
        ),
        aggregation_rule=(
            "total = people.received.esrp + people.received.espo + people.received.ueros "
            "+ people.received.pec + people.received.other_eval"
        ),
        provenance=(
            "composed from canonical indicators across questionnaire-dispositif and "
            "evaluation-activity grains; DEAc excluded from total"
        ),
        visibility="observatory",
        double_counting_policy="Somme des cinq composantes ; doubles comptes inter-catégories acceptés ; DEAc exclu.",
        business_warnings=("Les personnes comptées ne sont pas uniques.", "DEAc est explicitement exclu du total."),
        compatible_filters=("campaign_year", "region_code", "department_code", "finess_main"),
    ),
}


def get_indicator_definition(indicator_id: str) -> IndicatorDefinition | None:
    """Return the indicator definition when it exists."""

    return INDICATORS.get(indicator_id)


def get_indicator_required_capabilities(indicator_id: str) -> tuple[str, ...]:
    """Return schema capabilities required by an indicator."""

    return _resolve_required_capabilities(indicator_id, trail=())


def validate_indicator_catalog(indicators: dict[str, IndicatorDefinition]) -> None:
    """Validate internal consistency of the indicator catalog."""

    seen_ids: set[str] = set()
    known_indicator_ids = set(indicators)
    for indicator_id, definition in indicators.items():
        if indicator_id in seen_ids:
            raise ValueError(f"Duplicate indicator id: {indicator_id}")
        seen_ids.add(indicator_id)
        if not definition.label.strip():
            raise ValueError(f"Indicator {indicator_id} must define a non-empty label")
        if not definition.definition.strip():
            raise ValueError(f"Indicator {indicator_id} must define a non-empty definition")
        if definition.grain not in CANONICAL_GRAINS:
            raise ValueError(f"Indicator {indicator_id} uses unknown grain {definition.grain!r}")
        if definition.visibility not in CANONICAL_VISIBILITIES:
            raise ValueError(f"Indicator {indicator_id} uses unknown visibility {definition.visibility!r}")
        for capability in definition.required_capabilities:
            if capability not in CAPABILITY_NAMES:
                raise ValueError(f"Indicator {indicator_id} references unknown capability {capability!r}")
        for filter_name in definition.compatible_filters:
            if filter_name not in FILTER_NAMES:
                raise ValueError(f"Indicator {indicator_id} references unknown filter {filter_name!r}")
        for component_id in definition.component_indicators:
            if component_id not in known_indicator_ids:
                raise ValueError(f"Indicator {indicator_id} references unknown component {component_id!r}")
        if definition.grain == "composite":
            if not definition.component_indicators:
                raise ValueError(f"Composite indicator {indicator_id} must declare component indicators")
            if definition.source_fields or definition.required_capabilities:
                raise ValueError(f"Composite indicator {indicator_id} must not declare direct raw source fields or raw capabilities")
        else:
            if not definition.source_fields and not definition.source_paths:
                raise ValueError(f"Indicator {indicator_id} must declare source fields or source paths")
    _detect_cycles(indicators)
    people_received_all = indicators["people.received.all"]
    expected_components = (
        "people.received.esrp",
        "people.received.espo",
        "people.received.ueros",
        "people.received.pec",
        "people.received.other_eval",
    )
    if people_received_all.component_indicators != expected_components:
        raise ValueError("Indicator people.received.all must declare exactly ESRP, ESPO, UEROS, PEC and other_eval")
    if "people.received.deac" in people_received_all.component_indicators:
        raise ValueError("Indicator people.received.all must not include DEAc")
    _resolve_required_capabilities("people.received.all", trail=())


def _resolve_required_capabilities(indicator_id: str, *, trail: tuple[str, ...]) -> tuple[str, ...]:
    definition = INDICATORS[indicator_id]
    if not definition.component_indicators:
        return tuple(sorted(dict.fromkeys(definition.required_capabilities)))
    capabilities: list[str] = []
    for component_id in definition.component_indicators:
        if component_id in trail:
            raise ValueError(f"Circular indicator dependency detected: {' -> '.join((*trail, component_id))}")
        capabilities.extend(_resolve_required_capabilities(component_id, trail=(*trail, indicator_id)))
    return tuple(sorted(dict.fromkeys(capabilities)))


def _detect_cycles(indicators: dict[str, IndicatorDefinition]) -> None:
    for indicator_id in indicators:
        _walk_components(indicators, indicator_id, stack=())


def _walk_components(
    indicators: dict[str, IndicatorDefinition],
    indicator_id: str,
    *,
    stack: tuple[str, ...],
) -> None:
    if indicator_id in stack:
        raise ValueError(f"Circular indicator dependency detected: {' -> '.join((*stack, indicator_id))}")
    definition = indicators[indicator_id]
    for component_id in definition.component_indicators:
        _walk_components(indicators, component_id, stack=(*stack, indicator_id))


INDICATORS = {
    indicator_id: replace(
        definition,
        compatible_filters=definition.compatible_filters
        if "completion_scope" in definition.compatible_filters
        else (*definition.compatible_filters, "completion_scope"),
    )
    for indicator_id, definition in INDICATORS.items()
}

validate_indicator_catalog(INDICATORS)
