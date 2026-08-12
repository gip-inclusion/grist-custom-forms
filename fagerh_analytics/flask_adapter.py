"""Thin Flask adapter for the internal FAGERH analytics API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from flask import Blueprint, Response, jsonify, request

from .api import (
    API_VERSION,
    IndicatorQuery,
    check_export_permission,
    execute_indicator_query,
    get_data_quality_summary,
    list_available_indicators,
)
from .catalog_service import build_catalog_metadata, get_catalog_indicator_metadata
from .dashboard import build_dashboard_payload
from .observatoire import build_regional_observatory
from .engine import DataConsistencyError, DataQualityError
from .filters import FilterValidationError, IncompatibleFilterError
from .health import serialize_health_probe_result
from .permissions import InvalidUserContextError, PermissionDeniedError
from .repositories.base import RepositoryConfigurationError, RepositoryConnectionError, RepositoryResponseError


MAX_ANALYTICS_JSON_BYTES = 16 * 1024
MAX_FILTER_FINESS_VALUES = 100
MAX_FILTER_DISPOSITIFS = 4


def create_fagerh_analytics_blueprint(
    *,
    repository_factory: Callable[[], object],
    user_context_factory: Callable[[], object],
    auth_guard: Callable[[], Response | None],
    health_probe: Callable[[], object] | None = None,
) -> Blueprint:
    """Create a Blueprint exposing a thin HTTP layer over the analytics API."""

    blueprint = Blueprint("fagerh_analytics", __name__)

    @blueprint.route("/api/fagerh-analytics/v1/health", methods=["GET"])
    def health():
        try:
            result = health_probe() if health_probe is not None else None
            if result is None:
                return _json_error_response(503, "internal_error", "FAGERH Analytics health probe is unavailable.", None)
            payload, status_code = serialize_health_probe_result(result)
            return jsonify(payload), status_code
        except Exception:
            return _json_error_response(503, "internal_error", "FAGERH Analytics health probe failed.", None)

    @blueprint.route("/api/fagerh-analytics/v1/observatoire/<region_code>", methods=["GET"])
    def observatoire(region_code: str):
        denied = auth_guard()
        if denied is not None:
            return denied
        try:
            result = build_regional_observatory(
                repository_factory(),
                region_code,
                completion_scope=request.args.get("completion_scope", "completed"),
            )
            return _json_success_response(result=result, request_id=None)
        except ValueError as exc:
            return _json_error_response(400, "invalid_request", str(exc), None)
        except Exception as exc:
            return _translate_exception(exc)

    @blueprint.route("/api/fagerh-analytics/v1/indicators", methods=["GET"])
    def list_indicators():
        denied = auth_guard()
        if denied is not None:
            return denied
        try:
            user_context = user_context_factory()
            result = {"items": list_available_indicators(user_context, repository_factory())}
            return _json_success_response(result=result, request_id=None)
        except Exception as exc:
            return _translate_exception(exc)

    @blueprint.route("/api/fagerh-analytics/v1/catalog", methods=["GET"])
    def catalog():
        denied = auth_guard()
        if denied is not None:
            return denied
        try:
            user_context = user_context_factory()
            metadata = build_catalog_metadata(
                user_context,
                repository_factory(),
                filters=_extract_catalog_filters(),
            )
            payload = {
                "api_version": API_VERSION,
                "status": "success",
                "generated_at": _utc_now_iso(),
                "catalog_version": metadata.catalog_version,
                "indicators": metadata.indicators,
                "warnings": metadata.warnings,
                "error": None,
            }
            return jsonify(payload), 200
        except ValueError as exc:
            return _json_error_response(400, "invalid_request", str(exc), None)
        except Exception as exc:
            return _translate_exception(exc)

    @blueprint.route("/api/fagerh-analytics/v1/catalog/<indicator_id>", methods=["GET"])
    def catalog_indicator(indicator_id: str):
        denied = auth_guard()
        if denied is not None:
            return denied
        try:
            user_context = user_context_factory()
            metadata = build_catalog_metadata(user_context, repository_factory())
            item = get_catalog_indicator_metadata(user_context, repository_factory(), indicator_id)
            if item is None:
                return _json_error_response(404, "indicator_not_found", f"Unknown indicator: {indicator_id}", None)
            payload = {
                "api_version": API_VERSION,
                "status": "success",
                "generated_at": _utc_now_iso(),
                "catalog_version": metadata.catalog_version,
                "indicator": item,
                "warnings": metadata.warnings,
                "error": None,
            }
            return jsonify(payload), 200
        except Exception as exc:
            return _translate_exception(exc)

    @blueprint.route("/api/fagerh-analytics/v1/indicators/<indicator_id>", methods=["POST"])
    def execute_indicator(indicator_id: str):
        denied = auth_guard()
        if denied is not None:
            return denied

        transport_error = _validate_transport_payload()
        if transport_error is not None:
            return transport_error

        payload = request.get_json(silent=True)
        assert isinstance(payload, dict)
        filters = payload.get("filters") or {}
        request_id = payload.get("request_id")

        size_error = _validate_filter_limits(filters)
        if size_error is not None:
            return size_error

        user_context = user_context_factory()
        query = IndicatorQuery(
            indicator_id=indicator_id,
            filters=filters,
            user_context=user_context,
            request_id=request_id,
        )
        try:
            response = execute_indicator_query(query, repository_factory())
            return jsonify(_response_to_dict(response)), _http_status_for_response(response)
        except Exception as exc:
            return _translate_exception(exc)

    @blueprint.route("/api/fagerh-analytics/v1/export-permission", methods=["GET"])
    def export_permission():
        denied = auth_guard()
        if denied is not None:
            return denied
        try:
            user_context = user_context_factory()
            check_export_permission(user_context)
            return _json_success_response(
                result={"allowed": True, "role": getattr(user_context, "role", None)},
                request_id=None,
            )
        except Exception as exc:
            return _translate_exception(exc)

    @blueprint.route("/api/fagerh-analytics/v1/data-quality", methods=["GET"])
    def data_quality():
        denied = auth_guard()
        if denied is not None:
            return denied
        try:
            user_context = user_context_factory()
            if getattr(user_context, "role", None) != "admin_global":
                return _json_error_response(403, "permission_denied", "Data quality details are reserved to internal administrators.", None)
            summary = get_data_quality_summary(repository_factory(), user_context)
            payload = {
                "api_version": API_VERSION,
                "status": "success",
                "generated_at": _utc_now_iso(),
                "summary": _serialize_data_quality_summary(summary),
                "issues": [_serialize_data_quality_issue(issue) for issue in summary.issues],
                "warnings": list(summary.warnings),
                "error": None,
            }
            return jsonify(payload), 200
        except Exception as exc:
            return _translate_exception(exc)

    @blueprint.route("/api/fagerh-analytics/v1/dashboard", methods=["POST"])
    def dashboard():
        denied = auth_guard()
        if denied is not None:
            return denied

        transport_error = _validate_transport_payload()
        if transport_error is not None:
            return transport_error

        payload = request.get_json(silent=True)
        assert isinstance(payload, dict)
        filters = payload.get("filters") or {}
        request_id = payload.get("request_id")

        size_error = _validate_filter_limits(filters)
        if size_error is not None:
            return size_error

        try:
            user_context = user_context_factory()
            dashboard_result = build_dashboard_payload(
                repository_factory(),
                user_context,
                filters=filters,
            )
            return _json_success_response(result=dashboard_result.payload, request_id=request_id)
        except Exception as exc:
            return _translate_exception(exc)

    return blueprint


def _validate_transport_payload():
    content_length = request.content_length or 0
    if content_length > MAX_ANALYTICS_JSON_BYTES:
        return _json_error_response(400, "invalid_request", "JSON payload too large", None)
    if not request.is_json:
        return _json_error_response(400, "invalid_request", "Request body must be JSON", None)
    payload = request.get_json(silent=True)
    if payload is None:
        return _json_error_response(400, "invalid_request", "Malformed JSON body", None)
    if not isinstance(payload, dict):
        return _json_error_response(400, "invalid_request", "JSON root must be an object", None)

    allowed_keys = {"filters", "request_id"}
    unknown_keys = sorted(set(payload) - allowed_keys)
    if unknown_keys:
        return _json_error_response(400, "invalid_request", f"Unknown JSON property: {unknown_keys[0]}", None)

    if "filters" in payload and not isinstance(payload.get("filters"), dict):
        return _json_error_response(400, "invalid_request", "filters must be an object", None)
    if "request_id" in payload:
        request_id = payload.get("request_id")
        if not isinstance(request_id, str) or not request_id.strip():
            return _json_error_response(400, "invalid_request", "request_id must be a non-empty string", None)
    return None


def _validate_filter_limits(filters: dict[str, Any]):
    finess_value = filters.get("finess_main")
    if isinstance(finess_value, list) and len(finess_value) > MAX_FILTER_FINESS_VALUES:
        return _json_error_response(400, "invalid_request", "Too many FINESS values requested", None)
    dispositifs_value = filters.get("dispositifs")
    if isinstance(dispositifs_value, list) and len(dispositifs_value) > MAX_FILTER_DISPOSITIFS:
        return _json_error_response(400, "invalid_request", "Too many dispositifs requested", None)
    return None


def _serialize_data_quality_summary(summary) -> dict[str, object]:
    return {
        "analyzed_questionnaires": summary.analyzed_questionnaires,
        "issue_count": summary.issue_count,
        "affected_record_count": summary.affected_record_count,
        "invalid_finess_count": summary.invalid_finess_count,
        "unknown_department_count": summary.unknown_department_count,
        "unresolved_region_count": summary.unresolved_region_count,
        "global_level": summary.global_level,
    }


def _serialize_data_quality_issue(issue) -> dict[str, object]:
    return {
        "code": issue.code,
        "severity": issue.severity,
        "field": issue.field,
        "record_count": issue.record_count,
        "distinct_value_count": issue.distinct_value_count,
        "message": issue.message,
        "impact": issue.impact,
        "action_required": issue.action_required,
        "masked_examples": list(issue.masked_examples),
        "sample_values": list(issue.sample_values),
    }


def _extract_catalog_filters() -> dict[str, str]:
    filters: dict[str, str] = {}
    for key in request.args:
        values = request.args.getlist(key)
        if len(values) != 1:
            raise ValueError(f"Invalid catalog filter {key}: expected a single value")
        filters[key] = values[0]
    return filters


def _http_status_for_response(response) -> int:
    if response.status == "success":
        return 200
    code = (response.error or {}).get("code")
    return {
        "invalid_request": 400,
        "invalid_filter": 400,
        "incompatible_filter": 400,
        "permission_denied": 403,
        "invalid_user_context": 403,
        "indicator_not_found": 404,
        "indicator_unavailable": 503,
        "data_quality_error": 422,
        "data_consistency_error": 422,
        "data_source_error": 503,
        "internal_error": 500,
    }.get(code, 500)


def _response_to_dict(response) -> dict[str, Any]:
    return {
        "api_version": response.api_version,
        "request_id": response.request_id,
        "status": response.status,
        "result": response.result,
        "error": response.error,
        "warnings": list(response.warnings),
        "generated_at": response.generated_at,
        "freshness_at": response.freshness_at,
    }


def _json_success_response(*, result: dict[str, Any], request_id: str | None):
    payload = {
        "api_version": API_VERSION,
        "request_id": request_id,
        "status": "success",
        "result": result,
        "error": None,
        "warnings": [],
        "generated_at": _utc_now_iso(),
        "freshness_at": None,
    }
    return jsonify(payload), 200


def _json_error_response(status_code: int, code: str, message: str, request_id: str | None):
    payload = {
        "api_version": API_VERSION,
        "request_id": request_id,
        "status": "error",
        "result": None,
        "error": {
            "code": code,
            "message": message,
            "details": {},
        },
        "warnings": [],
        "generated_at": _utc_now_iso(),
        "freshness_at": None,
    }
    return jsonify(payload), status_code


def _translate_exception(exc: Exception):
    if isinstance(exc, InvalidUserContextError):
        return _json_error_response(403, "invalid_user_context", str(exc), None)
    if isinstance(exc, PermissionDeniedError):
        return _json_error_response(403, "permission_denied", str(exc), None)
    if isinstance(exc, FilterValidationError):
        return _json_error_response(400, "invalid_filter", str(exc), None)
    if isinstance(exc, IncompatibleFilterError):
        return _json_error_response(400, "incompatible_filter", str(exc), None)
    if isinstance(exc, DataQualityError):
        return _json_error_response(422, "data_quality_error", str(exc), None)
    if isinstance(exc, DataConsistencyError):
        return _json_error_response(422, "data_consistency_error", str(exc), None)
    if isinstance(exc, (RepositoryConfigurationError, RepositoryConnectionError, RepositoryResponseError)):
        return _json_error_response(503, "data_source_error", str(exc), None)
    return _json_error_response(500, "internal_error", "An internal error occurred while handling the request.", None)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
