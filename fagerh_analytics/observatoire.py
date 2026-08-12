"""Regional observatory aggregates used by the FAGERH admin report."""

from __future__ import annotations

from collections import Counter
from decimal import Decimal
import json
import unicodedata
from typing import Any

from .geography import get_region_label


AGE_LABELS = ("16-17", "18-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60+", "Inconnu")
AGE_MIDPOINTS = (16.5, 18.5, 22.0, 27.0, 32.0, 37.0, 42.0, 47.0, 52.0, 57.0, 62.5)
LEVEL_LABELS = ("Niveau 2", "Niveau 3", "Niveau 4", "Niveau 5", "Niveau 6", "Niveau 7", "Inconnu")
HANDICAP_LABELS = (
    "Déficiences intellectuelles", "Autisme et autres TED", "Troubles psychiques",
    "Troubles du langage et des apprentissages", "Déficiences auditives",
    "Déficiences visuelles", "Déficiences motrices",
    "Déficiences métaboliques et nutritionnelles", "Cérébro-lésions",
    "Polyhandicap", "Troubles du comportement", "Diagnostics en cours",
    "Autres déficiences", "Inconnu",
)


def build_regional_observatory(
    repository,
    region_code: str,
    completion_scope: str = "completed",
) -> dict[str, object]:
    """Build the report-only indicators for one geography and completion scope."""
    code = str(region_code or "").strip()
    if not code:
        raise ValueError("Une région doit être sélectionnée.")
    is_france = code.lower() == "france"
    scope = str(completion_scope or "completed").strip().lower()
    if scope not in {"all", "completed", "in_progress"}:
        raise ValueError("Le périmètre des questionnaires est invalide.")

    records = [
        record for record in repository.list_raw_questionnaires()
        if (is_france or record.region_code == code)
        and (
            scope == "all"
            or (scope == "completed" and record.completion_status == "completed")
            or (scope == "in_progress" and record.completion_status == "in_progress")
        )
    ]
    ages = [0.0] * len(AGE_LABELS)
    levels = [0.0] * len(LEVEL_LABELS)
    handicaps = [0.0] * len(HANDICAP_LABELS)
    services = Counter()
    accommodation = Counter()
    accommodation_reported = Counter()
    health_support = Counter()
    institutional_network: dict[str, Counter] = {
        field_name: Counter()
        for field_name in ("q45_cpts", "q46_cpt", "q47_clsm", "q48_cle", "q49_cre", "q50_fiphfp", "q51_plith")
    }

    for record in records:
        raw = record.raw or {}
        for device in ("esrp", "espo", "ueros", "deac"):
            if _is_true(raw.get(f"check_{device}")):
                services[device] += 1
        _collect_health_support(raw.get("metiers_json"), health_support)
        for field_name, counters in institutional_network.items():
            counters[_committee_status(_committee_value(record, field_name))] += 1
        state = _conditional_state(record.prestations_details_json or {})
        for block_id, block in state.items():
            if not isinstance(block, dict):
                continue
            device = _device_from_block_id(str(block_id))
            if device is None:
                continue
            cohort = block.get("coh") if isinstance(block.get("coh"), dict) else {}
            ages = _add(ages, _numbers(cohort.get("age"), len(AGE_LABELS)))
            levels = _add(levels, _numbers(cohort.get("niveau_entree"), len(LEVEL_LABELS)))
            matrix = block.get("handicapMatrix")
            if isinstance(matrix, list):
                principal = [
                    _number(matrix[index].get("principal"))
                    if index < len(matrix) and isinstance(matrix[index], dict) else 0.0
                    for index in range(len(HANDICAP_LABELS))
                ]
                handicaps = _add(handicaps, principal)
            direct = block.get("directAvecOrp")
            direct_row = direct.get("row") if isinstance(direct, dict) else None
            if isinstance(direct_row, dict):
                for output_key, source_key in (
                    ("people", "hebergees_personnes"),
                    ("days", "hebergees_journees"),
                    ("nights", "hebergees_nuitees"),
                ):
                    raw_value = direct_row.get(source_key)
                    numeric_value = _number(raw_value)
                    accommodation[output_key] += numeric_value
                    if numeric_value > 0:
                        accommodation_reported[output_key] += 1

    known_age = sum(ages[:-1])
    estimated_age = (
        sum(value * midpoint for value, midpoint in zip(ages[:-1], AGE_MIDPOINTS)) / known_age
        if known_age else None
    )
    known_levels = sum(levels[:-1])
    known_handicaps = sum(handicaps[:-1])

    return {
        "region": {
            "code": "france" if is_france else code,
            "label": "France entière" if is_france else get_region_label(code),
        },
        "methodology": {
            "scope": {
                "completed": "Questionnaires terminés uniquement, sans extrapolation des réponses incomplètes.",
                "in_progress": "Questionnaires non terminés uniquement. Les résultats sont provisoires et peuvent être incomplets.",
                "all": "Tous les questionnaires. Les résultats mélangent réponses terminées et non terminées.",
            }[scope],
            "age": "Moyenne pondérée par milieux de tranches ; 60+ représenté par 62,5 ans ; inconnus exclus.",
        },
        "completion_scope": scope,
        "completion_scope_label": {
            "completed": "Questionnaires terminés",
            "in_progress": "Questionnaires non terminés",
            "all": "Tous les questionnaires",
        }[scope],
        "questionnaire_count": len(records),
        "questionnaires_completed": sum(1 for record in records if record.completion_status == "completed"),
        "questionnaires_in_progress": sum(1 for record in records if record.completion_status == "in_progress"),
        "declared_services": dict(services),
        "age": {
            "labels": list(AGE_LABELS),
            "counts": [_rounded(value) for value in ages],
            "known_count": _rounded(known_age),
            "unknown_count": _rounded(ages[-1]),
            "estimated_mean": round(estimated_age, 1) if estimated_age is not None else None,
        },
        "education": {
            "labels": list(LEVEL_LABELS),
            "counts": [_rounded(value) for value in levels],
            "known_count": _rounded(known_levels),
            "level_4_or_less_rate": round(sum(levels[:3]) / known_levels, 4) if known_levels else None,
        },
        "main_disability": {
            "labels": list(HANDICAP_LABELS),
            "counts": [_rounded(value) for value in handicaps],
            "known_count": _rounded(known_handicaps),
            "rates": [round(value / known_handicaps, 4) if known_handicaps else None for value in handicaps],
        },
        "accommodation": {
            "people": _rounded(accommodation["people"]) if accommodation_reported["people"] else None,
            "days": _rounded(accommodation["days"]) if accommodation_reported["days"] else None,
            "nights": _rounded(accommodation["nights"]) if accommodation_reported["nights"] else None,
            "reported_counts": dict(accommodation_reported),
            "status": "partially_available" if accommodation_reported["people"] else "not_reported",
            "message": "Les personnes hébergées sont renseignées ; les journées et nuitées ne le sont pas dans la campagne 2025."
            if accommodation_reported["people"] and not accommodation_reported["days"] and not accommodation_reported["nights"]
            else None,
        },
        "health_support": {
            "unit": "ETP déclarés",
            "method": "Somme des ETP internes et externes de metiers_json, regroupés selon les familles du PDF.",
            "categories": [
                {"id": key, "label": label, "value": _rounded(float(health_support[key]))}
                for key, label in HEALTH_SUPPORT_CATEGORIES
            ],
        },
        "institutional_network": {
            "unit": "établissements et services répondants",
            "items": [
                {
                    "id": field_name,
                    "label": INSTITUTION_LABELS[field_name],
                    "direct": counters["direct"],
                    "represented": counters["represented"],
                    "no": counters["no"],
                    "unknown": counters["unknown"],
                }
                for field_name, counters in institutional_network.items()
            ],
        },
        "unavailable_indicators": [
            {
                "id": "exam_results",
                "label": "Résultats aux examens",
                "reason": "La source 2025 ne fournit pas encore une ventilation régionale fiabilisée exploitable.",
            },
        ],
    }


