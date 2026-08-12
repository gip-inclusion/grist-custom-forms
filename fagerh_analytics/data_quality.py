"""Read-only data quality diagnostics for FAGERH analytics."""

from __future__ import annotations

from dataclasses import dataclass

from .domain import RawQuestionnaireRecord, UserContext
from .finess import diagnose_finess, normalize_finess
from .geography import normalize_department_code, resolve_region_code
from .permissions import get_scope


@dataclass(frozen=True)
class DataQualityIssue:
    """Aggregated, non-sensitive data quality issue."""

    code: str
    severity: str
    field: str
    record_count: int
    message: str
    impact: str
    action_required: str
    distinct_value_count: int = 0
    masked_examples: tuple[str, ...] = ()
    sample_values: tuple[str, ...] = ()


@dataclass(frozen=True)
class DataQualitySummary:
    """Aggregated diagnostics visible to the current analytical scope."""

    analyzed_questionnaires: int
    issue_count: int
    affected_record_count: int
    invalid_finess_count: int
    unknown_department_count: int
    unresolved_region_count: int
    global_level: str
    warnings: tuple[str, ...] = ()
    issues: tuple[DataQualityIssue, ...] = ()


def analyze_data_quality(
    records: list[RawQuestionnaireRecord] | tuple[RawQuestionnaireRecord, ...],
    user_context: UserContext | None,
) -> DataQualitySummary:
    """Analyze raw questionnaire records without modifying any value."""

    scope = get_scope(user_context)
    visible_records = [record for record in records if _record_is_visible(record, scope)]
    visible_uuids = {
        _normalize_uuid(record.uuid)
        for record in visible_records
        if _normalize_uuid(record.uuid) is not None
    }
    invalid_finess_records: list[tuple[RawQuestionnaireRecord, str | None, str]] = []
    missing_finess_records: list[tuple[RawQuestionnaireRecord, str | None, str]] = []
    normalized_finess_records: list[tuple[RawQuestionnaireRecord, str, str]] = []
    unknown_department_records: list[tuple[RawQuestionnaireRecord, str]] = []
    unresolved_region_records: list[tuple[RawQuestionnaireRecord, str]] = []

    for record in visible_records:
        raw_finess = _extract_raw_finess(record)
        diagnostic = diagnose_finess(raw_finess)
        if diagnostic.issue_code == "invalid_finess":
            invalid_finess_records.append((record, raw_finess, diagnostic.detail or "invalid"))
        elif diagnostic.issue_code == "missing_finess":
            missing_finess_records.append((record, raw_finess, diagnostic.detail or "empty"))
        elif diagnostic.issue_code == "normalized_finess" and diagnostic.normalized is not None:
            normalized_finess_records.append((record, raw_finess or "", diagnostic.normalized))

        raw_department = _extract_raw_department(record)
        if raw_department is None:
            continue
        normalized_department = normalize_department_code(raw_department)
        region_code = resolve_region_code(normalized_department)
        if normalized_department is None or region_code is None:
            unknown_department_records.append((record, raw_department))
        if region_code is None:
            unresolved_region_records.append((record, raw_department))

    issues: list[DataQualityIssue] = []
    affected_uuids: set[str] = set()

    if normalized_finess_records:
        affected_uuids.update(
            normalized_uuid
            for normalized_uuid in (_normalize_uuid(record.uuid) for record, _, _ in normalized_finess_records)
            if normalized_uuid is not None
        )
        distinct_values = _distinct_preserving_order(raw_finess for _, raw_finess, _ in normalized_finess_records)
        issues.append(DataQualityIssue(
            code="normalized_finess",
            severity="warning",
            field="finess_main",
            record_count=len(normalized_finess_records),
            distinct_value_count=len(distinct_values),
            masked_examples=tuple(
                masked
                for masked in (_mask_finess(value) for value in distinct_values)
                if masked is not None
            )[:5],
            message="Certains FINESS ont été normalisés dans Analytics par ajout d’un zéro initial.",
            impact="Les résultats Analytics utilisent une valeur canonique à 9 chiffres sans modifier la donnée source Grist.",
            action_required="Conserver cette normalisation dans Analytics ; corriger la source uniquement si le métier le demande ailleurs.",
        ))

    if missing_finess_records:
        affected_uuids.update(
            normalized_uuid
            for normalized_uuid in (_normalize_uuid(record.uuid) for record, _, _ in missing_finess_records)
            if normalized_uuid is not None
        )
        issues.append(DataQualityIssue(
            code="missing_finess",
            severity="error",
            field="finess_main",
            record_count=len(missing_finess_records),
            distinct_value_count=1,
            message="Certains questionnaires n’ont aucun FINESS renseigné.",
            impact="Les regroupements par établissement et certains filtres FINESS restent incomplets.",
            action_required="Renseigner un FINESS valide à la source avec validation humaine.",
        ))

    if invalid_finess_records:
        affected_uuids.update(
            normalized_uuid
            for normalized_uuid in (_normalize_uuid(record.uuid) for record, _, _ in invalid_finess_records)
            if normalized_uuid is not None
        )
        distinct_values = _distinct_preserving_order(raw_finess for _, raw_finess, _ in invalid_finess_records)
        issues.append(DataQualityIssue(
            code="invalid_finess",
            severity="error",
            field="finess_main",
            record_count=len(invalid_finess_records),
            distinct_value_count=len(distinct_values),
            masked_examples=tuple(
                masked
                for masked in (_mask_finess(value) for value in distinct_values)
                if masked is not None
            )[:5],
            message="Certains identifiants FINESS ne respectent pas le format attendu.",
            impact="Les résultats nationaux restent disponibles, mais les filtres par établissement et les regroupements par FINESS peuvent être incomplets.",
            action_required="Corriger les FINESS à la source dans le formulaire ou la colonne Grist, avec validation humaine.",
        ))

    if unknown_department_records:
        affected_uuids.update(
            normalized_uuid
            for normalized_uuid in (_normalize_uuid(record.uuid) for record, _ in unknown_department_records)
            if normalized_uuid is not None
        )
        distinct_values = _distinct_preserving_order(raw_department for _, raw_department in unknown_department_records)
        issues.append(DataQualityIssue(
            code="unknown_department",
            severity="error",
            field="es_departement",
            record_count=len(unknown_department_records),
            distinct_value_count=len(distinct_values),
            sample_values=tuple(str(value) for value in distinct_values[:5]),
            message="Un code département ne correspond pas au format ou au référentiel attendu.",
            impact="Les totaux nationaux restent disponibles, mais certaines ventilations départementales et régionales peuvent être incomplètes.",
            action_required="Corriger la valeur du département dans la source FAGERH après validation humaine.",
        ))

    if unresolved_region_records:
        affected_uuids.update(
            normalized_uuid
            for normalized_uuid in (_normalize_uuid(record.uuid) for record, _ in unresolved_region_records)
            if normalized_uuid is not None
        )
        distinct_values = _distinct_preserving_order(raw_department for _, raw_department in unresolved_region_records)
        issues.append(DataQualityIssue(
            code="unresolved_region",
            severity="warning",
            field="region_code",
            record_count=len(unresolved_region_records),
            distinct_value_count=len(distinct_values),
            sample_values=tuple(str(value) for value in distinct_values[:5]),
            message="Au moins un département visible ne peut pas être rattaché à une région.",
            impact="Les agrégations géographiques régionales peuvent être incomplètes pour le périmètre concerné.",
            action_required="Vérifier le département source avant de recalculer les ventilations géographiques.",
        ))

    return DataQualitySummary(
        analyzed_questionnaires=len(visible_uuids),
        issue_count=len(issues),
        affected_record_count=len(affected_uuids),
        invalid_finess_count=len(_distinct_preserving_order(raw_finess for _, raw_finess, _ in invalid_finess_records)),
        unknown_department_count=len(_distinct_preserving_order(raw_department for _, raw_department in unknown_department_records)),
        unresolved_region_count=len(_distinct_preserving_order(raw_department for _, raw_department in unresolved_region_records)),
        global_level=_resolve_global_level(issues),
        warnings=tuple(),
        issues=tuple(issues),
    )


