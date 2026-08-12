"""Aggregated dashboard payloads for the FAGERH Analytics admin page."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from typing import Any

from .catalog import get_indicator_definition
from .data_quality import analyze_data_quality
from .domain import EvaluationActivityRecord, QuestionnaireRecord, RawQuestionnaireRecord, UserContext
from .engine import (
    AnalyticsEngine,
    DataQualityError,
    _build_establishment_service_key,
    _normalize_dui_value,
    _normalize_non_negative_integer,
    _normalize_operator_name,
    _normalize_remuneration_value,
    project_questionnaire,
)
from .evaluation_projection import project_evaluation_activities
from .filters import (
    FILTER_NAMES,
    build_filter_context,
    record_matches_evaluation,
    record_matches_questionnaire,
    record_matches_raw,
    resolve_filters,
)
from .geography import DEPARTMENT_TO_REGION_CODE, get_region_label
from .permissions import get_scope
from .prestations import load_conditional_definitions, project_received_people_records
from .repositories.base import QuestionnaireRepository


DEFAULT_ESTABLISHMENT_PAGE_SIZE = 50

ALLOWED_DASHBOARD_FILTERS = tuple(sorted(FILTER_NAMES))
NETWORK_OVERVIEW_DEVICE_ORDER = ("ueros", "espo", "esrp")
NETWORK_OVERVIEW_EDITORIAL = {
    "ueros": {
        "label": "UEROS",
        "subtitle": "Unités d’évaluation, de réentraînement et d’orientation sociale et professionnelle",
        "public_text": "Personnes atteintes de lésions cérébrales acquises.",
        "objectives": (
            "Évaluer les possibilités de réinsertion sociale et professionnelle.",
            "Identifier les potentialités professionnelles.",
            "Tester les possibilités d’adaptation.",
            "Préconiser une orientation concrète.",
        ),
    },
    "espo": {
        "label": "ESPO / Pré-orientation",
        "subtitle": "Établissements et services de pré-orientation",
        "public_text": "Travailleurs handicapés souhaitant élaborer ou confirmer un projet professionnel.",
        "objectives": (
            "Élaborer ou confirmer un projet professionnel.",
            "Réaliser un bilan dynamique.",
            "Tester le projet visé.",
            "Conclure par une préconisation d’orientation.",
        ),
    },
    "esrp": {
        "label": "ESRP",
        "subtitle": "Établissements et services de réadaptation professionnelle",
        "public_text": "Travailleurs handicapés sur orientation de la CDAPH.",
        "objectives": (
            "Évaluer pour identifier le parcours le plus adapté.",
            "Compenser le handicap dans le parcours de formation.",
            "Préparer et former à l’emploi.",
            "Accompagner vers et dans l’emploi.",
        ),
    },
}


@dataclass(frozen=True)
class DashboardResult:
    payload: dict[str, object]


def build_dashboard_payload(
    repository: QuestionnaireRepository,
    user_context: UserContext,
    filters: dict[str, object] | None = None,
) -> DashboardResult:
    raw_records = tuple(repository.list_raw_questionnaires())
    permission_scope = get_scope(user_context)
    resolved_filters = resolve_filters(
        filters or {},
        compatible_filters=ALLOWED_DASHBOARD_FILTERS,
        indicator_id="dashboard",
        context=build_filter_context(raw_records),
        permission_scope=permission_scope,
    )

    current_records = _select_dashboard_raw_records(raw_records, resolved_filters)
    base_comparison_filters = {
        key: value
        for key, value in resolved_filters.applied.items()
        if key not in {"completion_scope", "dispositifs"}
    }
    base_geography_filters = {
        key: value
        for key, value in resolved_filters.applied.items()
        if key not in {"region_code", "department_code"}
    }

    overview_engine = AnalyticsEngine(repository)
    overview_counts = _build_questionnaire_counts(current_records, resolved_filters=resolved_filters)
    overview_and_activity = _build_overview_and_activity_sections(
        overview_engine,
        user_context,
        current_records,
        resolved_filters.applied,
        base_comparison_filters,
        overview_counts,
    )
    network_overview = _safe_section(
        "Le réseau en un regard",
        lambda: _build_network_overview_section(current_records, resolved_filters.applied),
    )
    geography = _safe_section(
        "Territoires",
        lambda: _build_geography_section(raw_records, resolved_filters, base_geography_filters, permission_scope),
    )
    establishments = _safe_section(
        "Établissements et services",
        lambda: _build_establishment_rows(current_records),
    )
    internal = _safe_section(
        "Informations complémentaires internes",
        lambda: _build_internal_section(current_records, resolved_filters=resolved_filters),
    )
    quality = _safe_section(
        "Qualité des données",
        lambda: _build_quality_section(current_records, user_context),
    )
    modalites = _safe_section(
        "Modalités d’accompagnement",
        lambda: _build_modalites_section(current_records, resolved_filters.applied),
    )
    insertion = _safe_section(
        "Insertion professionnelle",
        lambda: _build_insertion_section(current_records, resolved_filters.applied),
    )
    participation = _safe_section(
        "Participation institutionnelle",
        lambda: _build_participation_section(
            overview_engine,
            user_context,
            current_records,
            resolved_filters.applied,
        ),
    )

    payload = {
        "filters": {
            "applied": dict(resolved_filters.applied),
            "requested": dict(resolved_filters.requested),
            "warnings": list(resolved_filters.warnings),
            "available": {
                "completion_scope": [
                    {"id": "all", "label": "Tous les questionnaires"},
                    {"id": "completed", "label": "Questionnaires terminés"},
                    {"id": "in_progress", "label": "Questionnaires en cours"},
                ],
                "campaign_available": bool(build_filter_context(raw_records).campaign_filter_available),
            },
        },
        "overview": overview_and_activity["overview"],
        "network_overview": network_overview,
        "activity": overview_and_activity["activity"],
        "modalites": modalites,
        "insertion": insertion,
        "participation_institutionnelle": participation,
        "geography": geography,
        "establishments": establishments,
        "quality": quality,
        "internal": internal,
        "source_matrix": build_source_matrix(),
        "freshness_at": repository.get_freshness_at(),
    }
    return DashboardResult(payload=payload)


def _safe_section(title: str, builder):
    try:
        payload = builder()
    except Exception:
        return {
            "title": title,
            "status": "error",
            "message": f"{title} indisponible pour le moment.",
        }
    if isinstance(payload, dict):
        return {
            "title": payload.get("title", title),
            "status": payload.get("status", "available"),
            **payload,
        }
    return {
        "title": title,
        "status": "error",
        "message": f"{title} indisponible pour le moment.",
    }


def build_source_matrix() -> list[dict[str, str]]:
    return [
        {
            "rubrique": "Vue d’ensemble",
            "demande": "Nombre de personnes reçues toutes catégories confondues",
            "indicator_id": "people.received.all",
            "source": "prestations_json + fallback plat contrôlé",
            "path": "prestations_json.<conditional_id>.fileActive + sorties pour ESRP/ESPO/UEROS ; fileActive pour les évaluations",
            "unit": "personnes déclarées",
            "grain": "composite",
            "availability": "available",
            "notes": "DEAc exclu.",
        },
        {
            "rubrique": "Activité",
            "demande": "Évaluations préliminaires",
            "indicator_id": "preliminary.evaluations",
            "source": "people.received.pec + people.received.other_eval",
            "path": "indicateurs canoniques",
            "unit": "personnes déclarées",
            "grain": "composite",
            "availability": "available",
            "notes": "PEC + autres dispositifs d’évaluation.",
        },
        {
            "rubrique": "Modalités d’accompagnement",
            "demande": "Hors les murs",
            "indicator_id": "support.outside_walls",
            "source": "prestations_json",
            "path": "directAvecOrp.row.hors_murs_personnes",
            "unit": "personnes déclarées",
            "grain": "bloc direct par questionnaire",
            "availability": "available",
            "notes": "Somme lue sur les blocs directs ESRP, ESPO et UEROS.",
        },
        {
            "rubrique": "Activité",
            "demande": "Sous-indicateurs ESRP",
            "indicator_id": "activity.esrp.details",
            "source": "prestations_json + prestations_details_json",
            "path": "prestations_json.<conditional_id>.fileActive + prestations_json.<conditional_id>.sorties",
            "unit": "personnes déclarées",
            "grain": "bloc conditionnel ESRP",
            "availability": "available",
            "notes": "Détails affichés comme non additifs.",
        },
        {
            "rubrique": "Insertion professionnelle",
            "demande": "Volumes emploi et préconisations",
            "indicator_id": "employment.volumes",
            "source": "prestations_json",
            "path": "directAvecOrp.row.emploi_* + preconisationsBloc.*",
            "unit": "volumes déclarés",
            "grain": "bloc direct par questionnaire",
            "availability": "available",
            "notes": "Les pourcentages restent masqués tant que le dénominateur métier n’est pas arbitré.",
        },
        {
            "rubrique": "Informations complémentaires internes",
            "demande": "DUI",
            "indicator_id": "internal.dui",
            "source": "q38_dui, q38_dui_lequel",
            "path": "colonnes plates",
            "unit": "établissements et services",
            "grain": "campaign_year+finess_main+dispositif",
            "availability": "available",
            "notes": "Comptage dédupliqué par établissement et service.",
        },
        {
            "rubrique": "Informations complémentaires internes",
            "demande": "Rémunération",
            "indicator_id": "internal.remuneration",
            "source": "q40_remuneration, q40_operateur",
            "path": "colonnes plates",
            "unit": "établissements et services",
            "grain": "campaign_year+finess_main+dispositif",
            "availability": "available",
            "notes": "Docaposte, ASP, double usage, autre, ni l’un ni l’autre.",
        },
    ]


def _build_main_indicators(
    engine: AnalyticsEngine,
    user_context: UserContext,
    current_records: tuple[RawQuestionnaireRecord, ...],
    filters: dict[str, object],
) -> dict[str, dict[str, object]]:
    selected_dispositifs = set(filters.get("dispositifs", ()))
    if selected_dispositifs:
        return _build_main_indicators_for_dispositifs(current_records, selected_dispositifs)
    indicators = {
        "total": _indicator_payload(engine, "people.received.all", user_context, filters),
        "esrp": _indicator_payload(engine, "people.received.esrp", user_context, filters),
        "espo": _indicator_payload(engine, "people.received.espo", user_context, filters),
        "ueros": _indicator_payload(engine, "people.received.ueros", user_context, filters),
        "deac": _indicator_payload(engine, "people.received.deac", user_context, filters),
        "pec": _indicator_payload(engine, "people.received.pec", user_context, filters),
        "other_eval": _indicator_payload(engine, "people.received.other_eval", user_context, filters),
        "other_eval_professional": _indicator_payload(engine, "people.received.other_eval.professional_assessment", user_context, filters),
        "other_eval_without_orp": _indicator_payload(engine, "people.received.other_eval.without_orp_cdaph", user_context, filters),
        "other_eval_with_orp": _indicator_payload(engine, "people.received.other_eval.with_orp_cdaph", user_context, filters),
    }
    preliminary_total = indicators["pec"]["value"] + indicators["other_eval"]["value"]
    indicators["preliminary_evaluations"] = {
        "id": "preliminary.evaluations",
        "label": "Évaluations préliminaires",
        "definition": "PEC + autres dispositifs d’évaluation, avec ou sans ORP CDAPH.",
        "unit": "personnes déclarées",
        "value": preliminary_total,
        "status": "available",
        "children": [
            {"id": "people.received.pec", "label": indicators["pec"]["label"], "value": indicators["pec"]["value"]},
            {"id": "people.received.other_eval", "label": indicators["other_eval"]["label"], "value": indicators["other_eval"]["value"]},
        ],
    }
    indicators["esrp_certifying"] = {
        "id": "activity.esrp.certifying",
        "label": "Parcours à visée certifiante",
        "definition": "Somme déclarative des blocs ESRP de parcours à visée certifiante, non additive avec les autres sous-indicateurs.",
        "unit": "personnes déclarées",
        "value": _sum_file_active_for_block_names(
            current_records,
            prefixes=("Directes ORP CDAPH - Parcours accompagnement à visée certifiante -",),
            selected_dispositifs=selected_dispositifs,
        ),
        "status": "available",
    }
    indicators["esrp_sociopro"] = {
        "id": "activity.esrp.sociopro",
        "label": "Parcours socio-professionnels",
        "definition": "Somme déclarative des blocs ESRP de parcours socio-professionnels, non additive avec les autres sous-indicateurs.",
        "unit": "personnes déclarées",
        "value": _sum_file_active_for_block_names(
            current_records,
            prefixes=("Directes ORP CDAPH - Parcours à visée socio-professionnelle -",),
            selected_dispositifs=selected_dispositifs,
        ),
        "status": "available",
    }
    indicators["activity_details"] = _build_activity_detail_items(current_records, selected_dispositifs)
    return indicators


def _build_overview_and_activity_sections(
    engine: AnalyticsEngine,
    user_context: UserContext,
    current_records: tuple[RawQuestionnaireRecord, ...],
    filters: dict[str, object],
    base_comparison_filters: dict[str, object],
    overview_counts: dict[str, object],
) -> dict[str, dict[str, object]]:
    try:
        main_indicators = _build_main_indicators(engine, user_context, current_records, filters)
        status_comparison = _build_status_comparison(engine, user_context, current_records, base_comparison_filters, filters)
    except Exception:
        return {
            "overview": {
                "title": "Vue d’ensemble",
                "status": "error",
                "message": "Vue d’ensemble indisponible pour le moment.",
                "questionnaire_count": overview_counts["questionnaire_count"],
                "questionnaire_status_counts": overview_counts["questionnaire_status_counts"],
                "analytics_line_count": overview_counts["analytics_line_count"],
                "indicators": {},
                "deac": {
                    "label": "DEAc",
                    "status": "error",
                    "message": "Indicateur indisponible pour le moment.",
                },
            },
            "activity": {
                "title": "Activité",
                "status": "error",
                "message": "Activité indisponible pour le moment.",
                "cards": [],
                "other_evaluations": {"title": "Autres dispositifs d’évaluation", "items": []},
                "status_comparison": {"questionnaires": {}, "rows": []},
            },
        }
    return {
        "overview": {
            "title": "Vue d’ensemble",
            "status": "available",
            "questionnaire_count": overview_counts["questionnaire_count"],
            "questionnaire_status_counts": overview_counts["questionnaire_status_counts"],
            "analytics_line_count": overview_counts["analytics_line_count"],
            "completion_notice": "Les chiffres incluent actuellement les questionnaires terminés et en cours de complétude."
            if filters.get("completion_scope", "all") == "all"
            else None,
            "formula": "Total = ESRP + ESPO + UEROS + PEC + autres dispositifs d’évaluation",
            "indicators": main_indicators,
            "deac": {
                "label": "DEAc",
                "status": "available",
                "unit": main_indicators["deac"]["unit"],
                "value": main_indicators["deac"]["value"],
                "message": "DEAc est affiché séparément et reste exclu du total général.",
            },
        },
        "activity": _build_activity_section(main_indicators, status_comparison, current_records, filters),
    }


def _indicator_payload(
    engine: AnalyticsEngine,
    indicator_id: str,
    user_context: UserContext,
    filters: dict[str, object],
) -> dict[str, object]:
    result = engine.compute_indicator(indicator_id, filters=filters, user_context=user_context)
    definition = get_indicator_definition(indicator_id)
    return {
        "id": indicator_id,
        "label": result.label,
        "definition": definition.definition if definition is not None else "",
        "unit": result.unit,
        "value": result.value,
        "status": "available",
        "breakdown": dict(result.breakdown),
    }


def _build_questionnaire_counts(
    records: tuple[RawQuestionnaireRecord, ...],
    *,
    resolved_filters,
) -> dict[str, object]:
    uuids = {
        str(record.uuid).strip()
        for record in records
        if record.uuid is not None and str(record.uuid).strip()
    }
    analytics_line_keys = set()
    for projected in _collect_received_rows(records, resolved_filters=resolved_filters):
        key = _build_establishment_service_key(projected)
        if key is not None:
            analytics_line_keys.add((key.campaign_year, key.finess_main, key.dispositif))
    return {
        "questionnaire_count": len(uuids),
        "questionnaire_status_counts": {
            "completed": sum(1 for record in records if record.completion_status == "completed"),
            "in_progress": sum(1 for record in records if record.completion_status == "in_progress"),
        },
        "analytics_line_count": len(analytics_line_keys),
    }


def _build_status_comparison(
    engine: AnalyticsEngine,
    user_context: UserContext,
    current_records: tuple[RawQuestionnaireRecord, ...],
    filters_without_completion: dict[str, object],
    filters: dict[str, object],
) -> dict[str, object]:
    selected_dispositifs = set(filters.get("dispositifs", ()))
    if selected_dispositifs:
        return _build_status_comparison_for_dispositifs(current_records, selected_dispositifs)
    scopes = {
        "all": filters_without_completion,
        "completed": {**filters_without_completion, "completion_scope": "completed"},
        "in_progress": {**filters_without_completion, "completion_scope": "in_progress"},
    }
    indicator_ids = [
        "questionnaires.count",
        "people.received.all",
        "people.received.esrp",
        "people.received.espo",
        "people.received.ueros",
        "people.received.pec",
        "people.received.other_eval",
    ]
    values: dict[str, dict[str, int]] = {}
    for scope_name, scope_filters in scopes.items():
        values[scope_name] = {}
        for indicator_id in indicator_ids:
            values[scope_name][indicator_id] = engine.compute_indicator(
                indicator_id,
                filters=scope_filters,
                user_context=user_context,
            ).value
    comparison_rows = []
    for indicator_id, label in (
        ("people.received.all", "Nombre de personnes reçues toutes catégories confondues"),
        ("people.received.esrp", "Nombre de personnes reçues en ESRP"),
        ("people.received.espo", "Nombre de personnes reçues en ESPO"),
        ("people.received.ueros", "Nombre de personnes reçues en UEROS"),
        ("people.received.pec", "Nombre de personnes reçues en PEC"),
        ("people.received.other_eval", "Nombre de personnes reçues sur les autres dispositifs d’évaluation"),
    ):
        total = values["all"][indicator_id]
        in_progress = values["in_progress"][indicator_id]
        comparison_rows.append({
            "id": indicator_id,
            "label": label,
            "all": total,
            "completed": values["completed"][indicator_id],
            "in_progress": in_progress,
            "in_progress_share": round((in_progress / total) * 100, 1) if total else 0.0,
        })
    return {
        "questionnaires": {
            "all": values["all"]["questionnaires.count"],
            "completed": values["completed"]["questionnaires.count"],
            "in_progress": values["in_progress"]["questionnaires.count"],
        },
        "rows": comparison_rows,
    }


def _build_main_indicators_for_dispositifs(
    current_records: tuple[RawQuestionnaireRecord, ...],
    selected_dispositifs: set[str],
) -> dict[str, dict[str, object]]:
    received_rows = _collect_received_rows(current_records, resolved_filters=None)
    totals = {"esrp": 0, "espo": 0, "ueros": 0, "deac": 0}
    for row in received_rows:
        if row.dispositif not in selected_dispositifs:
            continue
        if row.dispositif == "esrp":
            totals["esrp"] += _normalize_non_negative_integer(row.q53_accompagnes__esrp, "q53_accompagnes__esrp")
        elif row.dispositif == "espo":
            totals["espo"] += _normalize_non_negative_integer(row.q53_accompagnes__espo, "q53_accompagnes__espo")
        elif row.dispositif == "ueros":
            totals["ueros"] += _normalize_non_negative_integer(row.q53_accompagnes__ueros, "q53_accompagnes__ueros")
        elif row.dispositif == "deac":
            totals["deac"] += _normalize_non_negative_integer(row.q53_accompagnes__deac, "q53_accompagnes__deac")
    total = totals["esrp"] + totals["espo"] + totals["ueros"]
    details = _build_activity_detail_items(current_records, selected_dispositifs)
    return {
        "total": _static_indicator_payload("people.received.all", "Nombre de personnes reçues toutes catégories confondues", total),
        "esrp": _static_indicator_payload("people.received.esrp", "Nombre de personnes reçues en ESRP", totals["esrp"]),
        "espo": _static_indicator_payload("people.received.espo", "Nombre de personnes reçues en ESPO", totals["espo"]),
        "ueros": _static_indicator_payload("people.received.ueros", "Nombre de personnes reçues en UEROS", totals["ueros"]),
        "deac": _static_indicator_payload("people.received.deac", "Nombre de personnes reçues en DEAc", totals["deac"]),
        "pec": _zero_indicator_payload("people.received.pec", "Nombre de personnes reçues en PEC"),
        "other_eval": _zero_indicator_payload("people.received.other_eval", "Volume déclaré de personnes reçues dans les autres dispositifs d'évaluation"),
        "other_eval_professional": _zero_indicator_payload("people.received.other_eval.professional_assessment", "Évaluations professionnelles"),
        "other_eval_without_orp": _zero_indicator_payload("people.received.other_eval.without_orp_cdaph", "Autres évaluations sans ORP CDAPH"),
        "other_eval_with_orp": _zero_indicator_payload("people.received.other_eval.with_orp_cdaph", "Autres évaluations avec ORP CDAPH"),
        "preliminary_evaluations": {
            "id": "preliminary.evaluations",
            "label": "Évaluations préliminaires",
            "definition": "Les évaluations préliminaires ne sont pas rattachées au filtre dispositif courant.",
            "unit": "personnes déclarées",
            "value": 0,
            "status": "available",
            "children": [],
        },
        "esrp_certifying": _static_indicator_payload(
            "activity.esrp.certifying",
            "Parcours à visée certifiante",
            _sum_file_active_for_block_names(
                current_records,
                prefixes=("Directes ORP CDAPH - Parcours accompagnement à visée certifiante -",),
                selected_dispositifs=selected_dispositifs,
            ),
        ),
        "esrp_sociopro": _static_indicator_payload(
            "activity.esrp.sociopro",
            "Parcours socio-professionnels",
            _sum_file_active_for_block_names(
                current_records,
                prefixes=("Directes ORP CDAPH - Parcours à visée socio-professionnelle -",),
                selected_dispositifs=selected_dispositifs,
            ),
        ),
        "activity_details": details,
    }


def _build_status_comparison_for_dispositifs(
    current_records: tuple[RawQuestionnaireRecord, ...],
    selected_dispositifs: set[str],
) -> dict[str, object]:
    values = {}
    for scope_name, expected_status in (("all", None), ("completed", "completed"), ("in_progress", "in_progress")):
        scoped_records = current_records if expected_status is None else tuple(
            record for record in current_records if record.completion_status == expected_status
        )
        metrics = _build_main_indicators_for_dispositifs(scoped_records, selected_dispositifs)
        values[scope_name] = {
            "questionnaires.count": len({str(record.uuid).strip() for record in scoped_records if record.uuid}),
            "people.received.all": metrics["total"]["value"],
            "people.received.esrp": metrics["esrp"]["value"],
            "people.received.espo": metrics["espo"]["value"],
            "people.received.ueros": metrics["ueros"]["value"],
        }
    comparison_rows = []
    for indicator_id, label in (
        ("people.received.all", "Nombre de personnes reçues toutes catégories confondues"),
        ("people.received.esrp", "Nombre de personnes reçues en ESRP"),
        ("people.received.espo", "Nombre de personnes reçues en ESPO"),
        ("people.received.ueros", "Nombre de personnes reçues en UEROS"),
    ):
        total = values["all"][indicator_id]
        in_progress = values["in_progress"][indicator_id]
        comparison_rows.append({
            "id": indicator_id,
            "label": label,
            "all": total,
            "completed": values["completed"][indicator_id],
            "in_progress": in_progress,
            "in_progress_share": round((in_progress / total) * 100, 1) if total else 0.0,
        })
    return {
        "questionnaires": {
            "all": values["all"]["questionnaires.count"],
            "completed": values["completed"]["questionnaires.count"],
            "in_progress": values["in_progress"]["questionnaires.count"],
        },
        "rows": comparison_rows,
    }


def _build_geography_section(
    raw_records: tuple[RawQuestionnaireRecord, ...],
    resolved_filters,
    base_filters: dict[str, object],
    permission_scope,
) -> dict[str, object]:
    base_resolved = resolved_filters if not any(key in resolved_filters.applied for key in ("region_code", "department_code")) else resolve_filters(
        base_filters,
        compatible_filters=ALLOWED_DASHBOARD_FILTERS,
        indicator_id="dashboard_geography",
        context=build_filter_context(raw_records),
        permission_scope=permission_scope,
    )
    visible_records = _select_dashboard_raw_records(raw_records, base_resolved)
    region_totals: dict[str, dict[str, object]] = {
        region_code: {
            "region_code": region_code,
            "label": get_region_label(region_code),
            "questionnaire_count": 0,
            "total": 0,
        }
        for region_code in sorted(set(DEPARTMENT_TO_REGION_CODE.values()))
    }
    department_totals: dict[str, dict[str, object]] = {
        department_code: {
            "department_code": department_code,
            "region_code": region_code,
            "questionnaire_count": 0,
            "total": 0,
        }
        for department_code, region_code in sorted(DEPARTMENT_TO_REGION_CODE.items())
    }
    unknown_departments: dict[str, int] = {}

    question_uuids_by_region: dict[str, set[str]] = {code: set() for code in region_totals}
    question_uuids_by_department: dict[str, set[str]] = {code: set() for code in department_totals}
    for record in visible_records:
        uuid = str(record.uuid or "").strip()
        if record.region_code in question_uuids_by_region and uuid:
            question_uuids_by_region[record.region_code].add(uuid)
        if record.department_code in question_uuids_by_department and uuid:
            question_uuids_by_department[record.department_code].add(uuid)
        if record.department_code is None and record.raw.get("es_departement"):
            raw_value = str(record.raw.get("es_departement"))
            unknown_departments[raw_value] = unknown_departments.get(raw_value, 0) + 1

    for projected in _collect_received_rows(visible_records, resolved_filters=base_resolved):
        total_value = _device_row_total(projected)
        if projected.region_code in region_totals:
            region_totals[projected.region_code]["total"] += total_value
        if projected.department_code in department_totals:
            department_totals[projected.department_code]["total"] += total_value

    evaluation_rows = _collect_evaluation_rows(visible_records, resolved_filters=base_resolved)
    for evaluation_row in evaluation_rows:
        value = _normalize_non_negative_integer(evaluation_row.declared_volume, field_name=evaluation_row.source_path or "declared_volume")
        if evaluation_row.region_code in region_totals:
            region_totals[evaluation_row.region_code]["total"] += value
        if evaluation_row.department_code in department_totals:
            department_totals[evaluation_row.department_code]["total"] += value

    for region_code, uuids in question_uuids_by_region.items():
        region_totals[region_code]["questionnaire_count"] = len(uuids)
    for department_code, uuids in question_uuids_by_department.items():
        department_totals[department_code]["questionnaire_count"] = len(uuids)

    selected_region = resolved_filters.applied.get("region_code")
    department_rows = [
        item for item in department_totals.values()
        if not isinstance(selected_region, str) or item["region_code"] == selected_region
    ]
    return {
        "title": "Territoires",
        "selected_region": selected_region,
        "regions": list(region_totals.values()),
        "departments": department_rows,
        "unknown_departments": [
            {"value": key, "questionnaire_count": count}
            for key, count in sorted(unknown_departments.items())
        ],
    }


def _build_establishment_rows(records: tuple[RawQuestionnaireRecord, ...]) -> dict[str, object]:
    received_rows = _collect_received_rows(records, resolved_filters=None)
    evaluation_rows = _collect_evaluation_rows(records, resolved_filters=None)
    rows_by_finess: dict[str, dict[str, object]] = {}
    questionnaire_status_by_finess: dict[str, set[str]] = {}
    questionnaire_count_by_finess: dict[str, set[str]] = {}

    for raw_record in records:
        if raw_record.finess_main is None:
            continue
        finess = raw_record.finess_main
        establishment = rows_by_finess.setdefault(finess, {
            "finess_main": finess,
            "name": _first_non_empty_text(raw_record.raw, "es_nom", "etablissement_nom", "nom_etablissement"),
            "region_code": raw_record.region_code,
            "region_label": get_region_label(raw_record.region_code),
            "department_code": raw_record.department_code,
            "dispositifs": set(),
            "questionnaire_count": 0,
            "statuses": set(),
            "totals": {
                "total": 0,
                "esrp": 0,
                "espo": 0,
                "ueros": 0,
                "deac": 0,
                "pec": 0,
                "other_eval": 0,
            },
        })
        if not establishment["name"]:
            establishment["name"] = _first_non_empty_text(
                raw_record.raw,
                "es_nom",
                "etablissement_nom",
                "nom_etablissement",
            )
        if raw_record.completion_status:
            questionnaire_status_by_finess.setdefault(finess, set()).add(raw_record.completion_status)
        if raw_record.uuid:
            questionnaire_count_by_finess.setdefault(finess, set()).add(str(raw_record.uuid))

    for row in received_rows:
        if row.finess_main is None:
            continue
        current = rows_by_finess.setdefault(row.finess_main, {
            "finess_main": row.finess_main,
            "region_code": row.region_code,
            "region_label": get_region_label(row.region_code),
            "department_code": row.department_code,
            "dispositifs": set(),
            "questionnaire_count": 0,
            "statuses": set(),
            "name": None,
            "totals": {"total": 0, "esrp": 0, "espo": 0, "ueros": 0, "deac": 0, "pec": 0, "other_eval": 0},
        })
        if row.dispositif:
            current["dispositifs"].add(row.dispositif.upper())
        if row.completion_status:
            current["statuses"].add(row.completion_status)
        if row.dispositif == "esrp":
            current["totals"]["esrp"] += _normalize_non_negative_integer(row.q53_accompagnes__esrp, "q53_accompagnes__esrp")
        if row.dispositif == "espo":
            current["totals"]["espo"] += _normalize_non_negative_integer(row.q53_accompagnes__espo, "q53_accompagnes__espo")
        if row.dispositif == "ueros":
            current["totals"]["ueros"] += _normalize_non_negative_integer(row.q53_accompagnes__ueros, "q53_accompagnes__ueros")
        if row.dispositif == "deac":
            current["totals"]["deac"] += _normalize_non_negative_integer(row.q53_accompagnes__deac, "q53_accompagnes__deac")

    for row in evaluation_rows:
        if row.finess_main is None:
            continue
        current = rows_by_finess.setdefault(row.finess_main, {
            "finess_main": row.finess_main,
            "region_code": row.region_code,
            "region_label": get_region_label(row.region_code),
            "department_code": row.department_code,
            "dispositifs": set(),
            "questionnaire_count": 0,
            "statuses": set(),
            "name": None,
            "totals": {"total": 0, "esrp": 0, "espo": 0, "ueros": 0, "deac": 0, "pec": 0, "other_eval": 0},
        })
        if row.completion_status:
            current["statuses"].add(row.completion_status)
        value = _normalize_non_negative_integer(row.declared_volume, row.source_path or "declared_volume")
        if row.evaluation_type == "pec":
            current["dispositifs"].add("PEC")
            current["totals"]["pec"] += value
        elif row.evaluation_type == "other_eval":
            current["dispositifs"].add("AUTRES ÉVALUATIONS")
            current["totals"]["other_eval"] += value

    items = []
    for finess, item in rows_by_finess.items():
        totals = item["totals"]
        totals["total"] = totals["esrp"] + totals["espo"] + totals["ueros"] + totals["pec"] + totals["other_eval"]
        item["questionnaire_count"] = len(questionnaire_count_by_finess.get(finess, set()))
        item["statuses"] = sorted(questionnaire_status_by_finess.get(finess, item["statuses"]))
        item["dispositifs"] = sorted(item["dispositifs"])
        items.append(item)
    items.sort(key=lambda item: (-item["totals"]["total"], item["finess_main"]))
    return {
        "title": "Établissements et services",
        "total_items": len(items),
        "page_size": DEFAULT_ESTABLISHMENT_PAGE_SIZE,
        "items": items[:DEFAULT_ESTABLISHMENT_PAGE_SIZE],
        "truncated": len(items) > DEFAULT_ESTABLISHMENT_PAGE_SIZE,
    }


def _first_non_empty_text(raw: dict[str, object], *field_names: str) -> str | None:
    for field_name in field_names:
        value = raw.get(field_name)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def _build_internal_section(records: tuple[RawQuestionnaireRecord, ...], *, resolved_filters) -> dict[str, object]:
    unique_questionnaires: dict[str, RawQuestionnaireRecord] = {}
    for index, record in enumerate(records):
        questionnaire_key = str(record.uuid).strip() if record.uuid is not None and str(record.uuid).strip() else f"__row__{index}"
        unique_questionnaires[questionnaire_key] = record

    dui_yes = dui_no = dui_unknown = 0
    dui_tools: dict[str, int] = {}
    remuneration = {
        "docaposte": 0,
        "asp": 0,
        "docaposte_and_asp": 0,
        "other": 0,
        "none": 0,
        "unknown": 0,
    }
    for record in unique_questionnaires.values():
        normalized_dui = _normalize_dui_value(record.q38_dui)
        if normalized_dui == "Oui":
            dui_yes += 1
            normalized_tool = _normalize_dui_tool(record.raw.get("q38_dui_lequel"))
            if normalized_tool is not None:
                dui_tools[normalized_tool] = dui_tools.get(normalized_tool, 0) + 1
        elif normalized_dui == "Non":
            dui_no += 1
        else:
            dui_unknown += 1

        remuneration_value = _normalize_remuneration_value(record.q40_remuneration)
        operator_raw = str(record.q40_operateur).strip() if record.q40_operateur is not None else ""
        operator_tokens = _normalize_operator_tokens(operator_raw)
        if remuneration_value is None:
            remuneration["unknown"] += 1
        elif remuneration_value == "Non":
            remuneration["none"] += 1
        elif not operator_tokens:
            remuneration["unknown"] += 1
        elif {"docaposte", "asp"}.issubset(operator_tokens):
            remuneration["docaposte_and_asp"] += 1
        elif "docaposte" in operator_tokens:
            remuneration["docaposte"] += 1
        elif "asp" in operator_tokens:
            remuneration["asp"] += 1
        else:
            remuneration["other"] += 1

    return {
        "title": "Informations complémentaires internes",
        "dui": {
            "yes": dui_yes,
            "no": dui_no,
            "unknown": dui_unknown,
            "tools": [
                {"label": label, "count": count}
                for label, count in sorted(dui_tools.items(), key=lambda item: (-item[1], item[0]))
            ],
        },
        "remuneration": remuneration,
    }


def _build_quality_section(records: tuple[RawQuestionnaireRecord, ...], user_context: UserContext) -> dict[str, object]:
    summary = analyze_data_quality(records, user_context)
    normalized_finess_count = 0
    for issue in summary.issues:
        if issue.code == "normalized_finess":
            normalized_finess_count = issue.record_count
            break
    return {
        "summary": {
            "analyzed_questionnaires": summary.analyzed_questionnaires,
            "issue_count": summary.issue_count,
            "affected_record_count": summary.affected_record_count,
            "invalid_finess_count": summary.invalid_finess_count,
            "unknown_department_count": summary.unknown_department_count,
            "unresolved_region_count": summary.unresolved_region_count,
            "normalized_finess_count": normalized_finess_count,
            "global_level": summary.global_level,
        },
        "messages": [
            "Aucune erreur bloquante détectée sur les FINESS ou les départements." if summary.invalid_finess_count == 0 and summary.unknown_department_count == 0 else "Des anomalies de source subsistent.",
            "Dix FINESS sont normalisés uniquement dans Analytics." if normalized_finess_count else "Aucune normalisation FINESS détectée dans le périmètre courant.",
            "La campagne n’est pas disponible dans la source actuelle.",
            "DEAc est non alimenté à ce stade.",
        ],
        "issues": [
            {
                "code": issue.code,
                "severity": issue.severity,
                "message": issue.message,
                "record_count": issue.record_count,
            }
            for issue in summary.issues
        ],
    }


def _build_activity_section(
    main_indicators: dict[str, dict[str, object]],
    status_comparison: dict[str, object],
    records: tuple[RawQuestionnaireRecord, ...],
    filters: dict[str, object],
) -> dict[str, object]:
    return {
        "title": "Activité",
        "status": "available",
        "cards": [
            _card_from_indicator(main_indicators["esrp"]),
            _card_from_indicator(main_indicators["esrp_certifying"]),
            _card_from_indicator(main_indicators["esrp_sociopro"]),
            _card_from_indicator(main_indicators["ueros"]),
            _card_from_indicator(main_indicators["espo"]),
            _card_from_indicator(main_indicators["preliminary_evaluations"]),
        ],
        "details": list(main_indicators.get("activity_details", [])),
        "other_evaluations": {
            "title": "Autres dispositifs d’évaluation",
            "total": main_indicators["other_eval"].get("value", 0),
            "items": [
                _card_from_indicator(main_indicators["other_eval_professional"]),
                _card_from_indicator(main_indicators["other_eval_without_orp"]),
                _card_from_indicator(main_indicators["other_eval_with_orp"]),
            ],
        },
        "etp_analysis": _build_etp_analysis_section(records, filters),
        "status_comparison": status_comparison,
    }


def _build_etp_analysis_section(
    records: tuple[RawQuestionnaireRecord, ...],
    filters: dict[str, object],
) -> dict[str, object]:
    total_etp = _sum_dispositif_etp(records, ("etp_esrp", "etp_espo", "etp_ueros", "etp_deac"))
    comparable_target = _sum_dispositif_etp(records, ("etp_esrp", "etp_espo", "etp_ueros"))
    deac_etp = _sum_dispositif_etp(records, ("etp_deac",))
    metiers_total = _sum_declared_metiers_etp(records)
    cdi_total = _sum_declared_metiers_component(records, "etpCdi")
    cdd_total = _sum_declared_metiers_component(records, "etpCdd")
    externe_total = _sum_declared_external_metiers_etp(records)
    selected_dispositifs = tuple(filters.get("dispositifs", ()))
    breakdown_available = not selected_dispositifs

    cards = [
        {
            "id": "etp.total",
            "label": "ETP déclarés tous dispositifs",
            "definition": "Somme des ETP saisis sur les champs ESRP, ESPO, UEROS et DEAc du questionnaire.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(total_etp),
            "status": "available",
        },
        {
            "id": "etp.esrp",
            "label": "ETP ESRP",
            "definition": "Somme des ETP déclarés sur le dispositif ESRP.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(_sum_dispositif_etp(records, ("etp_esrp",))),
            "status": "available",
        },
        {
            "id": "etp.espo",
            "label": "ETP ESPO",
            "definition": "Somme des ETP déclarés sur le dispositif ESPO.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(_sum_dispositif_etp(records, ("etp_espo",))),
            "status": "available",
        },
        {
            "id": "etp.ueros",
            "label": "ETP UEROS",
            "definition": "Somme des ETP déclarés sur le dispositif UEROS.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(_sum_dispositif_etp(records, ("etp_ueros",))),
            "status": "available",
        },
        {
            "id": "etp.deac",
            "label": "ETP DEAc",
            "definition": "Somme des ETP déclarés sur le dispositif DEAc.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(deac_etp),
            "status": "available",
        },
        {
            "id": "etp.metiers.total",
            "label": "ETP métiers déclarés",
            "definition": "Somme des ETP saisis dans la répartition métiers. Cette répartition couvre ESRP, ESPO et UEROS, hors DEAc.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(metiers_total),
            "status": "available",
        },
    ]

    if not breakdown_available:
        return {
            "title": "Analyse des ETP",
            "status": "available",
            "cards": cards,
            "details": [
                {
                    "id": "etp.breakdown.filtered_out",
                    "label": "Répartition métiers et contrats",
                    "status": "to_map",
                    "message": "La répartition métiers n’est pas ventilée par dispositif dans la source actuelle.",
                },
            ],
            "top_metiers": [],
        }

    ecart = metiers_total - comparable_target
    details = [
        {
            "id": "etp.comparable_target",
            "label": "Cible dispositifs hors DEAc",
            "definition": "Somme des ETP ESRP, ESPO et UEROS saisis au niveau dispositif.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(comparable_target),
            "status": "available",
        },
        {
            "id": "etp.cdi",
            "label": "ETP CDI",
            "definition": "Somme des ETP CDI renseignés sur les lignes métiers internes.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(cdi_total),
            "status": "available",
        },
        {
            "id": "etp.cdd",
            "label": "ETP CDD",
            "definition": "Somme des ETP CDD renseignés sur les lignes métiers internes.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(cdd_total),
            "status": "available",
        },
        {
            "id": "etp.external",
            "label": "ETP externes",
            "definition": "Somme des ETP saisis sur les lignes métiers au mode Externe.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(externe_total),
            "status": "available",
        },
        {
            "id": "etp.gap",
            "label": "Écart métiers / cible hors DEAc",
            "definition": "Différence entre la somme métiers déclarée et la somme des ETP ESRP + ESPO + UEROS.",
            "unit": "ETP déclarés",
            "value": _serialize_decimal(ecart),
            "status": "available",
        },
    ]
    return {
        "title": "Analyse des ETP",
        "status": "available",
        "cards": cards,
        "details": details,
        "top_metiers": _build_top_metiers_items(records),
    }


def _build_modalites_section(
    records: tuple[RawQuestionnaireRecord, ...],
    filters: dict[str, object],
) -> dict[str, object]:
    selected_dispositifs = set(filters.get("dispositifs", ()))
    items = [_build_hors_les_murs_item(records, selected_dispositifs)]
    if selected_dispositifs:
        items.append({
            "id": "info_actions_filtered_out",
            "label": "Actions d’information",
            "status": "to_map",
            "message": "Les actions d’information ne sont pas rattachées au filtre dispositif courant.",
        })
        items.append({
            "id": "orienteurs_filtered_out",
            "label": "Orienteurs PEC et autres évaluations",
            "status": "to_map",
            "message": "Les orienteurs ne sont pas rattachés au filtre dispositif courant.",
        })
    else:
        items.extend(_build_information_actions_summary(records))
        items.extend(_build_orienteurs_items(records))
    return {
        "title": "Modalités d’accompagnement",
        "status": "available",
        "items": items,
    }


def _build_insertion_section(
    records: tuple[RawQuestionnaireRecord, ...],
    filters: dict[str, object],
) -> dict[str, object]:
    selected_dispositifs = set(filters.get("dispositifs", ()))
    employment_counters = _collect_employment_counters(records, selected_dispositifs)
    return {
        "title": "Insertion professionnelle",
        "status": "available",
        "items": [
            _build_employment_rate_card(
                "employment.access_rate",
                "Taux d’accès à l’emploi",
                employment_counters["emploi_acces_nb"],
                employment_counters["emploi_nb_repondants"],
                "Part des répondants ayant accédé à l’emploi dans les 12 mois suivant la sortie.",
            ),
            _build_employment_rate_card(
                "employment.presence_rate",
                "Taux de présence à l’emploi",
                employment_counters["emploi_presence_nb"],
                employment_counters["emploi_nb_repondants"],
                "Part des répondants encore en emploi au point de mesure à 12 mois.",
            ),
            *_build_employment_items(employment_counters),
            *_build_preconisation_items(records, selected_dispositifs),
        ],
    }


def _build_participation_section(
    engine: AnalyticsEngine,
    user_context: UserContext,
    records: tuple[RawQuestionnaireRecord, ...],
    filters: dict[str, object],
) -> dict[str, object]:
    mdph_epe = _indicator_payload(engine, "institution.mdph.epe.count", user_context, filters)
    mdph_cdaph = _indicator_payload(engine, "institution.mdph.cdaph.count", user_context, filters)
    mdph_working_groups = _indicator_payload(engine, "institution.mdph.working_groups.count", user_context, filters)
    return {
        "title": "Participation institutionnelle",
        "status": "available",
        "items": [
            _card_from_indicator(mdph_epe),
            _card_from_indicator(mdph_cdaph),
            _card_from_indicator(mdph_working_groups),
            _build_committee_participation_card(
                records,
                item_id="territorial_cle_cre",
                label="Participations aux CLE ou CRE",
                definition="Somme des participations déclarées aux CLE et CRE, en direct ou via représentation FAGERH.",
                fields=(
                    ("q48_cle", "ctx-q48", "CLE"),
                    ("q49_cre", "ctx-q49", "CRE"),
                ),
            ),
            _build_committee_participation_card(
                records,
                item_id="territorial_fiphfp",
                label="Participations aux comités locaux FIPHFP",
                definition="Somme des participations déclarées aux comités locaux FIPHFP, en direct ou via représentation FAGERH.",
                fields=(
                    ("q50_fiphfp", "ctx-q50", "FIPHFP"),
                ),
            ),
        ],
    }


def _build_network_overview_section(
    records: tuple[RawQuestionnaireRecord, ...],
    filters: dict[str, object],
) -> dict[str, object]:
    requested_dispositifs = tuple(filters.get("dispositifs", ()))
    visible_device_ids = [device_id for device_id in NETWORK_OVERVIEW_DEVICE_ORDER if device_id in requested_dispositifs]
    if not visible_device_ids:
        visible_device_ids = list(NETWORK_OVERVIEW_DEVICE_ORDER) if not requested_dispositifs else []

    if requested_dispositifs and not visible_device_ids:
        return {
            "title": "Le réseau en un regard",
            "status": "available",
            "message": "Le comparatif porte uniquement sur UEROS, ESPO et ESRP. Le filtre dispositif courant n’affiche donc aucune colonne dédiée.",
            "devices": [],
        }

    received_rows = _collect_received_rows(records, resolved_filters=None)
    rows_by_device = {
        device_id: [row for row in received_rows if row.dispositif == device_id]
        for device_id in NETWORK_OVERVIEW_DEVICE_ORDER
    }
    total_people_compared = sum(_network_people_received(rows_by_device[device_id], device_id) for device_id in NETWORK_OVERVIEW_DEVICE_ORDER)

    devices = [
        _build_network_device_card(
            device_id,
            device_rows=rows_by_device[device_id],
            records=records,
            total_people_compared=total_people_compared,
            show_share=(len(visible_device_ids) > 1 and total_people_compared > 0),
            focused=(len(visible_device_ids) == 1),
        )
        for device_id in visible_device_ids
    ]
    return {
        "title": "Le réseau en un regard",
        "status": "available",
        "message": "Comparatif dynamique UEROS, ESPO / Pré-orientation et ESRP. Les textes restent éditoriaux ; les chiffres suivent les filtres courants.",
        "devices": devices,
    }


def _build_committee_participation_card(
    records: tuple[RawQuestionnaireRecord, ...],
    *,
    item_id: str,
    label: str,
    definition: str,
    fields: tuple[tuple[str, str, str], ...],
) -> dict[str, object]:
    direct_total = 0
    represented_total = 0
    no_total = 0
    children: list[dict[str, object]] = []

    for field_name, snapshot_name, short_label in fields:
        counters = {"direct": 0, "represented": 0, "no": 0}
        for record in records:
            raw_value = _read_committee_value(record, field_name=field_name, snapshot_name=snapshot_name)
            normalized = _normalize_committee_response(raw_value)
            if normalized == "direct":
                counters["direct"] += 1
            elif normalized == "represented":
                counters["represented"] += 1
            elif normalized == "no":
                counters["no"] += 1
        direct_total += counters["direct"]
        represented_total += counters["represented"]
        no_total += counters["no"]
        if counters["direct"] > 0:
            children.append({"label": f"{short_label} en direct", "value": counters["direct"], "unit": "participations"})
        if counters["represented"] > 0:
            children.append({"label": f"{short_label} via FAGERH", "value": counters["represented"], "unit": "participations"})

    if no_total > 0:
        children.append({"label": "Non participation déclarée", "value": no_total, "unit": "réponses"})

    total_participations = direct_total + represented_total
    return {
        "id": item_id,
        "label": label,
        "definition": definition,
        "unit": "participations",
        "value": total_participations,
        "status": "available",
        "children": children,
    }


def _read_committee_value(
    record: RawQuestionnaireRecord,
    *,
    field_name: str,
    snapshot_name: str,
) -> str:
    raw_value = record.raw.get(field_name)
    if isinstance(raw_value, str) and raw_value.strip():
        return raw_value.strip()
    controls = (((record.prestations_details_json or {}).get("__wizard_v3_state") or {}).get("controls") or {})
    by_name = controls.get("byName") if isinstance(controls, dict) else {}
    snapshot_payload = by_name.get(snapshot_name) if isinstance(by_name, dict) else None
    if isinstance(snapshot_payload, dict):
        value = snapshot_payload.get("value")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _normalize_committee_response(value: object) -> str | None:
    normalized = str(value or "").strip().lower()
    if not normalized:
        return None
    if normalized == "oui":
        return "direct"
    if normalized.startswith("non") and "fagerh" in normalized:
        return "represented"
    if normalized == "non":
        return "no"
    return None


def _build_network_device_card(
    device_id: str,
    *,
    device_rows: list[QuestionnaireRecord],
    records: tuple[RawQuestionnaireRecord, ...],
    total_people_compared: int,
    show_share: bool,
    focused: bool,
) -> dict[str, object]:
    editorial = NETWORK_OVERVIEW_EDITORIAL[device_id]
    matching_uuids = {
        str(row.uuid).strip()
        for row in device_rows
        if row.uuid is not None and str(row.uuid).strip()
    }
    matching_records = [
        record for record in records
        if record.uuid is not None and str(record.uuid).strip() in matching_uuids
    ]
    questionnaire_status_counts = {"completed": 0, "in_progress": 0}
    for record in matching_records:
        status = _completion_status_slug(record.completion_status)
        questionnaire_status_counts[status] = questionnaire_status_counts.get(status, 0) + 1

    people_received = _network_people_received(device_rows, device_id)
    organization_count = len({row.finess_main for row in device_rows if row.finess_main})

    public_metrics = [
        _network_metric("Personnes reçues", value=people_received, unit="personnes déclarées"),
        _network_metric("Questionnaires concernés", value=len(matching_uuids), unit="questionnaires"),
    ]
    if show_share:
        public_metrics.append(_network_metric(
            "Part du volume comparé",
            display_value=_format_network_percentage(people_received, total_people_compared),
            unit="du volume UEROS + ESPO + ESRP",
        ))

    dispositifs_metrics = [
        _network_metric("Établissements et services distincts", value=organization_count, unit="FINESS canoniques distincts"),
        _network_metric("Questionnaires terminés", value=questionnaire_status_counts["completed"], unit="questionnaires"),
        _network_metric("Questionnaires en cours", value=questionnaire_status_counts["in_progress"], unit="questionnaires"),
        _network_metric(
            "ETP déclarés",
            value=_serialize_decimal(_sum_declared_metiers_etp(matching_records)),
            unit="ETP déclarés",
        ),
    ]

    return {
        "id": device_id,
        "label": editorial["label"],
        "subtitle": editorial["subtitle"],
        "focused": focused,
        "public": {
            "text": editorial["public_text"],
            "metrics": public_metrics,
        },
        "dispositifs": {
            "text": "Lecture au grain FINESS canonique distinct, sans reproduction des chiffres historiques de l’affiche.",
            "metrics": dispositifs_metrics,
        },
        "objectives": {
            "items": list(editorial["objectives"]),
        },
        "results": {
            "items": _build_network_results_items(records, device_id),
        },
    }


def _build_network_results_items(
    records: tuple[RawQuestionnaireRecord, ...],
    device_id: str,
) -> list[dict[str, object]]:
    if device_id == "ueros":
        items = [
            item for item in _build_preconisation_items(records, {"ueros"})
            if item.get("id") == "precon_ueros"
        ]
        items.append(_build_network_activity_item(records, "ueros"))
        return items
    if device_id == "espo":
        items = [
            item for item in _build_preconisation_items(records, {"espo"})
            if item.get("id") == "precon_espo"
        ]
        items.append(_build_network_activity_item(records, "espo"))
        return items

    esrp_details = _build_activity_detail_items(records, {"esrp"})
    return [
        {
            "id": "activity.esrp.details",
            "label": "Détail des parcours ESRP",
            "definition": "Sous-indicateurs ESRP déclaratifs, non additifs entre eux.",
            "children": [
                {
                    "label": item["label"],
                    "value": item["value"],
                    "unit": item.get("unit", ""),
                }
                for item in esrp_details
            ],
        },
        *_build_employment_items(_collect_employment_counters(records, {"esrp"})),
    ]


def _network_people_received(rows: list[QuestionnaireRecord], device_id: str) -> int:
    field_name = f"q53_accompagnes__{device_id}"
    return sum(_normalize_non_negative_integer(getattr(row, field_name), field_name) for row in rows)


def _build_network_activity_item(
    records: tuple[RawQuestionnaireRecord, ...],
    device_id: str,
) -> dict[str, object]:
    totals = _sum_network_activity_totals(records, device_id)
    if totals["journees"] <= 0 and totals["journees_theoriques"] <= 0:
        return {
            "id": f"{device_id}_activity_not_mapped",
            "label": "Journées ou volumes d’activité",
            "status": "to_map",
            "message": "Source à cartographier",
        }
    return _detail_card_payload(
        f"{device_id}_activity",
        "Journées ou volumes d’activité",
        "Journées lues directement dans le bloc conditionnel du dispositif.",
        [
            ("Journées réalisées", totals["journees"], "journées"),
            ("Journées théoriques", totals["journees_theoriques"], "journées"),
        ],
    )


def _sum_network_activity_totals(
    records: tuple[RawQuestionnaireRecord, ...],
    device_id: str,
) -> dict[str, Decimal]:
    target_block_name = f"Directes ORP CDAPH - {device_id.upper()}"
    totals = {
        "journees": Decimal("0"),
        "journees_theoriques": Decimal("0"),
    }
    for _, block_name, state in _iter_matching_blocks(records):
        if block_name != target_block_name or not isinstance(state, dict):
            continue
        totals["journees"] += _normalize_non_negative_decimal(state.get("journees"))
        totals["journees_theoriques"] += _normalize_non_negative_decimal(state.get("journeesTheoriques"))
    return totals


def _sum_declared_metiers_etp(records: list[RawQuestionnaireRecord] | tuple[RawQuestionnaireRecord, ...]) -> Decimal:
    total = Decimal("0")
    for record in records:
        total += _sum_record_metiers_etp(record)
    return total


def _sum_record_metiers_etp(record: RawQuestionnaireRecord) -> Decimal:
    rows = _load_metiers_rows(record)
    total = Decimal("0")
    for row in rows:
        if not isinstance(row, dict):
            continue
        etp_value = row.get("etp")
        if etp_value not in (None, ""):
            total += _normalize_non_negative_decimal(etp_value)
            continue
        total += _normalize_non_negative_decimal(row.get("etpCdi"))
        total += _normalize_non_negative_decimal(row.get("etpCdd"))
    return total


def _sum_declared_metiers_component(
    records: list[RawQuestionnaireRecord] | tuple[RawQuestionnaireRecord, ...],
    field_name: str,
) -> Decimal:
    total = Decimal("0")
    for record in records:
        for row in _load_metiers_rows(record):
            if not isinstance(row, dict):
                continue
            mode = str(row.get("mode") or "").strip()
            if mode == "Externe":
                continue
            if mode != "Interne" and row.get("etpCdi") in (None, "") and row.get("etpCdd") in (None, ""):
                continue
            total += _normalize_non_negative_decimal(row.get(field_name))
    return total


def _sum_declared_external_metiers_etp(
    records: list[RawQuestionnaireRecord] | tuple[RawQuestionnaireRecord, ...],
) -> Decimal:
    total = Decimal("0")
    for record in records:
        for row in _load_metiers_rows(record):
            if not isinstance(row, dict):
                continue
            mode = str(row.get("mode") or "").strip()
            if mode != "Externe":
                continue
            total += _normalize_non_negative_decimal(row.get("etp"))
    return total


def _sum_dispositif_etp(
    records: list[RawQuestionnaireRecord] | tuple[RawQuestionnaireRecord, ...],
    field_names: tuple[str, ...],
) -> Decimal:
    total = Decimal("0")
    for record in records:
        raw = record.raw if isinstance(record.raw, dict) else {}
        for field_name in field_names:
            total += _normalize_non_negative_decimal(raw.get(field_name))
    return total


def _build_top_metiers_items(
    records: list[RawQuestionnaireRecord] | tuple[RawQuestionnaireRecord, ...],
) -> list[dict[str, object]]:
    by_metier: dict[str, dict[str, Decimal]] = {}
    for record in records:
        for row in _load_metiers_rows(record):
            if not isinstance(row, dict):
                continue
            label = str(row.get("metier") or "").strip()
            if not label:
                continue
            bucket = by_metier.setdefault(label, {
                "total": Decimal("0"),
                "interne": Decimal("0"),
                "externe": Decimal("0"),
                "cdi": Decimal("0"),
                "cdd": Decimal("0"),
            })
            mode = str(row.get("mode") or "").strip()
            has_internal_components = row.get("etpCdi") not in (None, "") or row.get("etpCdd") not in (None, "")
            if mode == "Interne" or (mode != "Externe" and has_internal_components):
                cdi = _normalize_non_negative_decimal(row.get("etpCdi"))
                cdd = _normalize_non_negative_decimal(row.get("etpCdd"))
                total = _normalize_non_negative_decimal(row.get("etp")) if row.get("etp") not in (None, "") else cdi + cdd
                bucket["interne"] += total
                bucket["cdi"] += cdi
                bucket["cdd"] += cdd
                bucket["total"] += total
            elif mode == "Externe":
                total = _normalize_non_negative_decimal(row.get("etp"))
                bucket["externe"] += total
                bucket["total"] += total
            else:
                total = _normalize_non_negative_decimal(row.get("etp"))
                bucket["total"] += total

    sorted_items = sorted(
        by_metier.items(),
        key=lambda item: (item[1]["total"], item[0]),
        reverse=True,
    )
    return [
        {
            "id": f"etp.metier.{index}",
            "label": label,
            "value": _serialize_decimal(values["total"]),
            "unit": "ETP déclarés",
            "definition": "Somme déclarée sur les lignes métiers internes et externes.",
            "children": [
                {"label": "Interne", "value": _serialize_decimal(values["interne"]), "unit": "ETP"},
                {"label": "Externe", "value": _serialize_decimal(values["externe"]), "unit": "ETP"},
                {"label": "CDI", "value": _serialize_decimal(values["cdi"]), "unit": "ETP"},
                {"label": "CDD", "value": _serialize_decimal(values["cdd"]), "unit": "ETP"},
            ],
        }
        for index, (label, values) in enumerate(sorted_items[:8], start=1)
    ]


def _load_metiers_rows(record: RawQuestionnaireRecord) -> list[dict[str, object]]:
    raw_value = record.raw.get("metiers_json")
    if raw_value in (None, ""):
        return []
    if isinstance(raw_value, list):
        return [item for item in raw_value if isinstance(item, dict)]
    if isinstance(raw_value, str):
        normalized = raw_value.strip()
        if not normalized:
            return []
        try:
            parsed = json.loads(normalized)
        except json.JSONDecodeError:
            return []
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        return []
    return []


def _network_metric(
    label: str,
    *,
    value: int | None = None,
    unit: str = "",
    display_value: str | None = None,
    message: str | None = None,
) -> dict[str, object]:
    payload = {
        "label": label,
        "unit": unit,
    }
    if value is not None:
        payload["value"] = value
    if display_value is not None:
        payload["display_value"] = display_value
    if message:
        payload["status"] = "to_map"
        payload["message"] = message
    else:
        payload["status"] = "available"
    return payload


def _format_network_percentage(value: int, total: int) -> str:
    if total <= 0:
        return "0 %"
    percentage = (Decimal(value) * Decimal("100")) / Decimal(total)
    quantized = percentage.quantize(Decimal("0.1"))
    return f"{str(quantized).replace('.', ',')} %"


def _completion_status_slug(value: str | None) -> str:
    if value == "completed":
        return "completed"
    return "in_progress"


def _card_from_indicator(indicator: dict[str, object]) -> dict[str, object]:
    return {
        "id": indicator["id"],
        "label": indicator["label"],
        "definition": indicator.get("definition") or "",
        "unit": indicator.get("unit") or "",
        "value": indicator["value"],
        "status": indicator.get("status", "available"),
        "children": indicator.get("children", []),
    }


def _collect_received_rows(
    records: tuple[RawQuestionnaireRecord, ...],
    *,
    resolved_filters,
) -> list[QuestionnaireRecord]:
    rows: dict[tuple[object, ...], QuestionnaireRecord] = {}
    for record in records:
        for projected in project_received_people_records(
            record,
            normalize_integer=_normalize_non_negative_integer,
            quality_error_cls=DataQualityError,
        ):
            if resolved_filters is not None and not record_matches_questionnaire(projected, resolved_filters):
                continue
            key = _build_establishment_service_key(projected)
            if key is None:
                continue
            rows[(key.campaign_year, key.finess_main, key.dispositif)] = projected
    return list(rows.values())


def _collect_evaluation_rows(
    records: tuple[RawQuestionnaireRecord, ...],
    *,
    resolved_filters,
) -> list[EvaluationActivityRecord]:
    if resolved_filters is not None and resolved_filters.applied.get("dispositifs"):
        return []
    rows: dict[tuple[object, ...], EvaluationActivityRecord] = {}
    for record in records:
        for projected in project_evaluation_activities(
            record,
            normalize_integer=_normalize_non_negative_integer,
            quality_error_cls=DataQualityError,
        ):
            if resolved_filters is not None and not record_matches_evaluation(projected, resolved_filters):
                continue
            key = (
                projected.campaign_year,
                projected.finess_main,
                projected.evaluation_type,
                projected.orientation_cdaph,
                projected.source_block_id,
            )
            rows[key] = projected
    return list(rows.values())


def _device_row_total(row: QuestionnaireRecord) -> int:
    return (
        _normalize_non_negative_integer(row.q53_accompagnes__esrp, "q53_accompagnes__esrp")
        + _normalize_non_negative_integer(row.q53_accompagnes__espo, "q53_accompagnes__espo")
        + _normalize_non_negative_integer(row.q53_accompagnes__ueros, "q53_accompagnes__ueros")
    )


def _normalize_dui_tool(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    collapsed = " ".join(text.split())
    return collapsed


def _normalize_operator_tokens(value: str) -> set[str]:
    if not value:
        return set()
    raw_parts = [part.strip() for part in value.replace("/", ",").replace(";", ",").split(",") if part.strip()]
    tokens = set()
    for part in raw_parts:
        normalized = _normalize_operator_name(part)
        if normalized is not None:
            tokens.add(normalized)
    return tokens


def _select_dashboard_raw_records(
    raw_records: tuple[RawQuestionnaireRecord, ...],
    resolved_filters,
) -> tuple[RawQuestionnaireRecord, ...]:
    if "dispositifs" not in resolved_filters.applied:
        return tuple(record for record in raw_records if record_matches_raw(record, resolved_filters))
    base_applied = dict(resolved_filters.applied)
    base_applied.pop("dispositifs", None)
    base_resolved = resolve_filters(
        base_applied,
        compatible_filters=ALLOWED_DASHBOARD_FILTERS,
        indicator_id="dashboard_dispositifs",
        context=build_filter_context(raw_records),
        permission_scope=None,
    )
    base_records = tuple(record for record in raw_records if record_matches_raw(record, base_resolved))
    matching_uuids = {
        str(row.uuid).strip()
        for row in _collect_received_rows(base_records, resolved_filters=resolved_filters)
        if row.uuid is not None and str(row.uuid).strip()
    }
    return tuple(
        record for record in base_records
        if record.uuid is not None and str(record.uuid).strip() in matching_uuids
    )


def _static_indicator_payload(indicator_id: str, label: str, value: int) -> dict[str, object]:
    return {
        "id": indicator_id,
        "label": label,
        "definition": "",
        "unit": "personnes déclarées",
        "value": value,
        "status": "available",
        "breakdown": {},
    }


def _zero_indicator_payload(indicator_id: str, label: str) -> dict[str, object]:
    return _static_indicator_payload(indicator_id, label, 0)


def _iter_matching_blocks(records: tuple[RawQuestionnaireRecord, ...]):
    for record in records:
        prestations = record.prestations_json or {}
        for block in load_conditional_definitions(record.raw):
            state = prestations.get(block.source_block_id) or {}
            if isinstance(state, dict):
                yield record, block.source_block_name, state


def _infer_block_dispositif(block_name: str) -> str | None:
    if block_name == "Directes ORP CDAPH - ESRP" or block_name.startswith("Directes ORP CDAPH - Parcours accompagnement à visée certifiante -") or block_name.startswith("Directes ORP CDAPH - Parcours à visée socio-professionnelle -"):
        return "esrp"
    if block_name == "Directes ORP CDAPH - ESPO":
        return "espo"
    if block_name == "Directes ORP CDAPH - UEROS":
        return "ueros"
    return None


def _state_matches_selected_dispositifs(block_name: str, selected_dispositifs: set[str]) -> bool:
    if not selected_dispositifs:
        return True
    return _infer_block_dispositif(block_name) in selected_dispositifs


def _sum_file_active_for_block_names(
    records: tuple[RawQuestionnaireRecord, ...],
    *,
    exact_names: tuple[str, ...] = (),
    prefixes: tuple[str, ...] = (),
    selected_dispositifs: set[str],
) -> int:
    total = 0
    for _, block_name, state in _iter_matching_blocks(records):
        matches = block_name in exact_names or any(block_name.startswith(prefix) for prefix in prefixes)
        if not matches or not _state_matches_selected_dispositifs(block_name, selected_dispositifs):
            continue
        present_value = state.get("fileActive")
        exit_value = state.get("sorties")
        total += _normalize_non_negative_integer(present_value, "fileActive") if present_value not in (None, "") else 0
        total += _normalize_non_negative_integer(exit_value, "sorties") if exit_value not in (None, "") else 0
    return total


def _build_activity_detail_items(
    records: tuple[RawQuestionnaireRecord, ...],
    selected_dispositifs: set[str],
) -> list[dict[str, object]]:
    if selected_dispositifs and "esrp" not in selected_dispositifs:
        return []
    labels = (
        ("esrp_cert_formations", "Formations certifiantes", "Directes ORP CDAPH - Parcours accompagnement à visée certifiante - Formation certifiante ou diplômante - Sélection des formations"),
        ("esrp_cert_dfa", "Formation accompagnée certifiante DFA", "Directes ORP CDAPH - Parcours accompagnement à visée certifiante - Formation accompagnée certifiante (avec titre pro ou diplôme)"),
        ("esrp_prof", "Formation professionnalisante non certifiante", "Directes ORP CDAPH - Parcours accompagnement à visée certifiante - Formation professionnalisante (ne débouchant pas sur un diplôme)"),
        ("esrp_prof_dfa", "Formation accompagnée professionnalisante non certifiante DFA", "Directes ORP CDAPH - Parcours accompagnement à visée certifiante - Formation accompagnée professionnalisante (ne débouchant pas sur un diplôme)"),
        ("esrp_prep", "Parcours préparatoires", "Directes ORP CDAPH - Parcours accompagnement à visée certifiante - Préparer à accéder à une formation / remise à niveau savoirs de base"),
        ("esrp_fle", "FLE", "Directes ORP CDAPH - Parcours à visée socio-professionnelle - Apprentissage/maîtrise de la langue (FLE, alpha...)"),
        ("esrp_reentrainement", "Réentrainement au travail", "Directes ORP CDAPH - Parcours à visée socio-professionnelle - Réentrainement au travail"),
        ("esrp_projet", "Préparation du projet professionnel", "Directes ORP CDAPH - Parcours à visée socio-professionnelle - Préparation d'un projet professionnel (orientation hors ESPO)"),
        ("esrp_emploi", "Préparation à l’emploi", "Directes ORP CDAPH - Parcours à visée socio-professionnelle - Préparation à accéder à l'emploi (remobilisation, etc.)"),
    )
    return [
        {
            "id": item_id,
            "label": label,
            "value": _sum_file_active_for_block_names(
                records,
                exact_names=(block_name,),
                selected_dispositifs=selected_dispositifs,
            ),
            "unit": "personnes déclarées",
            "definition": "Sous-indicateur ESRP déclaratif, non additif avec les autres détails ESRP.",
        }
        for item_id, label, block_name in labels
    ]


def _build_hors_les_murs_item(
    records: tuple[RawQuestionnaireRecord, ...],
    selected_dispositifs: set[str],
) -> dict[str, object]:
    total = Decimal("0")
    for _, block_name, state in _iter_matching_blocks(records):
        if not _state_matches_selected_dispositifs(block_name, selected_dispositifs):
            continue
        direct_row = ((state.get("directAvecOrp") or {}).get("row")) if isinstance(state.get("directAvecOrp"), dict) else None
        if isinstance(direct_row, dict):
            total += _normalize_non_negative_decimal(direct_row.get("hors_murs_personnes"))
    return {
        "id": "support.outside_walls",
        "label": "Hors les murs",
        "value": _serialize_decimal(total),
        "unit": "personnes déclarées",
        "definition": "Somme des personnes accompagnées hors les murs déclarées dans les blocs directs.",
    }


def _build_information_actions_summary(records: tuple[RawQuestionnaireRecord, ...]) -> list[dict[str, object]]:
    counters = {name: Decimal("0") for name in (
        "personnes_collectives_journees",
        "personnes_collectives_total",
        "personnes_individuelles_heures",
        "partenaires_collectives_journees",
        "partenaires_collectives_total",
        "partenaires_individuelles_heures",
        "partenaires_individuelles_total",
        "organismes_collectives_journees",
        "organismes_collectives_total",
        "organismes_individuelles_heures",
        "organismes_individuelles_total",
    )}
    for _, block_name, state in _iter_matching_blocks(records):
        direct_rows = ((state.get("directSansOrp") or {}).get("rows")) if isinstance(state.get("directSansOrp"), dict) else None
        indirect_rows = ((state.get("indirect") or {}).get("rows")) if isinstance(state.get("indirect"), dict) else None
        if block_name == "Directes hors ORP CDAPH - Informations aux personnes" and isinstance(direct_rows, dict):
            collective = direct_rows.get("info_personnes_collectives") or {}
            counters["personnes_collectives_journees"] += _normalize_non_negative_decimal(collective.get("journees"))
            counters["personnes_collectives_total"] += (
                _normalize_non_negative_decimal(collective.get("boeth"))
                + _normalize_non_negative_decimal(collective.get("non_boeth"))
                + _normalize_non_negative_decimal(collective.get("sans_statut"))
            )
            individual = direct_rows.get("info_personnes_individuelles") or {}
            counters["personnes_individuelles_heures"] += _normalize_non_negative_decimal(individual.get("heures"))
        elif block_name == "Indirectes - Informations partenaires" and isinstance(indirect_rows, dict):
            collective = indirect_rows.get("part_collectives") or {}
            counters["partenaires_collectives_journees"] += _normalize_non_negative_decimal(collective.get("journees"))
            counters["partenaires_collectives_total"] += _normalize_non_negative_decimal(collective.get("partenaires_total"))
            individual = indirect_rows.get("part_individuelles") or {}
            counters["partenaires_individuelles_heures"] += _normalize_non_negative_decimal(individual.get("heures"))
            counters["partenaires_individuelles_total"] += _normalize_non_negative_decimal(individual.get("partenaires"))
        elif block_name == "Indirectes - Informations organisme de formation" and isinstance(indirect_rows, dict):
            collective = indirect_rows.get("of_collectives") or {}
            counters["organismes_collectives_journees"] += _normalize_non_negative_decimal(collective.get("journees"))
            counters["organismes_collectives_total"] += _normalize_non_negative_decimal(collective.get("partenaires_total"))
            individual = indirect_rows.get("of_individuelles") or {}
            counters["organismes_individuelles_heures"] += _normalize_non_negative_decimal(individual.get("heures"))
            counters["organismes_individuelles_total"] += _normalize_non_negative_decimal(individual.get("partenaires"))
    return [
        _detail_card_payload(
            "info_people",
            "Informations destinées aux personnes",
            "Unités exactes conservées : journées, personnes et heures ne sont pas additionnées entre elles.",
            [
                ("Journées d’information collectives", counters["personnes_collectives_journees"], "journées"),
                ("Personnes reçues en collectif", counters["personnes_collectives_total"], "personnes"),
                ("Information individuelle", counters["personnes_individuelles_heures"], "heures"),
            ],
        ),
        _detail_card_payload(
            "info_partners",
            "Informations destinées aux partenaires",
            "Les temps individuels sont exprimés en heures, faute de compteur de rendez-vous exploitable.",
            [
                ("Journées collectives", counters["partenaires_collectives_journees"], "journées"),
                ("Partenaires concernés en collectif", counters["partenaires_collectives_total"], "partenaires"),
                ("Information individuelle", counters["partenaires_individuelles_heures"], "heures"),
                ("Partenaires concernés en individuel", counters["partenaires_individuelles_total"], "partenaires"),
            ],
        ),
        _detail_card_payload(
            "info_training",
            "Informations destinées aux organismes de formation",
            "Les temps individuels sont exprimés en heures, faute de compteur de rendez-vous exploitable.",
            [
                ("Journées collectives", counters["organismes_collectives_journees"], "journées"),
                ("Organismes concernés en collectif", counters["organismes_collectives_total"], "organismes"),
                ("Information individuelle", counters["organismes_individuelles_heures"], "heures"),
                ("Organismes concernés en individuel", counters["organismes_individuelles_total"], "organismes"),
            ],
        ),
    ]


def _build_orienteurs_items(records: tuple[RawQuestionnaireRecord, ...]) -> list[dict[str, object]]:
    counters = {
        "pec": {"reseau_emploi": Decimal("0"), "mdph": Decimal("0"), "autres": Decimal("0")},
        "other": {"reseau_emploi": Decimal("0"), "mdph": Decimal("0"), "autres": Decimal("0")},
    }
    for _, block_name, state in _iter_matching_blocks(records):
        if block_name in {
            "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH",
            "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Sans ORP CDAPH",
        }:
            target = "pec"
        elif block_name in {
            "Directes hors ORP CDAPH - Évaluations professionnelles",
            "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH",
            "Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH",
        }:
            target = "other"
        else:
            continue
        orient = state.get("orienteursBloc") or {}
        if not isinstance(orient, dict):
            continue
        counters[target]["reseau_emploi"] += _normalize_non_negative_decimal(orient.get("reseau_emploi"))
        counters[target]["mdph"] += _normalize_non_negative_decimal(orient.get("mdph"))
        counters[target]["autres"] += (
            _normalize_non_negative_decimal(orient.get("autres"))
            + _normalize_non_negative_decimal(orient.get("demande_personnelle"))
            + _normalize_non_negative_decimal(orient.get("employeur_public"))
            + _normalize_non_negative_decimal(orient.get("employeur_prive"))
        )
    return [
        _detail_card_payload(
            "orienteurs_pec",
            "Orienteurs PEC",
            "Lecture regroupée en réseau pour l’emploi, MDPH et autres.",
            [
                ("Réseau pour l’emploi", counters["pec"]["reseau_emploi"], "orientations"),
                ("MDPH", counters["pec"]["mdph"], "orientations"),
                ("Autres", counters["pec"]["autres"], "orientations"),
            ],
        ),
        _detail_card_payload(
            "orienteurs_other",
            "Orienteurs autres dispositifs d’évaluation",
            "Lecture regroupée en réseau pour l’emploi, MDPH et autres.",
            [
                ("Réseau pour l’emploi", counters["other"]["reseau_emploi"], "orientations"),
                ("MDPH", counters["other"]["mdph"], "orientations"),
                ("Autres", counters["other"]["autres"], "orientations"),
            ],
        ),
    ]


def _collect_employment_counters(
    records: tuple[RawQuestionnaireRecord, ...],
    selected_dispositifs: set[str],
) -> dict[str, int]:
    counters = {key: 0 for key in (
        "emploi_sorties_n_1",
        "emploi_nb_repondants",
        "emploi_acces_nb",
        "emploi_presence_nb",
        "emploi_acces_cdi",
        "emploi_acces_cdd_plus6",
        "emploi_acces_cdd_moins6",
        "emploi_acces_alternance",
        "emploi_acces_interim",
        "emploi_acces_autre",
    )}
    for _, block_name, state in _iter_matching_blocks(records):
        if not _state_matches_selected_dispositifs(block_name, selected_dispositifs):
            continue
        direct_row = ((state.get("directAvecOrp") or {}).get("row")) if isinstance(state.get("directAvecOrp"), dict) else None
        if not isinstance(direct_row, dict):
            continue
        for key in counters:
            value = direct_row.get(key)
            if value not in (None, ""):
                counters[key] += _normalize_non_negative_integer(value, key)
    return counters


def _build_employment_items(counters: dict[str, int]) -> list[dict[str, object]]:
    return [
        _detail_card_payload(
            "employment_snapshot",
            "Volumes emploi déclarés",
            "Volumes bruts issus des questionnaires, utilisés comme numérateurs et dénominateurs des taux emploi.",
            [
                ("Sorties N-1 déclarées", counters["emploi_sorties_n_1"], "personnes"),
                ("Répondants emploi", counters["emploi_nb_repondants"], "personnes"),
                ("Accès à l’emploi", counters["emploi_acces_nb"], "personnes"),
                ("Toujours en emploi", counters["emploi_presence_nb"], "personnes"),
            ],
        ),
        _detail_card_payload(
            "employment_contracts",
            "Détail des contrats",
            "Les volumes sont déclaratifs et non transformés en taux.",
            [
                ("CDI", counters["emploi_acces_cdi"], "personnes"),
                ("CDD de plus de 6 mois", counters["emploi_acces_cdd_plus6"], "personnes"),
                ("CDD de moins de 6 mois", counters["emploi_acces_cdd_moins6"], "personnes"),
                ("Alternance", counters["emploi_acces_alternance"], "personnes"),
                ("Intérim", counters["emploi_acces_interim"], "personnes"),
                ("Autres", counters["emploi_acces_autre"], "personnes"),
            ],
        ),
    ]


def _build_employment_rate_card(
    item_id: str,
    label: str,
    numerator: int,
    denominator: int,
    definition: str,
) -> dict[str, object]:
    rate = Decimal("0")
    if denominator > 0:
        rate = ((Decimal(numerator) * Decimal("100")) / Decimal(denominator)).quantize(Decimal("0.1"))
    return {
        "id": item_id,
        "label": label,
        "definition": definition,
        "unit": "%",
        "value": _serialize_decimal(rate),
        "status": "available",
        "children": [
            {"label": "Numérateur", "value": numerator, "unit": "personnes"},
            {"label": "Dénominateur", "value": denominator, "unit": "personnes"},
        ],
    }


def _build_preconisation_items(
    records: tuple[RawQuestionnaireRecord, ...],
    selected_dispositifs: set[str],
) -> list[dict[str, object]]:
    counters = {"espo": {}, "ueros": {}}
    for _, block_name, state in _iter_matching_blocks(records):
        if not _state_matches_selected_dispositifs(block_name, selected_dispositifs):
            continue
        if block_name == "Directes ORP CDAPH - ESPO":
            target = "espo"
        elif block_name == "Directes ORP CDAPH - UEROS":
            target = "ueros"
        else:
            continue
        block = state.get("preconisationsBloc") or {}
        if not isinstance(block, dict):
            continue
        for key, value in block.items():
            if key.endswith("_precision") or value in (None, ""):
                continue
            counters[target][key] = counters[target].get(key, 0) + _normalize_non_negative_integer(value, key)
    return [
        _detail_card_payload(
            "precon_espo",
            "Préconisations à l’issue de l’ESPO",
            "Catégories structurées lues directement dans le JSON.",
            [(_humanize_preconisation_key(key), value, "préconisations") for key, value in sorted(counters["espo"].items(), key=lambda item: (-item[1], item[0]))],
        ),
        _detail_card_payload(
            "precon_ueros",
            "Préconisations à l’issue des UEROS",
            "Catégories structurées lues directement dans le JSON.",
            [(_humanize_preconisation_key(key), value, "préconisations") for key, value in sorted(counters["ueros"].items(), key=lambda item: (-item[1], item[0]))],
        ),
    ]


def _detail_card_payload(
    item_id: str,
    label: str,
    definition: str,
    children: list[tuple[str, Decimal | int | float, str]],
) -> dict[str, object]:
    return {
        "id": item_id,
        "label": label,
        "definition": definition,
        "children": [
            {"label": child_label, "value": _serialize_decimal(value), "unit": unit}
            for child_label, value, unit in children
            if _serialize_decimal(value) not in (None, 0, 0.0)
        ],
    }


def _humanize_preconisation_key(value: str) -> str:
    mapping = {
        "emploi_milieu_ordinaire": "Emploi en milieu ordinaire",
        "entreprise_adaptee": "Entreprise adaptée",
        "esat": "ESAT",
        "creation_entreprise": "Création d’entreprise",
        "maintien_emploi": "Maintien dans l’emploi",
        "formation_droit_commun": "Formation de droit commun",
        "formation_alternance": "Formation en alternance",
        "formation_esrp_dfa": "Formation ESRP / DFA",
        "espo_specialisee_ueros": "ESPO spécialisée / UEROS",
        "service_accompagnement_social": "Service d’accompagnement social",
        "vie_sociale": "Vie sociale",
        "soins": "Soins",
        "emploi_accompagne": "Emploi accompagné",
        "autres": "Autres",
        "droit_commun": "Droit commun",
        "sante_social": "Santé / social",
        "readaptation_professionnelle": "Réadaptation professionnelle",
        "readaptation_ueros": "Réadaptation UEROS",
        "readaptation_espo": "Réadaptation ESPO",
        "readaptation_esrp": "Réadaptation ESRP",
        "readaptation_dfa": "Réadaptation DFA",
        "inconnu": "Inconnu",
    }
    return mapping.get(value, value.replace("_", " ").capitalize())


def _normalize_non_negative_decimal(value: object) -> Decimal:
    if value in (None, ""):
        return Decimal("0")
    if isinstance(value, bool):
        raise DataQualityError("Boolean values are not accepted")
    if isinstance(value, int):
        if value < 0:
            raise DataQualityError("Negative values are not accepted")
        return Decimal(value)
    text = str(value).strip().replace(",", ".")
    if not text:
        return Decimal("0")
    try:
        parsed = Decimal(text)
    except InvalidOperation as exc:
        raise DataQualityError("Invalid decimal value") from exc
    if parsed < 0:
        raise DataQualityError("Negative values are not accepted")
    return parsed


def _serialize_decimal(value: Decimal | int | float | None) -> int | float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    return value
