import base64
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import app
from fagerh_analytics.api import IndicatorQuery, execute_indicator_query, list_available_indicators
from fagerh_analytics.domain import UserContext
from fagerh_analytics.health import build_fagerh_analytics_health_probe
from fagerh_analytics.repositories.base import (
    QuestionnaireRepository,
    RepositoryConnectionError,
    RepositoryResponseError,
)
from fagerh_analytics.repositories.fake import FakeQuestionnaireRepository
from fagerh_analytics.schema import (
    SchemaValidationResult,
    ensure_indicator_schema_available,
    validate_schema_columns,
)


ALL_COLUMNS = {
    "uuid",
    "finess_main",
    "es_departement",
    "check_esrp",
    "check_espo",
    "check_ueros",
    "check_deac",
    "q38_dui",
    "q40_remuneration",
    "q40_operateur",
    "q53_accompagnes__esrp",
    "q53_accompagnes__espo",
    "q53_accompagnes__ueros",
    "q53_accompagnes__deac",
    "prestations_json",
    "prestations_details_json",
}


class SchemaValidationTest(unittest.TestCase):
    def test_all_expected_columns_are_compatible(self):
        result = validate_schema_columns(set(ALL_COLUMNS))

        self.assertTrue(result.is_compatible)
        self.assertEqual(result.core_status, "ok")
        self.assertIn("geography", result.available_capabilities)

    def test_missing_uuid_makes_schema_incompatible(self):
        result = validate_schema_columns(set(ALL_COLUMNS) - {"uuid"})

        self.assertFalse(result.is_compatible)
        self.assertIn("uuid", result.missing_required_columns)

    def test_missing_finess_main_makes_schema_incompatible(self):
        result = validate_schema_columns(set(ALL_COLUMNS) - {"finess_main"})

        self.assertFalse(result.is_compatible)
        self.assertIn("finess_main", result.missing_required_columns)

    def test_missing_dui_only_disables_dui_capability(self):
        result = validate_schema_columns(set(ALL_COLUMNS) - {"q38_dui"})

        self.assertTrue(result.is_compatible)
        self.assertIn("dui", result.unavailable_capabilities)
        self.assertNotIn("remuneration", result.unavailable_capabilities)

    def test_missing_remuneration_only_disables_remuneration_capability(self):
        result = validate_schema_columns(set(ALL_COLUMNS) - {"q40_operateur"})

        self.assertTrue(result.is_compatible)
        self.assertIn("remuneration", result.unavailable_capabilities)
        self.assertNotIn("dui", result.unavailable_capabilities)

    def test_missing_q53_esrp_disables_only_esrp_indicator_capability(self):
        result = validate_schema_columns(set(ALL_COLUMNS) - {"q53_accompagnes__esrp"})

        self.assertIn("annual_volumes_esrp", result.unavailable_capabilities)
        self.assertNotIn("annual_volumes_espo", result.unavailable_capabilities)

    def test_missing_prestations_json_disables_evaluation_and_mdph_capabilities(self):
        result = validate_schema_columns(set(ALL_COLUMNS) - {"prestations_json"})

        self.assertIn("evaluation_activities", result.unavailable_capabilities)
        self.assertIn("mdph_activities", result.unavailable_capabilities)

    def test_case_difference_is_not_accepted(self):
        result = validate_schema_columns((set(ALL_COLUMNS) - {"uuid"}) | {"UUID"})

        self.assertFalse(result.is_compatible)
        self.assertIn("uuid", result.missing_required_columns)

    def test_approximate_name_is_not_accepted(self):
        result = validate_schema_columns((set(ALL_COLUMNS) - {"q40_operateur"}) | {"q40_operator"})

        self.assertIn("remuneration", result.unavailable_capabilities)

    def test_missing_campaign_does_not_make_core_incompatible(self):
        result = validate_schema_columns(set(ALL_COLUMNS))

        self.assertTrue(result.is_compatible)
        self.assertNotIn("campaign_year", result.missing_required_columns)
        self.assertIn("campaign", result.unavailable_capabilities)

    def test_missing_region_column_does_not_disable_geography_when_department_exists(self):
        result = validate_schema_columns(set(ALL_COLUMNS))

        self.assertIn("geography", result.available_capabilities)


class SchemaIndicatorAvailabilityTest(unittest.TestCase):
    def test_people_received_all_becomes_unavailable_if_component_missing(self):
        repository = SchemaAwareRepository(validate_schema_columns(set(ALL_COLUMNS) - {"q53_accompagnes__espo"}))
        response = execute_indicator_query(
            IndicatorQuery("people.received.all", {}, UserContext("u1", "admin_global")),
            repository,
            generated_at="2026-07-24T12:00:00Z",
        )

        self.assertEqual(response.error["code"], "indicator_unavailable")

    def test_other_indicators_remain_available_when_their_columns_exist(self):
        repository = SchemaAwareRepository(validate_schema_columns(set(ALL_COLUMNS) - {"q38_dui"}))
        response = execute_indicator_query(
            IndicatorQuery("people.received.esrp", {}, UserContext("u1", "admin_global")),
            repository,
            generated_at="2026-07-24T12:00:00Z",
        )

        self.assertEqual(response.status, "success")

    def test_list_available_indicators_reflects_schema_capabilities(self):
        repository = SchemaAwareRepository(validate_schema_columns(set(ALL_COLUMNS) - {"prestations_json"}))
        indicators = list_available_indicators(UserContext("u1", "admin_global"), repository)

        pec = next(item for item in indicators if item["indicator_id"] == "people.received.pec")
        esrp = next(item for item in indicators if item["indicator_id"] == "people.received.esrp")
        self.assertFalse(pec["available"])
        self.assertTrue(esrp["available"])

    def test_missing_q53_esrp_makes_esrp_indicator_unavailable(self):
        repository = SchemaAwareRepository(validate_schema_columns(set(ALL_COLUMNS) - {"q53_accompagnes__esrp"}))
        response = execute_indicator_query(
            IndicatorQuery("people.received.esrp", {}, UserContext("u1", "admin_global")),
            repository,
            generated_at="2026-07-24T12:00:00Z",
        )

        self.assertEqual(response.error["code"], "indicator_unavailable")

    def test_missing_prestations_json_makes_pec_other_eval_and_mdph_unavailable(self):
        repository = SchemaAwareRepository(validate_schema_columns(set(ALL_COLUMNS) - {"prestations_json"}))
        indicators = list_available_indicators(UserContext("u1", "admin_global"), repository)

        for indicator_id in (
            "people.received.pec",
            "people.received.other_eval",
            "institution.mdph.epe.count",
        ):
            item = next(item for item in indicators if item["indicator_id"] == indicator_id)
            self.assertFalse(item["available"])