def _record_is_visible(record: RawQuestionnaireRecord, scope) -> bool:
    if scope.is_global:
        return True
    if scope.finess_values:
        finess_value = _normalize_scope_finess(record.finess_main)
        if finess_value is None or finess_value not in scope.finess_values:
            return False
    if scope.department_codes:
        department_code = _normalize_scope_code(record.department_code)
        if department_code is None or department_code not in scope.department_codes:
            return False
    if scope.region_codes:
        region_code = _normalize_scope_code(record.region_code)
        if region_code is None or region_code not in scope.region_codes:
            return False
    return True


def _normalize_scope_finess(value: object) -> str | None:
    return normalize_finess(value)


def _normalize_scope_code(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    return text or None


def _extract_raw_finess(record: RawQuestionnaireRecord) -> str | None:
    raw_value = record.raw.get("finess_main") if isinstance(record.raw, dict) else None
    if raw_value is None:
        raw_value = record.finess_main
    if raw_value is None:
        return None
    return str(raw_value)


def _extract_raw_department(record: RawQuestionnaireRecord) -> str | None:
    raw_value = None
    if isinstance(record.raw, dict):
        raw_value = record.raw.get("es_departement")
        if raw_value is None:
            raw_value = record.raw.get("department_code")
        if raw_value is None:
            raw_value = record.raw.get("departement")
    if raw_value is None:
        raw_value = record.department_code
    if raw_value is None:
        return None
    text = str(raw_value).strip()
    return text or None


def _mask_finess(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = str(value).strip()
    if not stripped:
        return None
    if len(stripped) <= 4:
        return "*" * len(stripped)
    return stripped[:2] + ("*" * (len(stripped) - 4)) + stripped[-2:]


def _distinct_preserving_order(values) -> list[str | None]:
    distinct: list[str | None] = []
    seen: set[str] = set()
    saw_none = False
    for value in values:
        if value is None:
            if not saw_none:
                distinct.append(None)
                saw_none = True
            continue
        key = str(value)
        if key in seen:
            continue
        seen.add(key)
        distinct.append(key)
    return distinct


def _normalize_uuid(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _resolve_global_level(issues: list[DataQualityIssue]) -> str:
    if any(issue.severity == "error" for issue in issues):
        return "error"
    if any(issue.severity == "warning" for issue in issues):
        return "warning"
    return "none"
