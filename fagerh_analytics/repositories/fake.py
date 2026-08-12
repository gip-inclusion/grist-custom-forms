"""Fake repository backed by in-memory test data."""

from __future__ import annotations

import json

from fagerh_analytics.domain import RawQuestionnaireRecord
from fagerh_analytics.finess import normalize_finess
from fagerh_analytics.repositories.base import QuestionnaireRepository


class FakeQuestionnaireRepository(QuestionnaireRepository):
    """Simple in-memory repository used by unit tests."""

    repository_name = "fake"

    def __init__(self, rows: list[dict[str, object]] | None = None) -> None:
        self._rows = rows or []

    def list_raw_questionnaires(self) -> list[RawQuestionnaireRecord]:
        return [
            RawQuestionnaireRecord(
                uuid=_coerce_uuid(row.get("uuid")),
                campaign_year=_coerce_int(row.get("campaign_year")),
                region_code=_coerce_uuid(row.get("region_code")),
                department_code=_coerce_uuid(row.get("department_code")),
                finess_main=normalize_finess(row.get("finess_main")),
                completion_status=_coerce_completion_status(row.get("saisie_terminee")),
                dispositif_hint=_coerce_uuid(row.get("dispositif")),
                check_esrp=_coerce_flag_value(row, "esrp"),
                check_espo=_coerce_flag_value(row, "espo"),
                check_ueros=_coerce_flag_value(row, "ueros"),
                check_deac=_coerce_flag_value(row, "deac"),
                q38_dui=_coerce_uuid(row.get("q38_dui")),
                q40_remuneration=_coerce_uuid(row.get("q40_remuneration")),
                q40_operateur=_coerce_uuid(row.get("q40_operateur")),
                q53_accompagnes__esrp=row.get("q53_accompagnes__esrp"),
                q53_accompagnes__espo=row.get("q53_accompagnes__espo"),
                q53_accompagnes__ueros=row.get("q53_accompagnes__ueros"),
                q53_accompagnes__deac=row.get("q53_accompagnes__deac"),
                prestations_json=_coerce_dict(row.get("prestations_json")),
                prestations_details_json=_coerce_dict(row.get("prestations_details_json")),
                raw=dict(row),
            )
            for row in self._rows
        ]

    def list_available_campaign_years(self) -> tuple[int, ...]:
        return tuple(sorted({
            campaign_year
            for campaign_year in (_coerce_int(row.get("campaign_year")) for row in self._rows)
            if isinstance(campaign_year, int) and campaign_year > 0
        }))


def _coerce_uuid(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _coerce_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        return int(normalized)
    return int(value)


def _coerce_dict(value: object) -> dict[str, object]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return {}
        parsed = json.loads(normalized)
        if isinstance(parsed, dict):
            return parsed
    raise TypeError("Expected prestations_json to be a dict or JSON object string")


def _coerce_flag_value(row: dict[str, object], dispositif: str) -> object | None:
    explicit_key = f"check_{dispositif}"
    if explicit_key in row:
        return row.get(explicit_key)
    legacy_dispositif = _coerce_uuid(row.get("dispositif"))
    if legacy_dispositif and legacy_dispositif.strip().lower() == dispositif:
        return True
    if legacy_dispositif:
        return False
    return None


def _coerce_completion_status(value: object) -> str | None:
    if value is True:
        return "completed"
    if value is False:
        return "in_progress"
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "oui", "yes", "1", "completed"}:
            return "completed"
        if normalized in {"false", "non", "no", "0", "in_progress"}:
            return "in_progress"
    return None
