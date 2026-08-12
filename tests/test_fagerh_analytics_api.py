import unittest
from datetime import datetime, timezone

from fagerh_analytics.api import (
    API_VERSION,
    IndicatorQuery,
    check_export_permission,
    execute_indicator_query,
    list_available_indicators,
    serialize_indicator_result,
)
from fagerh_analytics.domain import IndicatorResult, PermissionScope, ResolvedFilters, UserContext
from fagerh_analytics.repositories.base import QuestionnaireRepository, RepositoryConfigurationError
from fagerh_analytics.repositories.fake import FakeQuestionnaireRepository


class FagerhAnalyticsApiTest(unittest.TestCase):
    def test_valid_query_returns_success(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ])

        response = execute_indicator_query(
            IndicatorQuery(
                indicator_id="people.received.esrp",
                filters={},
                user_context=UserContext("u1", "admin_global"),
            ),
            repository,
            generated_at="2026-07-24T12:00:00Z",
        )

        self.assertEqual(response.status, "success")
        self.assertEqual(response.result["value"], 4)

    def test_response_contains_api_version(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.api_version, API_VERSION)

    def test_response_contains_generated_at_utc(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[]),
            now_provider=lambda: datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(response.generated_at, "2026-07-24T12:00:00Z")

    def test_request_id_is_echoed(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("u1", "admin_global"), request_id="req-1"),
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.request_id, "req-1")

    def test_missing_request_id_stays_null(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertIsNone(response.request_id)

    def test_unknown_indicator_returns_indicator_not_found(self):
        response = execute_indicator_query(
            IndicatorQuery("unknown.indicator", {}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "indicator_not_found")

    def test_missing_user_context_returns_invalid_request(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, None),  # type: ignore[arg-type]
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "invalid_request")

    def test_unknown_role_returns_invalid_user_context(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("u1", "unknown_role")),
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "invalid_user_context")

    def test_invalid_filter_returns_invalid_filter(self):
        response = execute_indicator_query(
            IndicatorQuery("people.received.esrp", {"campaign_year": "2025"}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "invalid_filter")

    def test_incompatible_filter_returns_incompatible_filter(self):
        response = execute_indicator_query(
            IndicatorQuery("people.received.pec", {"dispositifs": "esrp"}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "incompatible_filter")

    def test_out_of_scope_returns_permission_denied(self):
        response = execute_indicator_query(
            IndicatorQuery(
                "people.received.esrp",
                {"region_code": "84"},
                UserContext("u1", "regional_user", region_codes=("44",)),
            ),
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "permission_denied")

    def test_data_quality_error_returns_data_quality_error(self):
        response = execute_indicator_query(
            IndicatorQuery("people.received.esrp", {}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[
                {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": -1},
            ]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "data_quality_error")

    def test_data_consistency_error_returns_data_consistency_error(self):
        response = execute_indicator_query(
            IndicatorQuery("people.received.esrp", {}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[
                {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
                {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 5},
            ]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "data_consistency_error")

    def test_unexpected_error_returns_internal_error_without_trace(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("u1", "admin_global")),
            ExplodingRepository(),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "internal_error")
        self.assertNotIn("Traceback", response.error["message"])

    def test_repository_configuration_error_returns_data_source_error(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("u1", "admin_global")),
            MisconfiguredRepository(),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "data_source_error")

    def test_error_response_does_not_contain_local_path(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("u1", "admin_global")),
            ExplodingRepository(),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertNotIn("/Users/", str(response.error))

    def test_error_response_does_not_contain_python_exception_object(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("u1", "admin_global")),
            ExplodingRepository(),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertNotIn("RuntimeError", str(response.error))

    def test_indicator_result_serializes_to_json_simple_types(self):
        result = IndicatorResult(
            indicator_id="x",
            label="X",
            value=1,
            unit="count",
            privacy_status="visible",
            confidence_level="high",
            source={"b": 2, "a": 1},
            breakdown={"z": 3},
            resolved_filters=ResolvedFilters(applied={"k": ("b", "a")}, warnings=("w",)),
            user_role="admin_global",
            permission_scope=PermissionScope(True, (), (), (), (), True, "admin_global"),
        )

        serialized = serialize_indicator_result(result)

        self.assertEqual(serialized["source"], {"a": 1, "b": 2})
        self.assertEqual(serialized["resolved_filters"]["applied"]["k"], ["b", "a"])

    def test_sets_are_serialized_with_deterministic_order(self):
        result = IndicatorResult(
            indicator_id="x",
            label="X",
            value=1,
            unit="count",
            privacy_status="visible",
            confidence_level="high",
            source={"s": {"b", "a"}},
        )

        serialized = serialize_indicator_result(result)

        self.assertEqual(serialized["source"]["s"], ["a", "b"])

    def test_breakdown_of_people_received_all_is_preserved(self):
        response = execute_indicator_query(
            IndicatorQuery("people.received.all", {}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[
                {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 2},
            ]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertIn("breakdown", response.result)

    def test_resolved_filters_are_preserved(self):
        response = execute_indicator_query(
            IndicatorQuery("people.received.esrp", {"campaign_year": 2025}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[
                {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 2},
            ]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertIn("resolved_filters", response.result)

    def test_permission_scope_is_preserved_without_personal_data(self):
        response = execute_indicator_query(
            IndicatorQuery("questionnaires.count", {}, UserContext("user-secret", "admin_global")),
            FakeQuestionnaireRepository(rows=[]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.result["permission_scope"]["role"], "admin_global")
        self.assertNotIn("user_id", str(response.result["permission_scope"]))

    def test_warnings_are_preserved(self):
        response = execute_indicator_query(
            IndicatorQuery("people.received.esrp", {"campaign_year": 2030}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[
                {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 2},
            ]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.warnings, ["campaign_year 2030 absent from dataset; result will be empty"])

    def test_campaign_filter_unavailable_returns_incompatible_filter(self):
        response = execute_indicator_query(
            IndicatorQuery("people.received.esrp", {"campaign_year": 2025}, UserContext("u1", "admin_global")),
            FakeQuestionnaireRepository(rows=[
                {"campaign_year": None, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 2},
            ]),
            generated_at="2026-07-24T12:00:00Z",
        )
        self.assertEqual(response.error["code"], "incompatible_filter")
        self.assertEqual(response.error["message"], "Le filtre de campagne n’est pas disponible pour cette source de données.")

    def test_list_available_indicators_triggers_no_calculation(self):
        indicators = list_available_indicators(UserContext("u1", "admin_global"), NoReadRepository())
        self.assertGreater(len(indicators), 0)

    def test_list_available_indicators_contains_compatible_filters(self):
        indicators = list_available_indicators(UserContext("u1", "admin_global"), NoReadRepository())
        item = next(item for item in indicators if item["indicator_id"] == "people.received.pec")
        self.assertEqual(item["compatible_filters"], ["campaign_year", "region_code", "department_code", "finess_main", "completion_scope"])

    def test_people_received_all_unavailable_with_incomplete_scope(self):
        indicators = list_available_indicators(
            UserContext("u1", "regional_user", region_codes=("44",), allowed_dispositifs=("esrp",)),
            NoReadRepository(),
        )
        item = next(item for item in indicators if item["indicator_id"] == "people.received.all")
        self.assertFalse(item["available"])

    def test_transverse_indicators_remain_available_for_dispositif_limited_scope(self):
        indicators = list_available_indicators(
            UserContext("u1", "regional_user", region_codes=("44",), allowed_dispositifs=("esrp",)),
            NoReadRepository(),
        )
        item = next(item for item in indicators if item["indicator_id"] == "institution.mdph.epe.count")
        self.assertTrue(item["available"])

    def test_check_export_permission_allows_admin_global(self):
        check_export_permission(UserContext("u1", "admin_global"))

    def test_check_export_permission_refuses_others(self):
        with self.assertRaises(Exception):
            check_export_permission(UserContext("u1", "national_readonly"))


class ExplodingRepository(QuestionnaireRepository):
    repository_name = "exploding"

    def list_raw_questionnaires(self):
        raise RuntimeError("/Users/secret/path boom")


class NoReadRepository(QuestionnaireRepository):
    repository_name = "no-read"

    def list_raw_questionnaires(self):
        raise AssertionError("should not calculate")


class MisconfiguredRepository(QuestionnaireRepository):
    repository_name = "misconfigured"

    def list_raw_questionnaires(self):
        raise RepositoryConfigurationError("Missing required FAGERH analytics configuration: GRIST_DOC_FAGERH.")