HEALTH_SUPPORT_CATEGORIES = (
    ("nursing", "Accompagnement à la santé - infirmiers"),
    ("multidisciplinary", "Appuis pluridisciplinaires"),
    ("social", "Accompagnement social"),
    ("psychology", "Accompagnement psychologique"),
    ("medical", "Accompagnement à la santé - médecins"),
    ("adapted_physical_activity", "Activités physiques adaptées"),
    ("occupational_therapy", "Ergothérapie"),
    ("social_animation", "Animation sociale"),
)

INSTITUTION_LABELS = {
    "q45_cpts": "CPTS",
    "q46_cpt": "Communauté psychiatrique de territoire",
    "q47_clsm": "Conseil local de santé mentale",
    "q48_cle": "Comité local pour l’emploi",
    "q49_cre": "Comité régional pour l’emploi",
    "q50_fiphfp": "Comité local FIPHFP",
    "q51_plith": "PRITH / PLITH",
}

INSTITUTION_SNAPSHOT_NAMES = {
    "q45_cpts": "ctx-q45",
    "q46_cpt": "ctx-q46",
    "q47_clsm": "ctx-q47",
    "q48_cle": "ctx-q48",
    "q49_cre": "ctx-q49",
    "q50_fiphfp": "ctx-q50",
    "q51_plith": "ctx-q51",
}


