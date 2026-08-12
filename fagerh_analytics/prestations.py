"""Deterministic extraction rules for FAGERH prestations JSON blocks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .domain import EvaluationActivityRecord, QuestionnaireRecord, RawQuestionnaireRecord


@dataclass(frozen=True)
class ConditionalBlockDefinition:
    source_block_id: str
    source_block_name: str


@dataclass(frozen=True)
class DeviceVolumeDefinition:
    dispositif: str
    block_label: str
    source_path: str
    indicator_id: str
    grain: str = "campaign_year+finess_main+dispositif"
    expected_type: str = "integer"


@dataclass(frozen=True)
class EvaluationVolumeDefinition:
    evaluation_type: str
    evaluation_detail: str
    block_label: str
    orientation_cdaph: str
    source_path: str


@dataclass(frozen=True)
class ExtractedScalarValue:
    source_block_id: str
    source_block_name: str
    source_path: str
    state: str
    value: int | None
    raw_value: object | None


DEVICE_VOLUME_DEFINITIONS: tuple[DeviceVolumeDefinition, ...] = (
    DeviceVolumeDefinition("esrp", "Directes ORP CDAPH - ESRP", "fileActive+sorties", "people.received.esrp"),
    DeviceVolumeDefinition("espo", "Directes ORP CDAPH - ESPO", "fileActive+sorties", "people.received.espo"),
    DeviceVolumeDefinition("ueros", "Directes ORP CDAPH - UEROS", "fileActive+sorties", "people.received.ueros"),
    DeviceVolumeDefinition("deac", "Directes ORP CDAPH - DEAc", "fileActive+sorties", "people.received.deac"),
)

OTHER_EVAL_DEFINITIONS: tuple[EvaluationVolumeDefinition, ...] = (
    EvaluationVolumeDefinition(
        "other_eval",
        "professional_assessment",
        "Directes hors ORP CDAPH - Évaluations professionnelles",
        "sans_orp_cdaph",
        "directSansOrp.rows.pec.beneficiaires",
    ),
    EvaluationVolumeDefinition(
        "other_eval",
        "without_orp_cdaph",
        "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH",
        "sans_orp_cdaph",
        "fileActive",
    ),
    EvaluationVolumeDefinition(
        "other_eval",
        "with_orp_cdaph",
        "Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH",
        "avec_orp_cdaph",
        "fileActive",
    ),
)

PEC_DEFINITIONS: tuple[EvaluationVolumeDefinition, ...] = (
    EvaluationVolumeDefinition(
        "pec",
        "pec",
        "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH",
        "avec_orp_cdaph",
        "fileActive",
    ),
    EvaluationVolumeDefinition(
        "pec",
        "pec",
        "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Sans ORP CDAPH",
        "sans_orp_cdaph",
        "fileActive",
    ),
    EvaluationVolumeDefinition(
        "pec",
        "pec",
        "Directes hors ORP CDAPH - PEC",
        "sans_orp_cdaph",
        "directSansOrp.rows.pec.beneficiaires",
    ),
)

ALL_EVALUATION_DEFINITIONS = PEC_DEFINITIONS + OTHER_EVAL_DEFINITIONS


def load_conditional_definitions(raw_fields: dict[str, Any]) -> tuple[ConditionalBlockDefinition, ...]:
    details = _coerce_json_object(raw_fields.get("prestations_details_json"))
    snapshot = details.get("__wizard_v3_state")
    if not isinstance(snapshot, dict):
        return tuple()
    runtime = snapshot.get("runtime")
    if not isinstance(runtime, dict):
        return tuple()
    conditional_defs = runtime.get("conditionalDefs")
    if not isinstance(conditional_defs, list):
        return tuple()
    definitions: list[ConditionalBlockDefinition] = []
    for item in conditional_defs:
        if not isinstance(item, dict):
            continue
        source_block_id = str(item.get("id") or "").strip()
        source_block_name = str(item.get("name") or "").strip()
        if not source_block_id or not source_block_name:
            continue
        definitions.append(ConditionalBlockDefinition(source_block_id, source_block_name))
    return tuple(definitions)


def extract_device_volume_candidates(
    raw_record: RawQuestionnaireRecord,
    definition: DeviceVolumeDefinition,
    *,
    normalize_integer: Any,
) -> tuple[ExtractedScalarValue, ...]:
    prestations = raw_record.prestations_json or {}
    definitions = load_conditional_definitions(raw_record.raw)
    extracted: list[ExtractedScalarValue] = []
    for block in definitions:
        if block.source_block_name != definition.block_label:
            continue
        state = prestations.get(block.source_block_id)
        extracted.append(
            _extract_scalar_value(
                state=state,
                source_block_id=block.source_block_id,
                source_block_name=block.source_block_name,
                source_path=definition.source_path,
                normalize_integer=normalize_integer,
            )
        )
    return tuple(extracted)


def resolve_device_volume(
    raw_record: RawQuestionnaireRecord,
    definition: DeviceVolumeDefinition,
    *,
    flat_value: object,
    flat_field_name: str,
    normalize_integer: Any,
    quality_error_cls: type[Exception],
) -> tuple[int, dict[str, object]]:
    candidates = extract_device_volume_candidates(
        raw_record,
        definition,
        normalize_integer=normalize_integer,
    )
    explicit = [item for item in candidates if item.state in {"positive", "zero", "empty_string"}]
    if explicit:
        positive_or_zero = [item for item in explicit if item.state in {"positive", "zero"}]
        if positive_or_zero:
            distinct_values = {item.value for item in positive_or_zero}
            if len(distinct_values) > 1:
                raise quality_error_cls(
                    f"Contradictory JSON values for {definition.dispositif}: "
                    f"{sorted(value for value in distinct_values if value is not None)}"
                )
            chosen = positive_or_zero[0]
            flat_normalized = normalize_integer(flat_value, field_name=flat_field_name)
            conflict = flat_normalized > 0 and flat_normalized != (chosen.value or 0)
            return chosen.value or 0, {
                "source_type": "prestations_json",
                "source_block_id": chosen.source_block_id,
                "source_block_name": chosen.source_block_name,
                "source_path": chosen.source_path,
                "state": chosen.state,
                "fallback_used": False,
                "flat_conflict": conflict,
            }
        return 0, {
            "source_type": "prestations_json",
            "source_block_id": explicit[0].source_block_id,
            "source_block_name": explicit[0].source_block_name,
            "source_path": explicit[0].source_path,
            "state": explicit[0].state,
            "fallback_used": False,
            "flat_conflict": False,
        }

    fallback_value = normalize_integer(flat_value, field_name=flat_field_name)
    return fallback_value, {
        "source_type": "flat_fallback",
        "source_block_id": None,
        "source_block_name": None,
        "source_path": flat_field_name,
        "state": "fallback",
        "fallback_used": True,
        "flat_conflict": False,
    }


def project_received_people_records(
    raw_record: RawQuestionnaireRecord,
    *,
    normalize_integer: Any,
    quality_error_cls: type[Exception],
) -> tuple[QuestionnaireRecord, ...]:
    projected: list[QuestionnaireRecord] = []
    active_dispositifs = _get_active_dispositifs(raw_record)
    for definition in DEVICE_VOLUME_DEFINITIONS:
        flat_field_name = f"q53_accompagnes__{definition.dispositif}"
        value, meta = resolve_device_volume(
            raw_record,
            definition,
            flat_value=getattr(raw_record, flat_field_name),
            flat_field_name=flat_field_name,
            normalize_integer=normalize_integer,
            quality_error_cls=quality_error_cls,
        )
        if meta["fallback_used"]:
            if value > 0 and definition.dispositif not in active_dispositifs:
                raise quality_error_cls(
                    "Inconsistent annual people received values: logical dispositif "
                    f"{','.join(active_dispositifs) or '<none>'} cannot carry a positive value in {flat_field_name}"
                )
            if value == 0 and definition.dispositif not in active_dispositifs:
                continue
        projected.append(
            QuestionnaireRecord(
                uuid=raw_record.uuid,
                campaign_year=raw_record.campaign_year,
                region_code=raw_record.region_code,
                department_code=raw_record.department_code,
                finess_main=raw_record.finess_main,
                completion_status=raw_record.completion_status,
                dispositif=definition.dispositif,
                q53_accompagnes__esrp=value if definition.dispositif == "esrp" else 0,
                q53_accompagnes__espo=value if definition.dispositif == "espo" else 0,
                q53_accompagnes__ueros=value if definition.dispositif == "ueros" else 0,
                q53_accompagnes__deac=value if definition.dispositif == "deac" else 0,
                raw={**raw_record.raw, "_analytics_device_volume": meta},
            )
        )
    return tuple(projected)


def project_evaluation_activities(
    raw_record: RawQuestionnaireRecord,
    *,
    normalize_integer: Any,
    quality_error_cls: type[Exception],
) -> tuple[EvaluationActivityRecord, ...]:
    definitions_by_name = {item.block_label: item for item in ALL_EVALUATION_DEFINITIONS}
    prestations = raw_record.prestations_json or {}
    projected_rows: list[EvaluationActivityRecord] = []
    for block in load_conditional_definitions(raw_record.raw):
        definition = definitions_by_name.get(block.source_block_name)
        if definition is None:
            continue
        state = prestations.get(block.source_block_id)
        extracted = _extract_scalar_value(
            state=state,
            source_block_id=block.source_block_id,
            source_block_name=block.source_block_name,
            source_path=definition.source_path,
            normalize_integer=normalize_integer,
        )
        projected_rows.append(
            EvaluationActivityRecord(
                uuid=raw_record.uuid,
                campaign_year=raw_record.campaign_year,
                region_code=raw_record.region_code,
                department_code=raw_record.department_code,
                finess_main=raw_record.finess_main,
                completion_status=raw_record.completion_status,
                evaluation_type=definition.evaluation_type,
                evaluation_detail=definition.evaluation_detail,
                orientation_cdaph=definition.orientation_cdaph,
                declared_volume=extracted.value or 0,
                source_block_id=block.source_block_id,
                source_block_name=block.source_block_name,
                source_path=definition.source_path,
                raw=raw_record.raw,
            )
        )
    return tuple(projected_rows)


def _extract_scalar_value(
    *,
    state: dict[str, Any] | None,
    source_block_id: str,
    source_block_name: str,
    source_path: str,
    normalize_integer: Any,
) -> ExtractedScalarValue:
    if source_path == "fileActive":
        raw_value = state.get("fileActive") if isinstance(state, dict) else None
    elif source_path == "fileActive+sorties":
        if not isinstance(state, dict):
            raw_value = None
        else:
            presents = state.get("fileActive")
            exits = state.get("sorties")
            if presents is None and exits is None:
                raw_value = None
            elif all(value is None or (isinstance(value, str) and not value.strip()) for value in (presents, exits)):
                raw_value = ""
            else:
                present_value = normalize_integer(
                    presents,
                    field_name=f"{source_block_name}.fileActive",
                )
                exit_value = normalize_integer(
                    exits,
                    field_name=f"{source_block_name}.sorties",
                )
                raw_value = present_value + exit_value
    elif source_path == "directSansOrp.rows.pec.beneficiaires":
        raw_value = ((((state or {}).get("directSansOrp") or {}).get("rows") or {}).get("pec") or {}).get("beneficiaires")
    else:
        raise ValueError(f"Unsupported prestations source path: {source_path}")

    if raw_value is None:
        return ExtractedScalarValue(source_block_id, source_block_name, source_path, "absent", None, None)
    if isinstance(raw_value, str) and not raw_value.strip():
        return ExtractedScalarValue(source_block_id, source_block_name, source_path, "empty_string", None, raw_value)
    value = normalize_integer(raw_value, field_name=f"{source_block_name}.{source_path}")
    state_name = "positive" if value > 0 else "zero"
    return ExtractedScalarValue(source_block_id, source_block_name, source_path, state_name, value, raw_value)


def _coerce_json_object(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if not isinstance(value, str):
        return {}
    normalized = value.strip()
    if not normalized:
        return {}
    parsed = json.loads(normalized)
    return parsed if isinstance(parsed, dict) else {}


def _get_active_dispositifs(raw_record: RawQuestionnaireRecord) -> tuple[str, ...]:
    active: list[str] = []
    for dispositif in ("esrp", "espo", "ueros", "deac"):
        if _coerce_flag(getattr(raw_record, f"check_{dispositif}", None)):
            active.append(dispositif)
    return tuple(active)


def _coerce_flag(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "vrai", "oui", "yes"}
    return False