class SchemaHealthProbeTest(unittest.TestCase):
    def test_invalid_schema_metadata_returns_503(self):
        probe = build_fagerh_analytics_health_probe(
            repository_factory=lambda: InvalidSchemaRepository(),
            cache_ttl_seconds=0,
        )

        result = probe()

        self.assertEqual(result.http_status, 503)
        self.assertEqual(result.analytics_status, "unavailable")

    def test_cache_avoids_two_close_repository_checks(self):
        repository = CountingRepository()
        probe = build_fagerh_analytics_health_probe(
            repository_factory=lambda: repository,
            cache_ttl_seconds=60,
            now_provider=_clock(datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)),
        )

        probe()
        probe()

        self.assertEqual(repository.check_connection_calls, 1)
        self.assertEqual(repository.validate_schema_calls, 1)

    def test_disabled_cache_runs_two_checks(self):
        repository = CountingRepository()
        probe = build_fagerh_analytics_health_probe(
            repository_factory=lambda: repository,
            cache_ttl_seconds=0,
        )

        probe()
        probe()

        self.assertEqual(repository.check_connection_calls, 2)
        self.assertEqual(repository.validate_schema_calls, 2)


class SchemaHttpIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.auth_patch = patch.object(app, "_get_admin_credentials", return_value=("admin", "secret"))
        self.auth_patch.start()
        self.addCleanup(self.auth_patch.stop)

    def test_health_route_stays_unchanged(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_indicator_unavailable_returns_503_json(self):
        token = base64.b64encode(b"admin:secret").decode("ascii")
        with patch.object(app, "get_fagerh_analytics_repository", return_value=SchemaAwareRepository(
            validate_schema_columns(set(ALL_COLUMNS) - {"q53_accompagnes__espo"})
        )):
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/people.received.all",
                headers={"Authorization": f"Basic {token}"},
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 503)
        self.assertTrue(response.is_json)
        self.assertEqual(response.get_json()["error"]["code"], "indicator_unavailable")

    def test_health_endpoint_does_not_expose_questionnaire_data_or_secret(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=SchemaAwareRepository(
            validate_schema_columns(set(ALL_COLUMNS) - {"q38_dui"})
        )):
            response = self.client.get("/api/fagerh-analytics/v1/health")

        body = response.get_data(as_text=True)
        self.assertNotIn("Bearer", body)
        self.assertNotIn("records", body)


class SchemaRepositoryBehaviorTest(unittest.TestCase):
    def test_schema_validation_does_not_load_dataset(self):
        repository = MetadataRepository()

        repository.validate_schema()

        self.assertEqual(repository.calls, ["columns"])

    def test_schema_metadata_only_uses_get_semantics(self):
        repository = MetadataRepository()

        repository.validate_schema()

        self.assertEqual(repository.methods, ["GET"])

    def test_timeout_during_schema_read_raises_source_error(self):
        repository = TimeoutSchemaRepository()

        with self.assertRaises(RepositoryConnectionError):
            repository.validate_schema()


class SchemaAwareRepository(QuestionnaireRepository):
    def __init__(self, schema_result, rows=None):
        self._schema_result = schema_result
        self._delegate = FakeQuestionnaireRepository(rows=rows or [{
            "campaign_year": 2025,
            "finess_main": "010000001",
            "check_esrp": True,
            "q53_accompagnes__esrp": 4,
        }])

    def list_raw_questionnaires(self):
        return self._delegate.list_raw_questionnaires()

    def validate_schema(self):
        return self._schema_result


class CountingRepository(QuestionnaireRepository):
    def __init__(self):
        self.check_connection_calls = 0
        self.validate_schema_calls = 0

    def list_raw_questionnaires(self):
        return []

    def check_connection(self):
        self.check_connection_calls += 1

    def validate_schema(self):
        self.validate_schema_calls += 1
        return validate_schema_columns(set(ALL_COLUMNS))


class InvalidSchemaRepository(QuestionnaireRepository):
    def list_raw_questionnaires(self):
        return []

    def check_connection(self):
        return None

    def validate_schema(self):
        raise RepositoryResponseError("bad schema")


class MetadataRepository(QuestionnaireRepository):
    def __init__(self):
        self.calls = []
        self.methods = []

    def list_raw_questionnaires(self):
        return []

    def validate_schema(self):
        self.calls.append("columns")
        self.methods.append("GET")
        return validate_schema_columns(set(ALL_COLUMNS))


class TimeoutSchemaRepository(QuestionnaireRepository):
    def list_raw_questionnaires(self):
        return []

    def validate_schema(self):
        raise RepositoryConnectionError("timeout")


def _clock(moment):
    state = {"current": moment}

    def provider():
        return state["current"]

    return provider


if __name__ == "__main__":
    unittest.main()
