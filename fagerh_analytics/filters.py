"""Centralized analytical filters for the FAGERH analytics engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .domain import EvaluationActivityRecord, PermissionScope, QuestionnaireRecord, RawQuestionnaireRecord, ResolvedFilters
from .finess import normalize_finess
from .permissions import PermissionDeniedError


KNOWN_DISPOSITIFS = {"esrp", "espo", "ueros", "deac"}
KNOWN_COMPLETION_SCOPES = {"all", "completed", "in_progress"}
FILTER_NAMES = {"campaign_year", "region_code", "department_code", "finess_main", "dispositifs", "completion_scope"}


class FilterValidationError(ValueError):
    """Raised when a filter value is invalid."""


class IncompatibleFilterError(ValueError):
    """Raised when a valid filter is not compatible with an indicator."""


@dataclass(frozen=True)
class FilterContext:
    """Filter resolution context derived from repository data."""

    available_campaign_years: tuple[int, ...]
    campaign_filter_available: bool
    department_to_regions: dict[str, tuple[str, ...]]
    finess_to_regions: dict[str, tuple[str, ...]]
    finess_to_departments: dict[str, tuple[str, ...]]


def build_filter_context(raw_records: Iterable[RawQuestionnaireRecord]) -> FilterContext:
    campaigns = sorted({
        record.campaign_year
        for record in raw_records
        if isinstance(record.campaign_year, int) and record.campaign_year > 0
    })
    department_to_regions: dict[str, set[str]] = {}
    finess_to_regions: dict[str, set[str]] = {}
    finess_to_departments: dict[str, set[str]] = {}
    for record in raw_records:
        department_code = _normalize_optional_code(record.department_code)
        region_code = _normalize_optional_code(record.region_code)
        finess_main = _normalize_finess_value(record.finess_main)
        if department_code is None or region_code is None:
            if finess_main is None:
                continue
        else:
            department_to_regions.setdefault(department_code, set()).add(region_code)
        if finess_main is not None and region_code is not None:
            finess_to_regions.setdefault(finess_main, set()).add(region_code)
        if finess_main is not None and department_code is not None:
            finess_to_departments.setdefault(finess_main, set()).add(department_code)
    return FilterContext(
        available_campaign_years=tuple(campaigns),
        campaign_filter_available=bool(campaigns),
        department_to_regions={key: tuple(sorted(values)) for key, values in department_to_regions.items()},
        finess_to_regions={key: tuple(sorted(values)) for key, values in finess_to_regions.items()},
        finess_to_departments={key: tuple(sorted(values)) for key, values in finess_to_departments.items()},
    )


def resolve_filters(
    requested_filters: dict[str, object] | None,
    *,
    compatible_filters: tuple[str, ...],
    indicator_id: str,
    context: FilterContext,
    permission_scope: PermissionScope | None = None,
) -> ResolvedFilters:
    requested_filters = dict(requested_filters or {})
    unknown_filters = sorted(set(requested_filters) - FILTER_NAMES)
    if unknown_filters:
        name = unknown_filters[0]
        raise FilterValidationError(f"Invalid filter {name!r} for indicator {indicator_id}: unknown filter")

    requested: dict[str, object] = {}
    applied: dict[str, object] = {}
    scope_constraints: dict[str, object] = {}
    warnings: list[str] = []
    for filter_name, raw_value in requested_filters.items():
        requested[filter_name] = raw_value
        if filter_name not in compatible_filters:
            raise IncompatibleFilterError(
                f"Incompatible filter {filter_name}={raw_value!r} for indicator {indicator_id}"
            )
        normalized_value = _normalize_filter_value(filter_name, raw_value)
        if normalized_value is None:
            continue
        applied[filter_name] = normalized_value

    department_code = applied.get("department_code")
    region_code = applied.get("region_code")
    if isinstance(department_code, str) and isinstance(region_code, str):
        known_regions = context.department_to_regions.get(department_code)
        if known_regions and region_code not in known_regions:
            raise FilterValidationError(
                f"Invalid filter department_code={department_code!r} for indicator {indicator_id}: "
                f"incompatible with region_code={region_code!r}"
            )

    campaign_year = applied.get("campaign_year")
    if isinstance(campaign_year, int) and not context.campaign_filter_available:
        raise IncompatibleFilterError(
            "Le filtre de campagne n’est pas disponible pour cette source de données."
        )
    if isinstance(campaign_year, int) and campaign_year not in context.available_campaign_years:
        warnings.append(f"campaign_year {campaign_year} absent from dataset; result will be empty")

    if permission_scope is not None:
        applied, scope_constraints = _apply_permission_scope(
            applied=applied,
            requested=requested,
            indicator_id=indicator_id,
            compatible_filters=compatible_filters,
            context=context,
            permission_scope=permission_scope,
        )

    return ResolvedFilters(
        requested=requested,
        applied=applied,
        rejected={},
        scope_constraints=scope_constraints,
        user_role=permission_scope.role if permission_scope is not None else None,
        warnings=tuple(warnings),
    )


def _apply_permission_scope(
    *,
    applied: dict[str, object],
    requested: dict[str, object],
    indicator_id: str,
    compatible_filters: tuple[str, ...],
    context: FilterContext,
    permission_scope: PermissionScope,
) -> tuple[dict[str, object], dict[str, object]]:
    final_applied = dict(applied)
    scope_constraints: dict[str, object] = {}

    if permission_scope.region_codes:
        final_applied["region_code"] = _merge_scope_constraint(
            indicator_id=indicator_id,
            filter_name="region_code",
            requested_value=final_applied.get("region_code"),
            allowed_values=permission_scope.region_codes,
            multi=False,
        )
        if "region_code" not in applied:
            scope_constraints["region_code"] = permission_scope.region_codes

    if permission_scope.department_codes:
        final_applied["department_code"] = _merge_scope_constraint(
            indicator_id=indicator_id,
            filter_name="department_code",
            requested_value=final_applied.get("department_code"),
            allowed_values=permission_scope.department_codes,
            multi=False,
        )
        if "department_code" not in applied:
            scope_constraints["department_code"] = permission_scope.department_codes

    if permission_scope.finess_values:
        final_applied["finess_main"] = _merge_scope_constraint(
            indicator_id=indicator_id,
            filter_name="finess_main",
            requested_value=final_applied.get("finess_main"),
            allowed_values=permission_scope.finess_values,
            multi=True,
        )
        if "finess_main" not in applied:
            scope_constraints["finess_main"] = permission_scope.finess_values

    if permission_scope.allowed_dispositifs and "dispositifs" in compatible_filters:
        final_applied["dispositifs"] = _merge_scope_constraint(
            indicator_id=indicator_id,
            filter_name="dispositifs",
            requested_value=final_applied.get("dispositifs"),
            allowed_values=permission_scope.allowed_dispositifs,
            multi=True,
        )
        if "dispositifs" not in applied:
            scope_constraints["dispositifs"] = permission_scope.allowed_dispositifs

    _validate_scope_relations(final_applied, requested, indicator_id, context)
    return final_applied, scope_constraints


def _merge_scope_constraint(
    *,
    indicator_id: str,
    filter_name: str,
    requested_value: object | None,
    allowed_values: tuple[str, ...],
    multi: bool,
) -> object:
    if requested_value is None:
        return allowed_values if multi else allowed_values[0]

    if multi:
        requested_values = tuple(requested_value)
        if any(value not in allowed_values for value in requested_values):
            raise PermissionDeniedError(
                f"Permission denied for filter {filter_name} on indicator {indicator_id}: value outside user scope"
            )
        return requested_values

    if requested_value not in allowed_values:
        raise PermissionDeniedError(
            f"Permission denied for filter {filter_name} on indicator {indicator_id}: value outside user scope"
        )
    return requested_value


def _validate_scope_relations(
    applied: dict[str, object],
    requested: dict[str, object],
    indicator_id: str,
    context: FilterContext,
) -> None:
    region_code = applied.get("region_code")
    department_code = applied.get("department_code")
    if isinstance(region_code, str) and isinstance(department_code, str):
        known_regions = context.department_to_regions.get(department_code)
        if known_regions and region_code not in known_regions:
            raise PermissionDeniedError(
                f"Permission denied for filter department_code on indicator {indicator_id}: value outside user scope"
            )

    finess_values = applied.get("finess_main")
    if not isinstance(finess_values, tuple):
        return
    for finess_value in finess_values:
        if isinstance(region_code, str):
            known_regions = context.finess_to_regions.get(finess_value)
            if known_regions and region_code not in known_regions:
                raise PermissionDeniedError(
                    f"Permission denied for filter finess_main on indicator {indicator_id}: value outside user scope"
                )
        if isinstance(department_code, str):
            known_departments = context.finess_to_departments.get(finess_value)
            if known_departments and department_code not in known_departments:
                raise PermissionDeniedError(
                    f"Permission denied for filter finess_main on indicator {indicator_id}: value outside user scope"
                )


def record_matches_raw(record: RawQuestionnaireRecord, resolved_filters: ResolvedFilters) -> bool:
    return _record_matches_common(
        campaign_year=record.campaign_year,
        region_code=record.region_code,
        department_code=record.department_code,
        finess_main=record.finess_main,
        completion_status=record.completion_status,
        dispositif=None,
        resolved_filters=resolved_filters,
        apply_dispositif_filter=False,
    )


def record_matches_questionnaire(record: QuestionnaireRecord, resolved_filters: ResolvedFilters) -> bool:
    return _record_matches_common(
        campaign_year=record.campaign_year,
        region_code=record.region_code,
        department_code=record.department_code,
        finess_main=record.finess_main,
        completion_status=record.completion_status,
        dispositif=record.dispositif,
        resolved_filters=resolved_filters,
        apply_dispositif_filter=True,
    )


def record_matches_evaluation(record: EvaluationActivityRecord, resolved_filters: ResolvedFilters) -> bool:
    return _record_matches_common(
        campaign_year=record.campaign_year,
        region_code=record.region_code,
        department_code=record.department_code,
        finess_main=record.finess_main,
        completion_status=record.completion_status,
        dispositif=None,
        resolved_filters=resolved_filters,
        apply_dispositif_filter=False,
    )


def _record_matches_common(
    *,
    campaign_year: int | None,
    region_code: str | None,
    department_code: str | None,
    finess_main: str | None,
    completion_status: str | None,
    dispositif: str | None,
    resolved_filters: ResolvedFilters,
    apply_dispositif_filter: bool,
) -> bool:
    applied = resolved_filters.applied
    if "campaign_year" in applied and campaign_year != applied["campaign_year"]:
        return False
    if "region_code" in applied and _normalize_optional_code(region_code) != applied["region_code"]:
        return False
    if "department_code" in applied and _normalize_optional_code(department_code) != applied["department_code"]:
        return False
    if "finess_main" in applied:
        allowed_finess = applied["finess_main"]
        if _normalize_finess_value(finess_main) not in allowed_finess:
            return False
    if "completion_scope" in applied:
        expected_status = applied["completion_scope"]
        if expected_status != "all" and completion_status != expected_status:
            return False
    if apply_dispositif_filter and "dispositifs" in applied:
        if dispositif is None or _normalize_dispositif_value(dispositif) not in applied["dispositifs"]:
            return False
    return True


def _normalize_filter_value(filter_name: str, raw_value: object) -> object | None:
    if filter_name == "campaign_year":
        if raw_value is None:
            return None
        if isinstance(raw_value, bool) or not isinstance(raw_value, int):
            raise FilterValidationError(f"Invalid filter campaign_year={raw_value!r}: expected positive integer")
        if raw_value <= 0 or raw_value > 9999:
            raise FilterValidationError(f"Invalid filter campaign_year={raw_value!r}: expected positive integer")
        return raw_value

    if filter_name == "region_code":
        return _normalize_code_filter("region_code", raw_value)

    if filter_name == "department_code":
        return _normalize_code_filter("department_code", raw_value)

    if filter_name == "finess_main":
        return _normalize_finess_filter(raw_value)

    if filter_name == "dispositifs":
        return _normalize_dispositifs_filter(raw_value)

    if filter_name == "completion_scope":
        return _normalize_completion_scope_filter(raw_value)

    raise FilterValidationError(f"Invalid filter {filter_name!r}: unknown filter")


def _normalize_code_filter(filter_name: str, raw_value: object) -> str | None:
    if raw_value is None:
        return None
    if not isinstance(raw_value, str):
        raise FilterValidationError(f"Invalid filter {filter_name}={raw_value!r}: expected string")
    normalized = raw_value.strip().upper()
    return normalized or None


def _normalize_finess_filter(raw_value: object) -> tuple[str, ...] | None:
    values = _coerce_multi_or_single(raw_value, "finess_main")
    if values is None:
        return None
    normalized_values = []
    for value in values:
        normalized = _normalize_finess_value(value)
        if normalized is None:
            raise FilterValidationError(f"Invalid filter finess_main={value!r}: expected 8 or 9 digits")
        normalized_values.append(normalized)
    return tuple(sorted(set(normalized_values)))


def _normalize_dispositifs_filter(raw_value: object) -> tuple[str, ...] | None:
    values = _coerce_multi_or_single(raw_value, "dispositifs")
    if values is None:
        return None
    normalized_values = []
    for value in values:
        normalized = _normalize_dispositif_value(value)
        if normalized is None:
            raise FilterValidationError(
                f"Invalid filter dispositifs={value!r}: expected one of esrp, espo, ueros, deac"
            )
        normalized_values.append(normalized)
    return tuple(sorted(set(normalized_values)))


def _normalize_completion_scope_filter(raw_value: object) -> str | None:
    if raw_value is None:
        return None
    if not isinstance(raw_value, str):
        raise FilterValidationError(
            f"Invalid filter completion_scope={raw_value!r}: expected one of {sorted(KNOWN_COMPLETION_SCOPES)}"
        )
    normalized = raw_value.strip().lower()
    if not normalized:
        return None
    if normalized not in KNOWN_COMPLETION_SCOPES:
        raise FilterValidationError(
            f"Invalid filter completion_scope={raw_value!r}: expected one of {sorted(KNOWN_COMPLETION_SCOPES)}"
        )
    return normalized


def _coerce_multi_or_single(raw_value: object, filter_name: str) -> tuple[object, ...] | None:
    if raw_value is None:
        return None
    if isinstance(raw_value, str):
        normalized = raw_value.strip()
        return (normalized,) if normalized else None
    if isinstance(raw_value, (list, tuple, set)):
        values = tuple(item for item in raw_value if not (isinstance(item, str) and not item.strip()))
        return values or None
    raise FilterValidationError(f"Invalid filter {filter_name}={raw_value!r}: expected string or collection of strings")


def _normalize_optional_code(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().upper()
    return normalized or None


def _normalize_finess_value(value: object) -> str | None:
    return normalize_finess(value)


def _normalize_dispositif_value(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    return normalized if normalized in KNOWN_DISPOSITIFS else None
