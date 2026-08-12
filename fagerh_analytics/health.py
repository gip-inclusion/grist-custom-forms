"""Health check helpers for the FAGERH analytics module."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable
from urllib.parse import urlparse

from .api import API_VERSION
from .repositories.base import (
    QuestionnaireRepository,
    RepositoryConfigurationError,
    RepositoryConnectionError,
    RepositoryResponseError,
)
from .schema import SchemaValidationResult


@dataclass(frozen=True)
class ConfigurationCheckResult:
    """Validated configuration snapshot for the analytics module."""

    base_url: str
    doc_id: str
    table_id: str
    api_key: str
    page_size: int
    max_pages: int
    timeout_seconds: float


@dataclass(frozen=True)
class HealthProbeResult:
    """Normalized health payload for the analytics module."""

    http_status: int
    status: str
    analytics_status: str
    checks: dict[str, str]
    error: dict[str, str] | None
    generated_at: str
    warnings: tuple[str, ...] = ()
    unavailable_capabilities: tuple[str, ...] = ()


def check_fagerh_analytics_configuration(
    env: dict[str, str] | None = None,
) -> ConfigurationCheckResult:
    """Validate FAGERH analytics configuration without contacting Grist."""

    source = env or {}
    base_url = _require_non_empty(source, "GRIST_BASE_URL")
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RepositoryConfigurationError("FAGERH Analytics configuration is incomplete.")

    doc_id = _require_non_empty(source, "GRIST_DOC_FAGERH")
    table_id = _require_non_empty(source, "GRIST_TABLE_FAGERH")
    api_key = _require_non_empty(source, "GRIST_API_KEY_FAGERH")
    page_size = _parse_positive_int(source.get("FAGERH_ANALYTICS_GRIST_PAGE_SIZE"), default=5000)
    max_pages = _parse_positive_int(source.get("FAGERH_ANALYTICS_GRIST_MAX_PAGES"), default=100)
    timeout_seconds = _parse_positive_float(source.get("FAGERH_ANALYTICS_GRIST_TIMEOUT_SECONDS"), default=10.0)
    return ConfigurationCheckResult(
        base_url=base_url.rstrip("/"),
        doc_id=doc_id,
        table_id=table_id,
        api_key=api_key,
        page_size=page_size,
        max_pages=max_pages,
        timeout_seconds=timeout_seconds,
    )


def build_fagerh_analytics_health_probe(
    *,
    repository_factory: Callable[[], QuestionnaireRepository],
    cache_ttl_seconds: int = 30,
    now_provider: Callable[[], datetime] | None = None,
) -> Callable[[], HealthProbeResult]:
    """Build a small in-memory cached health probe for the analytics module."""

    ttl = max(int(cache_ttl_seconds), 0)
    clock = now_provider or (lambda: datetime.now(timezone.utc))
    cache: dict[str, object] = {"expires_at": None, "result": None}

    def probe() -> HealthProbeResult:
        now = _to_utc(clock())
        cached_result = cache.get("result")
        cached_expiry = cache.get("expires_at")
        if ttl > 0 and isinstance(cached_expiry, datetime) and cached_result is not None and now < cached_expiry:
            return cached_result  # type: ignore[return-value]

        result = _run_health_probe(repository_factory=repository_factory, generated_at=_format_utc(now))
        if ttl > 0:
            cache["result"] = result
            cache["expires_at"] = now + timedelta(seconds=ttl)
        return result

    return probe


def _run_health_probe(
    *,
    repository_factory: Callable[[], QuestionnaireRepository],
    generated_at: str,
) -> HealthProbeResult:
    try:
        repository = repository_factory()
    except RepositoryConfigurationError:
        return _health_error(
            analytics_status="misconfigured",
            checks={"configuration": "error", "repository": "not_checked"},
            code="repository_configuration_error",
            message="FAGERH Analytics configuration is incomplete.",
            generated_at=generated_at,
        )
    except Exception:
        return _health_error(
            analytics_status="unavailable",
            checks={"configuration": "ok", "repository": "error"},
            code="internal_error",
            message="FAGERH Analytics health probe failed.",
            generated_at=generated_at,
        )

    try:
        repository.check_connection()
        schema = repository.validate_schema()
        if not schema.is_compatible:
            return _health_error(
                analytics_status="misconfigured",
                checks={"configuration": "ok", "repository": "ok", "schema": "error"},
                code="repository_schema_error",
                message="FAGERH Analytics schema is incompatible.",
                generated_at=generated_at,
                schema=schema,
            )
        return HealthProbeResult(
            http_status=200,
            status="success",
            analytics_status="available",
            checks={"configuration": "ok", "repository": "ok", "schema": "ok"},
            error=None,
            generated_at=generated_at,
            warnings=tuple(schema.warnings),
            unavailable_capabilities=tuple(schema.unavailable_capabilities),
        )
    except RepositoryConfigurationError:
        return _health_error(
            analytics_status="misconfigured",
            checks={"configuration": "error", "repository": "not_checked", "schema": "not_checked"},
            code="repository_configuration_error",
            message="FAGERH Analytics configuration is incomplete.",
            generated_at=generated_at,
        )
    except (RepositoryConnectionError, RepositoryResponseError):
        return _health_error(
            analytics_status="unavailable",
            checks={"configuration": "ok", "repository": "error", "schema": "not_checked"},
            code="repository_unavailable",
            message="FAGERH Analytics data source is unavailable.",
            generated_at=generated_at,
        )
    except Exception:
        return _health_error(
            analytics_status="unavailable",
            checks={"configuration": "ok", "repository": "error", "schema": "not_checked"},
            code="internal_error",
            message="FAGERH Analytics health probe failed.",
            generated_at=generated_at,
        )


def serialize_health_probe_result(result: HealthProbeResult) -> tuple[dict[str, object], int]:
    """Serialize a health probe result to an HTTP JSON payload."""

    return ({
        "api_version": API_VERSION,
        "status": result.status,
        "analytics_status": result.analytics_status,
        "generated_at": result.generated_at,
        "checks": dict(result.checks),
        "error": None if result.error is None else dict(result.error),
        "warnings": list(result.warnings),
        "unavailable_capabilities": list(result.unavailable_capabilities),
    }, result.http_status)


def _health_error(
    *,
    analytics_status: str,
    checks: dict[str, str],
    code: str,
    message: str,
    generated_at: str,
    schema: SchemaValidationResult | None = None,
) -> HealthProbeResult:
    return HealthProbeResult(
        http_status=503,
        status="error",
        analytics_status=analytics_status,
        checks=checks,
        error={"code": code, "message": message},
        generated_at=generated_at,
        warnings=tuple(schema.warnings) if schema is not None else (),
        unavailable_capabilities=tuple(schema.unavailable_capabilities) if schema is not None else (),
    )


def _require_non_empty(env: dict[str, str], key: str) -> str:
    value = str(env.get(key) or "").strip()
    if not value:
        raise RepositoryConfigurationError("FAGERH Analytics configuration is incomplete.")
    return value


def _parse_positive_int(raw_value: str | None, *, default: int) -> int:
    if raw_value is None or not str(raw_value).strip():
        return default
    value = int(str(raw_value).strip())
    if value <= 0:
        raise RepositoryConfigurationError("FAGERH Analytics configuration is incomplete.")
    return value


def _parse_positive_float(raw_value: str | None, *, default: float) -> float:
    if raw_value is None or not str(raw_value).strip():
        return default
    value = float(str(raw_value).strip())
    if value <= 0:
        raise RepositoryConfigurationError("FAGERH Analytics configuration is incomplete.")
    return value


def _to_utc(moment: datetime) -> datetime:
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)


def _format_utc(moment: datetime) -> str:
    return _to_utc(moment).isoformat().replace("+00:00", "Z")
