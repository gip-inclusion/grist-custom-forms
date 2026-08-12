"""Shared FINESS normalization rules for FAGERH analytics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FinessDiagnostic:
    raw: str | None
    normalized: str | None
    issue_code: str | None
    detail: str | None


def normalize_finess(value: object) -> str | None:
    text = _coerce_text(value)
    if text is None:
        return None
    if len(text) == 8 and text.isdigit():
        return f"0{text}"
    if len(text) == 9 and text.isdigit():
        return text
    return None


def diagnose_finess(value: object) -> FinessDiagnostic:
    raw = _coerce_text(value)
    if raw is None:
        return FinessDiagnostic(None, None, "missing_finess", "empty")
    if len(raw) == 8 and raw.isdigit():
        return FinessDiagnostic(raw, f"0{raw}", "normalized_finess", "leading_zero_added")
    if len(raw) == 9 and raw.isdigit():
        return FinessDiagnostic(raw, raw, None, None)
    if not raw.isdigit():
        return FinessDiagnostic(raw, None, "invalid_finess", "non_digit")
    if len(raw) < 8:
        return FinessDiagnostic(raw, None, "invalid_finess", "too_short")
    if len(raw) > 9:
        return FinessDiagnostic(raw, None, "invalid_finess", "too_long")
    return FinessDiagnostic(raw, None, "invalid_finess", "unsupported_length")


def _coerce_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).replace(" ", "").strip()
    return text or None
