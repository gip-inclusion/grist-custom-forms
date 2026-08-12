"""Centralized analytical permission scopes for the FAGERH analytics engine."""

from __future__ import annotations

from .domain import PermissionScope, UserContext


ALL_DISPOSITIFS = ("deac", "espo", "esrp", "ueros")
DEVICE_GRAIN_INDICATORS = {
    "people.received.esrp": "esrp",
    "people.received.espo": "espo",
    "people.received.ueros": "ueros",
    "people.received.deac": "deac",
}
REQUIRED_ALL_TOTAL_DISPOSITIFS = {"esrp", "espo", "ueros"}


class InvalidUserContextError(ValueError):
    """Raised when a user context is incomplete or incoherent."""


class PermissionDeniedError(ValueError):
    """Raised when a user tries to access data outside their scope."""


def get_scope(user_context: UserContext | None) -> PermissionScope:
    """Resolve the effective analytical permission scope."""

    if user_context is None:
        return PermissionScope(
            is_global=True,
            region_codes=(),
            department_codes=(),
            finess_values=(),
            allowed_dispositifs=(),
            can_export=True,
            role="admin_global",
        )

    role = str(user_context.role or "").strip()
    if role not in {"admin_global", "national_readonly", "regional_user", "establishment_user"}:
        raise InvalidUserContextError(f"Invalid user context role={user_context.role!r}: unknown role")

    region_codes = _normalize_code_collection(user_context.region_codes)
    department_codes = _normalize_code_collection(user_context.department_codes)
    finess_values = _normalize_finess_collection(user_context.finess_values)
    allowed_dispositifs = _normalize_dispositif_collection(user_context.allowed_dispositifs)

    if role == "admin_global":
        return PermissionScope(True, (), (), (), allowed_dispositifs, True, role)

    if role == "national_readonly":
        return PermissionScope(True, (), (), (), allowed_dispositifs, False, role)

    if role == "regional_user":
        if not region_codes:
            raise InvalidUserContextError("Invalid user context role='regional_user': region_codes is required")
        return PermissionScope(False, region_codes, department_codes, finess_values, allowed_dispositifs, False, role)

    if role == "establishment_user":
        if not finess_values:
            raise InvalidUserContextError("Invalid user context role='establishment_user': finess_values is required")
        return PermissionScope(False, region_codes, department_codes, finess_values, allowed_dispositifs, False, role)

    raise InvalidUserContextError(f"Invalid user context role={user_context.role!r}: unknown role")


def ensure_export_allowed(scope: PermissionScope) -> None:
    """Raise when export is forbidden for the current scope."""

    if not scope.can_export:
        raise PermissionDeniedError(f"Permission denied for role={scope.role!r}: export is not allowed")


def ensure_indicator_scope_allowed(indicator_id: str, scope: PermissionScope, compatible_filters: tuple[str, ...]) -> None:
    """Raise when a scope makes an indicator unavailable."""

    allowed_dispositifs = set(scope.allowed_dispositifs)
    if not allowed_dispositifs:
        return

    required_dispositif = DEVICE_GRAIN_INDICATORS.get(indicator_id)
    if required_dispositif is not None and required_dispositif not in allowed_dispositifs:
        raise PermissionDeniedError(
            f"Permission denied for role={scope.role!r}: indicator {indicator_id} is outside allowed dispositifs"
        )

    if indicator_id == "people.received.all" and not REQUIRED_ALL_TOTAL_DISPOSITIFS.issubset(allowed_dispositifs):
        raise PermissionDeniedError(
            f"Permission denied for role={scope.role!r}: indicator people.received.all requires esrp, espo and ueros access"
        )

    # Transverse indicators incompatible with dispositifs remain accessible territorially.
    if "dispositifs" not in compatible_filters:
        return


def _normalize_code_collection(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    normalized = tuple(sorted({
        str(value).strip().upper()
        for value in (values or ())
        if str(value).strip()
    }))
    return normalized


def _normalize_finess_collection(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    normalized = []
    for value in values or ():
        compact = str(value).replace(" ", "").strip()
        if not compact:
            continue
        if len(compact) != 9 or not compact.isdigit():
            raise InvalidUserContextError(f"Invalid user context finess_values={value!r}: expected 9 digits")
        normalized.append(compact)
    return tuple(sorted(set(normalized)))


def _normalize_dispositif_collection(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    normalized = []
    for value in values or ():
        compact = str(value).strip().lower()
        if not compact:
            continue
        if compact not in ALL_DISPOSITIFS:
            raise InvalidUserContextError(
                f"Invalid user context allowed_dispositifs={value!r}: expected one of esrp, espo, ueros, deac"
            )
        normalized.append(compact)
    return tuple(sorted(set(normalized)))
