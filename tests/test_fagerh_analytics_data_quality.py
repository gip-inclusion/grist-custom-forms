import base64
import unittest
from unittest.mock import patch

import app
from fagerh_analytics.api import IndicatorQuery, execute_indicator_query, get_data_quality_summary
from fagerh_analytics.domain import UserContext
from fagerh_analytics.repositories.fake import FakeQuestionnaireRepository


class FagerhAnalyticsDataQualityTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.previous_secret_key = app.app.config.get("SECRET_KEY")
        app.app.config["SECRET_KEY"] = "test-secret-key"
        self.auth_patch = patch.object(app, "_get_admin_credentials", return_value=("admin", "secret"))
        self.auth_patch.start()
        self.addCleanup(self.auth_patch.stop)
        self.repository_patch = patch.object(app, "get_fagerh_analytics_repository", return_value=_quality_repository())
        self.repository_patch.start()
        self.addCleanup(self.repository_patch.stop)
        self.addCleanup(self._restore_secret_key)

    def _restore_secret_key(self):
        app.app.config["SECRET_KEY"] = self.previous_secret_key

    def test_valid_finess_produces_no_issue(self):
        summary = get_data_quality_summary(FakeQuestionnaireRepository(rows=[{"uuid": "u1", "finess_main": "001234567", "department_code": "75"}]), _admin())
        self.assertEqual(summary.invalid_finess_count, 0)
        self.assertFalse(any(issue.code == "invalid_finess" for issue in summary.issues))

    def test_eight_digit_finess_produces_normalized_finess_warning(self):
        summary = get_data_quality_summary(FakeQuestionnaireRepository(rows=[{"uuid": "u1", "finess_main": "12345678", "department_code": "75"}]), _admin())
        issue = next(issue for issue in summary.issues if issue.code == "normalized_finess")
        self.assertEqual(issue.record_count, 1)
        self.assertEqual(issue.distinct_value_count, 1)
        self.assertEqual(summary.invalid_finess_count, 0)

    def test_non_digit_finess_produces_invalid_finess_issue(self):
        summary = get_data_quality_summary(FakeQuestionnaireRepository(rows=[{"uuid": "u1", "finess_main": "1234A6789", "department_code": "75"}]), _admin())
        self.assertTrue(any(issue.code == "invalid_finess" for issue in summary.issues))

    def test_finess_with_leading_zero_valid_is_preserved(self):
        summary = get_data_quality_summary(FakeQuestionnaireRepository(rows=[{"uuid": "u1", "finess_main": "012345678", "department_code": "75"}]), _admin())
        self.assertEqual(summary.invalid_finess_count, 0)

    def test_valid_department_produces_no_geography_issue(self):
        summary = get_data_quality_summary(FakeQuestionnaireRepository(rows=[{"uuid": "u1", "finess_main": "001234567", "department_code": "75"}]), _admin())
        self.assertEqual(summary.unknown_department_count, 0)
        self.assertEqual(summary.unresolved_region_count, 0)

    def test_hash_value_department_produces_unknown_department_issue(self):
        summary = get_data_quality_summary(FakeQuestionnaireRepository(rows=[{"uuid": "u1", "finess_main": "001234567", "department_code": "#VALUE!"}]), _admin())
        self.assertTrue(any(issue.code == "unknown_department" for issue in summary.issues))

    def test_unknown_department_produces_unresolved_region_issue(self):
        summary = get_data_quality_summary(FakeQuestionnaireRepository(rows=[{"uuid": "u1", "finess_main": "001234567", "department_code": "999"}]), _admin())
        self.assertTrue(any(issue.code == "unresolved_region" for issue in summary.issues))

    def test_anomalies_are_aggregated_without_exposing_full_finess_values(self):
        summary = get_data_quality_summary(FakeQuestionnaireRepository(rows=[{"uuid": "u1", "finess_main": "12345678", "department_code": "75"}]), _admin())
        issue = next(issue for issue in summary.issues if issue.code == "normalized_finess")
        self.assertIn("12****78", issue.masked_examples)
        self.assertNotIn("12345678", "".join(issue.masked_examples))

    def test_national_results_remain_calculable_with_geography_anomaly(self):
        repository = FakeQuestionnaireRepository(rows=[{
            "uuid": "u1",
            "finess_main": "001234567",
            "department_code": "#VALUE!",
            "prestations_json": {"cond-pec": {"fileActive": 24}},
            "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [{"id": "cond-pec", "name": "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"}]}}},
        }])
        response = execute_indicator_query(IndicatorQuery("people.received.pec", {}, _admin()), repository)
        self.assertEqual(response.status, "success")
        self.assertEqual(response.result["value"], 24)

    def test_eight_digit_finess_filter_is_normalized(self):
        repository = FakeQuestionnaireRepository(rows=[{"uuid": "u1", "finess_main": "001234567", "department_code": "75"}])
        response = execute_indicator_query(IndicatorQuery("questionnaires.count", {"finess_main": "12345678"}, _admin()), repository)
        self.assertEqual(response.status, "success")
        self.assertEqual(response.result["value"], 0)

    def test_regional_user_only_sees_scope_anomalies(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "u1", "finess_main": "12345678", "region_code": "11", "department_code": "75"},
            {"uuid": "u2", "finess_main": "87654321", "region_code": "84", "department_code": "69"},
        ])
        summary = get_data_quality_summary(repository, UserContext("u", "regional_user", region_codes=("11",)))
        issue = next(issue for issue in summary.issues if issue.code == "normalized_finess")
        self.assertEqual(issue.record_count, 1)

    def test_establishment_user_only_sees_scope_anomalies(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "u1", "finess_main": "001234567", "department_code": "#VALUE!"},
            {"uuid": "u2", "finess_main": "009999999", "department_code": "#VALUE!"},
        ])
        summary = get_data_quality_summary(repository, UserContext("u", "establishment_user", finess_values=("001234567",)))
        issue = next(issue for issue in summary.issues if issue.code == "unknown_department")
        self.assertEqual(issue.record_count, 1)

    def test_admin_sees_complete_summary(self):
        summary = get_data_quality_summary(_quality_repository(), _admin())
        self.assertEqual(summary.invalid_finess_count, 0)
        self.assertGreaterEqual(summary.unknown_department_count, 1)
        self.assertTrue(any(issue.code == "normalized_finess" for issue in summary.issues))

    def test_endpoint_without_auth_returns_401(self):
        response = self.client.get("/api/fagerh-analytics/v1/data-quality")
        self.assertEqual(response.status_code, 401)

    def test_endpoint_with_session_admin_returns_200(self):
        with self.client.session_transaction() as session_data:
            session_data["fagerh_analytics_authenticated"] = True
            session_data["fagerh_analytics_role"] = "admin_global"
        response = self.client.get("/api/fagerh-analytics/v1/data-quality")
        self.assertEqual(response.status_code, 200)

    def test_endpoint_response_is_json_compatible(self):
        response = self.client.get("/api/fagerh-analytics/v1/data-quality", headers=self._auth_headers())
        self.assertTrue(response.is_json)

    def test_endpoint_does_not_expose_full_finess_or_secrets(self):
        response = self.client.get("/api/fagerh-analytics/v1/data-quality", headers=self._auth_headers())
        body = response.get_data(as_text=True)
        self.assertNotIn("12345678", body)
        self.assertNotIn("secret", body)
        self.assertNotIn("GRIST_", body)

    def test_endpoint_for_non_admin_role_returns_403(self):
        with patch.object(app, "build_analytics_user_context", return_value=UserContext("u", "regional_user", region_codes=("11",))):
            response = self.client.get("/api/fagerh-analytics/v1/data-quality", headers=self._auth_headers())
        self.assertEqual(response.status_code, 403)

    def _auth_headers(self):
        token = base64.b64encode(b"admin:secret").decode("ascii")
        return {"Authorization": f"Basic {token}"}


def _admin():
    return UserContext("admin", "admin_global", can_export=True)


def _quality_repository():
    return FakeQuestionnaireRepository(rows=[
        {"uuid": "u1", "finess_main": "12345678", "department_code": "75"},
        {"uuid": "u2", "finess_main": "", "department_code": "75"},
        {"uuid": "u3", "finess_main": "001234567", "department_code": "#VALUE!"},
        {"uuid": "u4", "finess_main": "009999999", "department_code": "69"},
    ])


if __name__ == "__main__":
    unittest.main()