def _conditional_state(details: dict[str, Any]) -> dict[str, Any]:
    state = details.get("__wizard_v3_state")
    runtime = state.get("runtime") if isinstance(state, dict) else None
    value = runtime.get("conditionalState") if isinstance(runtime, dict) else None
    return value if isinstance(value, dict) else {}


def _device_from_block_id(block_id: str) -> str | None:
    prefix = "directes-orp-cdaph-"
    if not block_id.startswith(prefix):
        return None
    device = block_id[len(prefix):].split("-", 1)[0]
    return device if device in {"esrp", "espo", "ueros"} else None


def _number(value: Any) -> float:
    if value in (None, "", False):
        return 0.0
    try:
        return max(0.0, float(str(value).replace(",", ".")))
    except (TypeError, ValueError):
        return 0.0


def _numbers(values: Any, size: int) -> list[float]:
    source = values if isinstance(values, list) else []
    return [_number(source[index]) if index < len(source) else 0.0 for index in range(size)]


def _add(left: list[float], right: list[float]) -> list[float]:
    return [a + b for a, b in zip(left, right)]


def _is_true(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "oui", "yes"}


def _collect_health_support(raw_value: Any, counters: Counter) -> None:
    rows = raw_value
    if isinstance(raw_value, str):
        try:
            rows = json.loads(raw_value)
        except json.JSONDecodeError:
            return
    if not isinstance(rows, list):
        return
    for row in rows:
        if not isinstance(row, dict):
            continue
        category = _health_category(row.get("metier"))
        if category is None:
            continue
        value = _number(row.get("etp"))
        if row.get("etp") in (None, ""):
            value = _number(row.get("etpCdi")) + _number(row.get("etpCdd"))
        counters[category] += Decimal(str(value))


def _health_category(label: Any) -> str | None:
    normalized = _normalize_text(label)
    if any(term in normalized for term in ("infirm", "ide")):
        return "nursing"
    if any(term in normalized for term in ("psychologue", "neuropsych")):
        return "psychology"
    if any(term in normalized for term in ("medecin", "psychiatre")):
        return "medical"
    if any(term in normalized for term in ("activite physique", "enseignant apa", "sport adapte")):
        return "adapted_physical_activity"
    if "ergotherap" in normalized:
        return "occupational_therapy"
    if any(term in normalized for term in ("assistant social", "assistante sociale", "cesf", "conseiller en economie sociale")):
        return "social"
    if any(term in normalized for term in ("animateur", "animation", "educateur")):
        return "social_animation"
    if any(term in normalized for term in ("coordonn", "referent de parcours", "synthese")):
        return "multidisciplinary"
    return None


def _committee_status(value: Any) -> str:
    normalized = _normalize_text(value)
    if not normalized:
        return "unknown"
    if normalized == "oui":
        return "direct"
    if normalized.startswith("non") and "fagerh" in normalized:
        return "represented"
    if normalized == "non":
        return "no"
    return "unknown"


def _committee_value(record: Any, field_name: str) -> Any:
    raw_value = (record.raw or {}).get(field_name)
    if str(raw_value or "").strip():
        return raw_value
    state = (record.prestations_details_json or {}).get("__wizard_v3_state")
    controls = state.get("controls") if isinstance(state, dict) else None
    by_name = controls.get("byName") if isinstance(controls, dict) else None
    snapshot = by_name.get(INSTITUTION_SNAPSHOT_NAMES[field_name]) if isinstance(by_name, dict) else None
    return snapshot.get("value") if isinstance(snapshot, dict) else None


def _normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.lower().strip().split())


def _rounded(value: float) -> int | float:
    return int(value) if float(value).is_integer() else round(value, 2)
