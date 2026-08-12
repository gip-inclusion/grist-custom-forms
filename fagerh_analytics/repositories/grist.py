"""Read-only Grist repository for FAGERH analytics."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlparse

import requests

from fagerh_analytics.domain import RawQuestionnaireRecord
from fagerh_analytics.finess import normalize_finess
from fagerh_analytics.geography import normalize_department_code, resolve_region_code
from fagerh_analytics.repositories.base import (
    QuestionnaireRepository,
    RepositoryConfigurationError,
    RepositoryConnectionError,
    RepositoryResponseError,
)
from fagerh_analytics.schema import SchemaValidationResult, validate_schema_columns


DEFAULT_PAGE_SIZE = 5000
DEFAULT_MAX_PAGES = 100
DEFAULT_TIMEOUT_SECONDS = 10.0
REQUIRED_FIELD_NAMES = (
    "uuid",
    "campaign_year",
    "annee",
    "campagne",
    "es_departement",
    "finess_main",
    "dispositif",
    "check_esrp",
    "check_espo",
    "check_ueros",
    "check_deac",
    "q38_dui",
    "q40_remuneration",
    "q40_operateur",
    "q45_cpts",
    "q46_cpt",
    "q47_clsm",
    "q48_cle",
    "q49_cre",
    "q50_fiphfp",
    "q51_plith",
    "q53_accompagnes__esrp",
    "q53_accompagnes__espo",
    "q53_accompagnes__ueros",
    "q53_accompagnes__deac",
    "prestations_json",
    "prestations_details_json",
)


class GristQuestionnaireRepository(QuestionnaireRepository):
    """Read-only adapter over the FAGERH Grist questionnaire table."""

    repository_name = "grist"

    def __init__(
        self,
        *,
        base_url: str,
        doc_id: str | None,
        table_id: str | None,
        api_key: str | None,
        session: requests.Session | Any | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
        max_pages: int = DEFAULT_MAX_PAGES,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.base_url = str(base_url or "").rstrip("/")
        self.doc_id = str(doc_id or "").strip()
        self.table_id = str(table_id or "").strip()
        self.page_size = int(page_size)
        self.max_pages = int(max_pages)
        self.timeout_seconds = float(timeout_seconds)
        self._session = session or requests.Session()
        self._cached_rows: list[RawQuestionnaireRecord] | None = None
        self._cached_column_ids: set[str] | None = None
        self._headers = {
            "Authorization": f"Bearer {self._validate_required('GRIST_API_KEY_FAGERH', api_key)}",
            "Accept": "application/json",
        }
        self._validate_base_url(self.base_url)
        self._validate_required("GRIST_DOC_FAGERH", self.doc_id)
        self._validate_required("GRIST_TABLE_FAGERH", self.table_id)
        if self.page_size <= 0:
            raise RepositoryConfigurationError("Invalid FAGERH analytics repository configuration: page_size must be positive.")
        if self.max_pages <= 0:
            raise RepositoryConfigurationError("Invalid FAGERH analytics repository configuration: max_pages must be positive.")
        if self.timeout_seconds <= 0:
            raise RepositoryConfigurationError("Invalid FAGERH analytics repository configuration: timeout_seconds must be positive.")

    def list_raw_questionnaires(self) -> list[RawQuestionnaireRecord]:
        if self._cached_rows is not None:
            return list(self._cached_rows)
        records: list[RawQuestionnaireRecord] = []
        offset = 0
        page_index = 0
        while True:
            if page_index >= self.max_pages:
                raise RepositoryResponseError(
                    "FAGERH analytics data source stopped after the configured page safety limit."
                )
            payload = self._fetch_page(offset=offset)
            page_records = payload.get("records")
            if not isinstance(page_records, list):
                raise RepositoryResponseError("FAGERH analytics data source returned an invalid records payload.")
            records.extend(self._normalize_record(record, offset + position) for position, record in enumerate(page_records))
            if len(page_records) < self.page_size:
                self._cached_rows = list(records)
                return list(self._cached_rows)
            page_index += 1
            offset += self.page_size

    def check_connection(self) -> None:
        """Perform a read-only one-row probe against the configured Grist table."""

        payload = self._fetch_page(offset=0, limit=1)
        page_records = payload.get("records")
        if not isinstance(page_records, list):
            raise RepositoryResponseError("FAGERH analytics data source returned an invalid records payload.")

    def validate_schema(self) -> SchemaValidationResult:
        """Read the Grist column metadata and validate the minimal analytics contract."""

        return validate_schema_columns(self._fetch_column_ids())

    def _fetch_page(self, *, offset: int, limit: int | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/api/docs/{self.doc_id}/tables/{self.table_id}/records"
        params = {
            "limit": self.page_size if limit is None else limit,
            "offset": offset,
        }
        try:
            response = self._session.get(
                url,
                headers=self._headers,
                params=params,
                timeout=self.timeout_seconds,
            )
        except requests.exceptions.Timeout as exc:
            raise RepositoryConnectionError("FAGERH analytics data source timed out.") from exc
        except requests.exceptions.RequestException as exc:
            raise RepositoryConnectionError("FAGERH analytics data source is unreachable.") from exc

        if response.status_code != 200:
            raise RepositoryResponseError(
                f"FAGERH analytics data source returned HTTP {response.status_code}."
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise RepositoryResponseError("FAGERH analytics data source returned invalid JSON.") from exc
        if not isinstance(payload, dict):
            raise RepositoryResponseError("FAGERH analytics data source returned an unexpected JSON payload.")
        return payload

    def _fetch_column_ids(self) -> set[str]:
        if self._cached_column_ids is not None:
            return set(self._cached_column_ids)
        url = f"{self.base_url}/api/docs/{self.doc_id}/tables/{self.table_id}/columns"
        try:
            response = self._session.get(
                url,
                headers=self._headers,
                timeout=self.timeout_seconds,
            )
        except requests.exceptions.Timeout as exc:
            raise RepositoryConnectionError("FAGERH analytics schema source timed out.") from exc
        except requests.exceptions.RequestException as exc:
            raise RepositoryConnectionError("FAGERH analytics schema source is unreachable.") from exc

        if response.status_code != 200:
            raise RepositoryResponseError(
                f"FAGERH analytics schema source returned HTTP {response.status_code}."
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise RepositoryResponseError("FAGERH analytics schema source returned invalid JSON.") from exc
        if not isinstance(payload, dict):
            raise RepositoryResponseError("FAGERH analytics schema source returned an unexpected JSON payload.")
        columns = payload.get("columns")
        if not isinstance(columns, list):
            raise RepositoryResponseError("FAGERH analytics schema source returned an invalid columns payload.")
        column_ids: set[str] = set()
        for item in columns:
            if not isinstance(item, dict):
                raise RepositoryResponseError("FAGERH analytics schema source returned a malformed column metadata item.")
            column_id = item.get("id")
            if not isinstance(column_id, str) or not column_id.strip():
                raise RepositoryResponseError("FAGERH analytics schema source returned a malformed column identifier.")
            column_ids.add(column_id)
        self._cached_column_ids = set(column_ids)
        return set(self._cached_column_ids)

    def _normalize_record(self, record: object, row_index: int) -> RawQuestionnaireRecord:
        if not isinstance(record, dict):
            raise RepositoryResponseError("FAGERH analytics data source returned a malformed record.")
        fields = record.get("fields")
        if not isinstance(fields, dict):
            raise RepositoryResponseError("FAGERH analytics data source returned a record without fields.")

        normalized_raw = dict(fields)
        if "id" in record:
            normalized_raw["id"] = record.get("id")

        return RawQuestionnaireRecord(
            uuid=_coerce_text(_pick_first(fields, "uuid")),
            campaign_year=_coerce_campaign_year(_pick_first(fields, "campaign_year", "annee", "campagne")),
            region_code=resolve_region_code(normalize_department_code(_pick_first(fields, "department_code", "es_departement", "departement"))),
            department_code=normalize_department_code(_pick_first(fields, "department_code", "es_departement", "departement")),
            finess_main=_coerce_finess(_pick_first(fields, "finess_main")),
            completion_status=_coerce_completion_status(fields.get("saisie_terminee")),
            dispositif_hint=_coerce_text(_pick_first(fields, "dispositif")),
            check_esrp=fields.get("check_esrp"),
            check_espo=fields.get("check_espo"),
            check_ueros=fields.get("check_ueros"),
            check_deac=fields.get("check_deac"),
            q38_dui=_coerce_text(_pick_first(fields, "q38_dui")),
            q40_remuneration=_coerce_text(_pick_first(fields, "q40_remuneration")),
            q40_operateur=_coerce_text(_pick_first(fields, "q40_operateur")),
            q53_accompagnes__esrp=fields.get("q53_accompagnes__esrp"),
            q53_accompagnes__espo=fields.get("q53_accompagnes__espo"),
            q53_accompagnes__ueros=fields.get("q53_accompagnes__ueros"),
            q53_accompagnes__deac=fields.get("q53_accompagnes__deac"),
            prestations_json=_coerce_json_object(fields.get("prestations_json"), field_name="prestations_json", row_index=row_index),
            prestations_details_json=_coerce_json_object(fields.get("prestations_details_json"), field_name="prestations_details_json", row_index=row_index),
            raw=normalized_raw,
        )

    def _validate_required(self, env_name: str, value: object) -> str:
        normalized = str(value or "").strip()
        if not normalized:
            raise RepositoryConfigurationError(
                f"Missing required FAGERH analytics configuration: {env_name}."
            )
        return normalized

    def _validate_base_url(self, value: object) -> str:
        normalized = self._validate_required("GRIST_BASE_URL", value)
        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise RepositoryConfigurationError("Invalid FAGERH analytics repository configuration: GRIST_BASE_URL must be a valid HTTP URL.")
        return normalized


def _coerce_completion_status(value: object) -> str | None:
    if value is True:
        return "completed"
    if value is False:
        return "in_progress"
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "oui", "yes", "1"}:
            return "completed"
        if normalized in {"false", "non", "no", "0"}:
            return "in_progress"
    return None


def _pick_first(fields: dict[str, Any], *names: str) -> object | None:
    for name in names:
        if name in fields and fields.get(name) is not None:
            return fields.get(name)
    return None


def _coerce_text(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def _coerce_finess(value: object) -> str | None:
    return normalize_finess(value)


def _coerce_campaign_year(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise RepositoryResponseError("FAGERH analytics data source returned an invalid campaign year.")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not value.is_integer():
            raise RepositoryResponseError("FAGERH analytics data source returned an invalid campaign year.")
        return int(value)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        try:
            decimal_value = Decimal(normalized)
        except InvalidOperation as exc:
            raise RepositoryResponseError("FAGERH analytics data source returned an invalid campaign year.") from exc
        if decimal_value != decimal_value.to_integral_value():
            raise RepositoryResponseError("FAGERH analytics data source returned an invalid campaign year.")
        return int(decimal_value)
    raise RepositoryResponseError("FAGERH analytics data source returned an invalid campaign year.")


def _coerce_json_object(value: object, *, field_name: str, row_index: int) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return {}
        try:
            parsed = json.loads(normalized)
        except json.JSONDecodeError as exc:
            raise RepositoryResponseError(
                f"FAGERH analytics data source returned invalid JSON in {field_name} for row {row_index}."
            ) from exc
        if isinstance(parsed, dict):
            return parsed
        raise RepositoryResponseError(
            f"FAGERH analytics data source returned a non-object JSON payload in {field_name} for row {row_index}."
        )
    raise RepositoryResponseError(
        f"FAGERH analytics data source returned an unsupported JSON payload in {field_name} for row {row_index}."
    )
