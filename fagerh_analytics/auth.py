"""Authentication helpers for the FAGERH analytics browser surface."""

from __future__ import annotations

from urllib.parse import urlparse

from flask import current_app, request, session


FAGERH_ANALYTICS_SESSION_KEY = "fagerh_analytics_authenticated"
FAGERH_ANALYTICS_ROLE_KEY = "fagerh_analytics_role"


def has_session_signing_key() -> bool:
    """Return whether Flask session cookies are safely signed."""
    return bool(current_app.secret_key)


def mark_fagerh_analytics_session_authenticated(*, role: str = "admin_global") -> None:
    """Persist a minimal signed marker for subsequent same-origin API calls."""
    if not has_session_signing_key():
        raise RuntimeError("FAGERH Analytics session signing is not configured.")
    session[FAGERH_ANALYTICS_SESSION_KEY] = True
    session[FAGERH_ANALYTICS_ROLE_KEY] = role
    session.permanent = False
    session.modified = True


def clear_fagerh_analytics_session() -> None:
    """Remove the FAGERH analytics marker from the current session."""
    session.pop(FAGERH_ANALYTICS_SESSION_KEY, None)
    session.pop(FAGERH_ANALYTICS_ROLE_KEY, None)


def is_fagerh_analytics_session_authenticated() -> bool:
    """Return whether the current signed session grants FAGERH analytics access."""
    if session.get(FAGERH_ANALYTICS_SESSION_KEY) is not True:
        return False
    return session.get(FAGERH_ANALYTICS_ROLE_KEY) == "admin_global"


def get_fagerh_analytics_session_role() -> str | None:
    """Return the current session role when the marker is present."""
    if not is_fagerh_analytics_session_authenticated():
        return None
    role = session.get(FAGERH_ANALYTICS_ROLE_KEY)
    return str(role) if role else None


def is_same_origin_request() -> bool:
    """Accept only same-origin browser POST requests when relying on session auth."""
    origin = str(request.headers.get("Origin") or "").strip()
    referer = str(request.headers.get("Referer") or "").strip()
    current_origin = _origin_from_url(request.host_url)
    if origin:
        return _origin_from_url(origin) == current_origin
    if referer:
        return _origin_from_url(referer) == current_origin
    return False


def _origin_from_url(raw_url: str) -> str:
    parsed = urlparse(str(raw_url or "").strip())
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"
