"""Internal Python API facade for the FAGERH analytics engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from .catalog import INDICATORS, get_indicator_definition, get_indicator_required_capabilities
from .catalog_service import build_catalog_metadata
from .data_quality import DataQualitySummary, analyze_data_quality
from .domain import IndicatorResult, UserContext
from .engine import AnalyticsEngine, DataConsistencyError, DataQualityError, UnknownIndicatorError
from .filters import FilterValidationError, IncompatibleFilterError
from .permissions import InvalidUserContextError, PermissionDeniedError, ensure_export_allowed, get_scope
from .repositories.base import (
    QuestionnaireRepository,
    RepositoryConfigurationError,
    RepositoryConnectionError,
    RepositoryResponseError,
)
from .schema import IndicatorUnavailableError, ensure_indicator_schema_available, is_indicator_available


API_VERSION = "v1"


@dataclass(frozen=True)
class IndicatorQuery:
    """Stable internal request contract for analytics indicator execution."""

    indicator_id: str
    filters: dict[str, object]
    user_context: UserContext
    request_id: str | None = None


@dataclass(frozen=True)
class ApiError:
    """Stable internal error object for the API facade."""

    code: str
    message: str
    details: dict[str, object]


@dataclass(frozen=True)
class IndicatorQueryResponse:
    """Stable internal response contract for analytics indicator execution."""

    api_version: str
    request_id: str | None
    status: str
    result: dict[str, object] | None
    error: dict[str, object] | None
    warnings: list[str]
    generated_at: str
    freshness_at: str | None


def get_data_quality_summary(
    repository: QuestionnaireRepository,
    user_context: UserContext | None,
) -> DataQualitySummary:
    """Return an aggregated, scope-aware data quality summary."""

    return analyze_data_quality(repository.list_raw_questionnaires(), user_context)


def execute_indicator_query(
    query: IndicatorQuery,
    repository: QuestionnaireRepository,
    *,
    generated_at: str | None = None,
    now_provider: Callable[[], datetime] | None = None,
) -> IndicatorQueryResponse:
    """Execute an indicator query through the canonical analytics engine."""

    timestamp = _resolve_generated_at(generated_at=generated_at, now_provider=now_provider)
    try:
        _validate_query(query)
        if get_indicator_definition(query.indicator_id) is None:
            raise UnknownIndicatorError(f"Unknown indicator: {query.indicator_id}")
        ensure_indicator_schema_available(query.indicator_id, repository.validate_schema())
        result = AnalyticsEngine(repository).compute_indicator(
            query.indicator_id,
            filters=query.filters,
            user_context=query.user_context,
        )
        serialized_result = serialize_indicator_result(result)
        warnings = list(serialized_result.get("warnings", []))
        return IndicatorQueryResponse(
            api_version=API_VERSION,
            request_id=query.request_id,
            status="success",
            result=serialized_result,
            error=None,
            warnings=warnings,
            generated_at=timestamp,
            freshness_at=repository.get_freshness_at(),
        )
    except UnknownIndicatorError as exc:
        return _error_response("indicator_not_found", str(exc), query, timestamp, {"indicator_id": query.indicator_id})
    except InvalidUserContextError as exc:
        return _error_response("invalid_user_context", str(exc), query, timestamp, {})
    except PermissionDeniedError as exc:
        return _error_response("permission_denied", str(exc), query, timestamp, {})
    except FilterValidationError as exc:
        return _error_response("invalid_filter", str(exc), query, timestamp, {})
    except IncompatibleFilterError as exc:
        return _error_response("incompatible_filter", str(exc), query, timestamp, {})
    except DataQualityError as exc:
        return _error_response("data_quality_error", str(exc), query, timestamp, {})
    except DataConsistencyError as exc:
        return _error_response("data_consistency_error", str(exc), query, timestamp, {})
    except IndicatorUnavailableError as exc:
        return _error_response("indicator_unavailable", str(exc), query, timestamp, {"indicator_id": query.indicator_id})
    except (RepositoryConfigurationError, RepositoryConnectionError, RepositoryResponseError) as exc:
        return _error_response("data_source_error", str(exc), query, timestamp, {})
    except ValueError as exc:
        return _error_response("invalid_request", str(exc), query, timestamp, {})
    except Exception:
        return _error_response(
            "internal_error",
            "An internal error occurred while executing the indicator query.",
            query,
            timestamp,
            {},
        )


def serialize_indicator_result(result: IndicatorResult) -> dict[str, object]:
    """Convert IndicatorResult into a JSON-serializable stable mapping."""

    definition = get_indicator_definition(result.indicator_id)
    return {
        "indicator_id": result.indicator_id,
        "label": result.label,
        "value": result.value,
        "unit": result.unit,
        "breakdown": _serialize_mapping(result.breakdown),
        "privacy_status": result.privacy_status,
        "confidence_level": result.confidence_level,
        "source": _serialize_mapping(result.source),
        "resolved_filters": {
            "requested": _serialize_mapping(result.resolved_filters.requested),
            "applied": _serialize_mapping(result.resolved_filters.applied),
            "rejected": _serialize_mapping(result.resolved_filters.rejected),
            "scope_constraints": _serialize_mapping(result.resolved_filters.scope_constraints),
            "user_role": result.resolved_filters.user_role,
            "warnings": list(result.resolved_filters.warnings),
        },
        "user_role": result.user_role,
        "permission_scope": _serialize_permission_scope(result.permission_scope),
        "warnings": list(result.resolved_filters.warnings),
        "metadata": _serialize_indicator_metadata(definition),
        "freshness_at": None,
    }


def list_available_indicators(
    user_context: UserContext,
    repository: QuestionnaireRepository,
) -> list[dict[str, object]]:
    """Return indicator metadata and availability for a user scope without calculation."""

    return build_catalog_metadata(user_context, repository).indicators


def check_export_permission(user_context: UserContext) -> None:
    """Validate export capability for a user context."""

    ensure_export_allowed(get_scope(user_context))


def _validate_query(query: IndicatorQuery) -> None:
    if not isinstance(query, IndicatorQuery):
        raise ValueError("Invalid request: query must be an IndicatorQuery")
    if not isinstance(query.indicator_id, str) or not query.indicator_id.strip():
        raise ValueError("Invalid request: indicator_id must be a non-empty string")
    if not isinstance(query.filters, dict):
        raise ValueError("Invalid request: filters must be a dictionary")
    if query.user_context is None:
        raise ValueError("Invalid request: user_context is required")
    if query.request_id is not None and (not isinstance(query.request_id, str) or not query.request_id.strip()):
        raise ValueError("Invalid request: request_id must be a non-empty string when provided")


def _resolve_generated_at(
    *,
    generated_at: str | None,
    now_provider: Callable[[], datetime] | None,
) -> str:
    if generated_at is not None:
        return generated_at
    moment = now_provider() if now_provider is not None else datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _error_response(
    code: str,
    message: str,
    query: IndicatorQuery,
    generated_at: str,
    details: dict[str, object],
) -> IndicatorQueryResponse:
    api_error = ApiError(code=code, message=message, details=details)
    return IndicatorQueryResponse(
        api_version=API_VERSION,
        request_id=query.request_id,
        status="error",
        result=None,
        error={
            "code": api_error.code,
            "message": api_error.message,
            "details": _serialize_mapping(api_error.details),
        },
        warnings=[],
        generated_at=generated_at,
        freshness_at=None,
    )


def _serialize_permission_scope(scope) -> dict[str, object] | None:
    if scope is None:
        return None
    return {
        "is_global": scope.is_global,
        "region_codes": list(scope.region_codes),
        "department_codes": list(scope.department_codes),
        "finess_values": list(scope.finess_values),
        "allowed_dispositifs": list(scope.allowed_dispositifs),
        "can_export": scope.can_export,
        "role": scope.role,
    }


def _serialize_mapping(value: dict[str, object] | None) -> dict[str, object]:
    if not value:
        return {}
    return {key: _serialize_value(value[key]) for key in sorted(value)}


def _serialize_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return _serialize_mapping(value)
    if isinstance(value, tuple):
        return [_serialize_value(item) for item in value]
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, set):
        return [_serialize_value(item) for item in sorted(value)]
    return str(value)


def _serialize_indicator_metadata(definition) -> dict[str, object] | None:
    if definition is None:
        return None
    return {
        "definition": definition.definition,
        "grain": definition.grain,
        "visibility": definition.visibility,
        "required_capabilities": list(get_indicator_required_capabilities(definition.id)),
        "component_indicators": list(definition.component_indicators),
        "source_fields": list(definition.source_fields),
        "source_paths": list(definition.source_paths),
        "business_warnings": list(definition.business_warnings),
        "double_counting_policy": definition.double_counting_policy,
    }
