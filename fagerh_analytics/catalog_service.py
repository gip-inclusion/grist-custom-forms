"""Shared metadata service for the FAGERH analytics catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .catalog import (
    CATALOG_VERSION,
    GRAIN_SORT_ORDER,
    INDICATORS,
    VISIBILITY_SORT_ORDER,
    get_indicator_definition,
    get_indicator_required_capabilities,
)
from .permissions import PermissionDeniedError, ensure_indicator_scope_allowed, get_scope
from .repositories.base import QuestionnaireRepository
from .schema import is_indicator_available


ALLOWED_CATALOG_FILTERS = {"visibility", "grain", "available"}
ALLOWED_VISIBILITY_FILTERS = {"internal", "observatory", "both"}
ALLOWED_GRAIN_FILTERS = set(GRAIN_SORT_ORDER)
ALLOWED_AVAILABLE_FILTERS = {"true", "false"}


@dataclass(frozen=True)
class CatalogMetadataResult:
    """Structured catalog metadata payload."""

    catalog_version: str
    indicators: list[dict[str, object]]
    warnings: list[str]


def build_catalog_metadata(
    user_context,
    repository: QuestionnaireRepository,
    *,
    filters: dict[str, str] | None = None,
) -> CatalogMetadataResult:
    """Build a stable metadata catalog for the current user context and schema."""

    normalized_filters = _normalize_catalog_filters(filters or {})
    scope = get_scope(user_context)
    schema = repository.validate_schema()
    items: list[dict[str, object]] = []
    for indicator_id in sorted(INDICATORS, key=_catalog_sort_key):
        definition = INDICATORS[indicator_id]
        if not _is_visibility_allowed(definition.visibility, getattr(scope, "role", "")):
            continue
        available = is_indicator_available(indicator_id, schema)
        unavailable_reason = None
        missing_capabilities: list[str] = []
        if not available:
            required_capabilities = get_indicator_required_capabilities(indicator_id)
            missing_capabilities = [
                capability
                for capability in required_capabilities
                if capability not in schema.available_capabilities
            ]
            if missing_capabilities:
                unavailable_reason = f"Missing schema capabilities: {', '.join(missing_capabilities)}"
        try:
            ensure_indicator_scope_allowed(indicator_id, scope, definition.compatible_filters)
        except PermissionDeniedError:
            available = False
            unavailable_reason = "Indicator outside user scope"
        item = {
            "indicator_id": definition.id,
            "label": definition.label,
            "definition": definition.definition,
            "unit": definition.unit,
            "grain": definition.grain,
            "visibility": definition.visibility,
            "confidence_level": definition.confidence_level,
            "compatible_filters": list(definition.compatible_filters),
            "required_capabilities": list(get_indicator_required_capabilities(definition.id)),
            "component_indicators": list(definition.component_indicators),
            "business_warnings": list(definition.business_warnings),
            "double_counting_policy": definition.double_counting_policy,
            "exportable": definition.exportable and scope.can_export,
            "available": available,
            "unavailable_reason": unavailable_reason,
            "missing_capabilities": missing_capabilities,
            "dataset_id": definition.dataset_id,
            "source_fields": list(definition.source_fields),
            "source_paths": list(definition.source_paths),
            "aggregation_rule": definition.aggregation_rule,
            "provenance": definition.provenance,
        }
        if _matches_catalog_filters(item, normalized_filters):
            items.append(item)
    return CatalogMetadataResult(
        catalog_version=CATALOG_VERSION,
        indicators=items,
        warnings=list(schema.warnings),
    )


def get_catalog_indicator_metadata(
    user_context,
    repository: QuestionnaireRepository,
    indicator_id: str,
) -> dict[str, object] | None:
    """Return the detailed catalog metadata for one indicator when visible."""

    definition = get_indicator_definition(indicator_id)
    if definition is None:
        return None
    catalog = build_catalog_metadata(user_context, repository)
    for item in catalog.indicators:
        if item["indicator_id"] == indicator_id:
            return item
    return None


def _normalize_catalog_filters(filters: dict[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in filters.items():
        if key not in ALLOWED_CATALOG_FILTERS:
            raise ValueError(f"Unknown catalog query parameter: {key}")
        text = str(value).strip()
        if not text:
            raise ValueError(f"Invalid catalog filter {key}: expected non-empty value")
        normalized[key] = text
    visibility = normalized.get("visibility")
    if visibility is not None and visibility not in ALLOWED_VISIBILITY_FILTERS:
        raise ValueError(f"Invalid catalog filter visibility={visibility!r}")
    grain = normalized.get("grain")
    if grain is not None and grain not in ALLOWED_GRAIN_FILTERS:
        raise ValueError(f"Invalid catalog filter grain={grain!r}")
    available = normalized.get("available")
    if available is not None and available not in ALLOWED_AVAILABLE_FILTERS:
        raise ValueError(f"Invalid catalog filter available={available!r}")
    return normalized


def _matches_catalog_filters(item: dict[str, object], filters: dict[str, str]) -> bool:
    if "visibility" in filters and item["visibility"] != filters["visibility"]:
        return False
    if "grain" in filters and item["grain"] != filters["grain"]:
        return False
    if "available" in filters and item["available"] is not (filters["available"] == "true"):
        return False
    return True


def _is_visibility_allowed(visibility: str, role: str) -> bool:
    if role == "admin_global":
        return True
    return visibility in {"observatory", "both"}


def _catalog_sort_key(indicator_id: str) -> tuple[int, int, str, str]:
    definition = INDICATORS[indicator_id]
    return (
        VISIBILITY_SORT_ORDER[definition.visibility],
        GRAIN_SORT_ORDER[definition.grain],
        definition.label.casefold(),
        definition.id,
    )
