import os
import unittest
from unittest.mock import patch

import requests

import app
from fagerh_analytics.repositories.base import (
    RepositoryConfigurationError,
    RepositoryConnectionError,
    RepositoryResponseError,
)
from fagerh_analytics.repositories.fake import FakeQuestionnaireRepository
from fagerh_analytics.repositories.grist import GristQuestionnaireRepository


class GristQuestionnaireRepositoryTest(unittest.TestCase):
    def test_complete_fagerh_configuration_builds_grist_repository(self):
        with patch.dict(os.environ, {
            "GRIST_DOC_FAGERH": "doc-fagerh",
            "GRIST_TABLE_FAGERH": "table-fagerh",
            "GRIST_API_KEY_FAGERH": "token-fagerh",
            "GRIST_DOC_EURES_BETA": "doc-eures",
            "GRIST_TABLE_EURES_BETA": "table-eures",
            "GRIST_API_KEY_EURES_BETA": "token-eures",
        }, clear=False):
            repository = app.get_fagerh_analytics_repository()

        self.assertIsInstance(repository, GristQuestionnaireRepository)
        self.assertEqual(repository.doc_id, "doc-fagerh")
        self.assertEqual(repository.table_id, "table-fagerh")

    def test_missing_configuration_raises_error_and_not_empty_dataset(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GRIST_DOC_FAGERH", None)
            os.environ.pop("GRIST_TABLE_FAGERH", None)
            os.environ.pop("GRIST_API_KEY_FAGERH", None)
            with self.assertRaises(RepositoryConfigurationError):
                app.get_fagerh_analytics_repository()

    def test_eures_variables_are_not_used_as_fallback(self):
        with patch.dict(os.environ, {
            "GRIST_DOC_EURES_BETA": "doc-eures",
            "GRIST_TABLE_EURES_BETA": "table-eures",
            "GRIST_API_KEY_EURES_BETA": "token-eures",
        }, clear=False):
            os.environ.pop("GRIST_DOC_FAGERH", None)
            os.environ.pop("GRIST_TABLE_FAGERH", None)
            os.environ.pop("GRIST_API_KEY_FAGERH", None)
            with self.assertRaises(RepositoryConfigurationError):
                app.get_fagerh_analytics_repository()

    def test_missing_api_key_raises_configuration_error(self):
        with self.assertRaises(RepositoryConfigurationError):
            self._make_repository(api_key=None)

    def test_missing_table_raises_configuration_error(self):
        with self.assertRaises(RepositoryConfigurationError):
            self._make_repository(table_id=None)

    def test_missing_document_raises_configuration_error(self):
        with self.assertRaises(RepositoryConfigurationError):
            self._make_repository(doc_id=None)

    def test_single_page_is_converted_correctly(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {
                "records": [
                    {"id": 1, "fields": self._make_fields()},
                ],
            }),
        ]))

        rows = repository.list_raw_questionnaires()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].uuid, "uuid-1")
        self.assertEqual(rows[0].campaign_year, 2025)
        self.assertEqual(rows[0].finess_main, "010000001")
        self.assertEqual(rows[0].department_code, "69")
        self.assertEqual(rows[0].region_code, "84")
        self.assertEqual(rows[0].prestations_json, {"a": {"indirect": {"rows": {}}}})
        self.assertIn("prestations_details_json", rows[0].raw)

    def test_missing_campaign_is_accepted_and_preserved_as_none(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(campaign_year=None, annee=None, campagne=None)},
            ]}),
        ]))

        rows = repository.list_raw_questionnaires()

        self.assertIsNone(rows[0].campaign_year)

    def test_department_2b_is_normalized_and_region_is_derived(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(department_code=None, es_departement="2b", region_code=None)},
            ]}),
        ]))

        rows = repository.list_raw_questionnaires()

        self.assertEqual(rows[0].department_code, "2B")
        self.assertEqual(rows[0].region_code, "94")

    def test_numeric_department_keeps_metropolitan_leading_zero(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(department_code=None, es_departement=1, region_code=None)},
            ]}),
        ]))

        rows = repository.list_raw_questionnaires()

        self.assertEqual(rows[0].department_code, "01")
        self.assertEqual(rows[0].region_code, "84")

    def test_multiple_pages_are_concatenated(self):
        repository = self._make_repository(
            page_size=2,
            session=FakeSession([
                FakeResponse(200, {"records": [
                    {"id": 1, "fields": self._make_fields(uuid="uuid-1")},
                    {"id": 2, "fields": self._make_fields(uuid="uuid-2")},
                ]}),
                FakeResponse(200, {"records": [
                    {"id": 3, "fields": self._make_fields(uuid="uuid-3")},
                ]}),
            ]),
        )

        rows = repository.list_raw_questionnaires()

        self.assertEqual([row.uuid for row in rows], ["uuid-1", "uuid-2", "uuid-3"])

    def test_list_raw_questionnaires_is_cached_after_first_read(self):
        session = FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(uuid="uuid-1")},
            ]}),
        ])
        repository = self._make_repository(session=session)

        first = repository.list_raw_questionnaires()
        second = repository.list_raw_questionnaires()

        self.assertEqual([row.uuid for row in first], ["uuid-1"])
        self.assertEqual([row.uuid for row in second], ["uuid-1"])
        self.assertEqual(len(session.calls), 1)

    def test_empty_dataset_is_accepted(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": []}),
        ]))

        rows = repository.list_raw_questionnaires()

        self.assertEqual(rows, [])

    def test_last_partial_page_stops_iteration(self):
        session = FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(uuid="uuid-1")},
                {"id": 2, "fields": self._make_fields(uuid="uuid-2")},
            ]}),
            FakeResponse(200, {"records": [
                {"id": 3, "fields": self._make_fields(uuid="uuid-3")},
            ]}),
        ])
        repository = self._make_repository(page_size=2, session=session)

        repository.list_raw_questionnaires()

        self.assertEqual([call["params"]["offset"] for call in session.calls], [0, 2])

    def test_validate_schema_reuses_cached_column_ids(self):
        session = FakeSession([
            FakeResponse(200, {"columns": [
                {"id": "uuid"},
                {"id": "finess_main"},
                {"id": "es_departement"},
                {"id": "prestations_json"},
                {"id": "prestations_details_json"},
            ]}),
        ])
        repository = self._make_repository(session=session)

        repository.validate_schema()
        repository.validate_schema()

        self.assertEqual(len(session.calls), 1)

    def test_http_error_during_pagination_raises_structured_error(self):
        repository = self._make_repository(
            page_size=2,
            session=FakeSession([
                FakeResponse(200, {"records": [
                    {"id": 1, "fields": self._make_fields(uuid="uuid-1")},
                    {"id": 2, "fields": self._make_fields(uuid="uuid-2")},
                ]}),
                FakeResponse(503, {"error": "boom"}),
            ]),
        )

        with self.assertRaises(RepositoryResponseError) as ctx:
            repository.list_raw_questionnaires()

        self.assertIn("HTTP 503", str(ctx.exception))

    def test_timeout_raises_structured_error(self):
        repository = self._make_repository(session=TimeoutSession())

        with self.assertRaises(RepositoryConnectionError) as ctx:
            repository.list_raw_questionnaires()

        self.assertNotIn("token-fagerh", str(ctx.exception))

    def test_valid_json_string_is_decoded(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(prestations_json='{"a":{"indirect":{"rows":{}}}}')},
            ]}),
        ]))

        rows = repository.list_raw_questionnaires()

        self.assertEqual(rows[0].prestations_json, {"a": {"indirect": {"rows": {}}}})

    def test_decoded_json_object_is_preserved(self):
        payload = {"a": {"indirect": {"rows": {}}}}
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(prestations_json=payload)},
            ]}),
        ]))

        rows = repository.list_raw_questionnaires()

        self.assertEqual(rows[0].prestations_json, payload)

    def test_invalid_json_raises_explicit_error(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(prestations_json="{invalid")},
            ]}),
        ]))

        with self.assertRaises(RepositoryResponseError) as ctx:
            repository.list_raw_questionnaires()

        self.assertIn("prestations_json", str(ctx.exception))

    def test_finess_keeps_leading_zeroes(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(finess_main="001234567")},
            ]}),
        ]))

        rows = repository.list_raw_questionnaires()

        self.assertEqual(rows[0].finess_main, "001234567")

    def test_eight_digit_finess_is_normalized_on_read(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": [
                {"id": 1, "fields": self._make_fields(finess_main="12345678")},
            ]}),
        ]))

        rows = repository.list_raw_questionnaires()

        self.assertEqual(rows[0].finess_main, "012345678")
        self.assertEqual(rows[0].raw["finess_main"], "12345678")

    def test_read_only_repository_only_uses_get_requests(self):
        session = FakeSession([
            FakeResponse(200, {"records": []}),
        ])
        repository = self._make_repository(session=session)

        repository.list_raw_questionnaires()

        self.assertEqual(session.methods, ["GET"])

    def test_error_messages_do_not_expose_secrets(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(500, {"error": "bad token-fagerh"}),
        ]))

        with self.assertRaises(RepositoryResponseError) as ctx:
            repository.list_raw_questionnaires()

        self.assertNotIn("token-fagerh", str(ctx.exception))

    def test_factory_injection_can_still_use_fake_repository(self):
        repository = FakeQuestionnaireRepository(rows=[{"campaign_year": 2025}])

        self.assertEqual(repository.repository_name, "fake")

    def test_freshness_remains_unknown(self):
        repository = self._make_repository(session=FakeSession([
            FakeResponse(200, {"records": []}),
        ]))

        self.assertIsNone(repository.get_freshness_at())

    def _make_repository(
        self,
        *,
        doc_id="doc-fagerh",
        table_id="table-fagerh",
        api_key="token-fagerh",
        session=None,
        page_size=5000,
    ):
        return GristQuestionnaireRepository(
            base_url="https://grist.example.test",
            doc_id=doc_id,
            table_id=table_id,
            api_key=api_key,
            session=session,
            page_size=page_size,
            max_pages=3,
            timeout_seconds=1,
        )

    def _make_fields(self, **overrides):
        fields = {
            "uuid": "uuid-1",
            "campaign_year": "2025",
            "region_code": "84",
            "department_code": "69",
            "es_departement": "69",
            "finess_main": "010000001",
            "check_esrp": True,
            "check_espo": False,
            "check_ueros": False,
            "check_deac": False,
            "q38_dui": "Oui",
            "q40_remuneration": "Oui",
            "q40_operateur": "ASP",
            "q53_accompagnes__esrp": 7,
            "q53_accompagnes__espo": 0,
            "q53_accompagnes__ueros": 0,
            "q53_accompagnes__deac": 0,
            "prestations_json": {"a": {"indirect": {"rows": {}}}},
            "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": []}}},
        }
        fields.update(overrides)
        return fields


class FakeSession:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
        self.methods = []

    def get(self, url, *, headers, params=None, timeout=None):
        self.calls.append({"url": url, "headers": dict(headers), "params": dict(params or {}), "timeout": timeout})
        self.methods.append("GET")
        return self._responses.pop(0)


class TimeoutSession:
    def get(self, url, *, headers, params=None, timeout=None):
        raise requests.exceptions.Timeout("late")


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


if __name__ == "__main__":
    unittest.main()
