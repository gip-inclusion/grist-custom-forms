import base64
import json
import os
import unittest
from unittest.mock import patch

import app
from fagerh_analytics.auth import FAGERH_ANALYTICS_ROLE_KEY, FAGERH_ANALYTICS_SESSION_KEY
from fagerh_analytics.domain import UserContext
from fagerh_analytics.repositories.base import QuestionnaireRepository
from fagerh_analytics.repositories.fake import FakeQuestionnaireRepository


class FagerhAnalyticsHttpTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.previous_secret_key = app.app.config.get("SECRET_KEY")
        app.app.config["SECRET_KEY"] = "test-secret-key"
        self.auth_patch = patch.object(app, "_get_admin_credentials", return_value=("admin", "secret"))
        self.auth_patch.start()
        self.addCleanup(self.auth_patch.stop)
        self.repository_patch = patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[]))
        self.repository_patch.start()
        self.addCleanup(self.repository_patch.stop)
        self.addCleanup(self._restore_secret_key)

    def _restore_secret_key(self):
        app.app.config["SECRET_KEY"] = self.previous_secret_key

    def test_list_indicators_authenticated_returns_200(self):
        response = self.client.get("/api/fagerh-analytics/v1/indicators", headers=self._auth_headers())

        self.assertEqual(response.status_code, 200)

    def test_list_without_authentication_returns_401(self):
        response = self.client.get("/api/fagerh-analytics/v1/indicators")

        self.assertEqual(response.status_code, 401)
        self.assertTrue(response.is_json)

    def test_page_authentication_initializes_session_for_following_api_calls(self):
        page_response = self.client.get("/admin/fagerh/analytics/", headers=self._auth_headers())
        self.addCleanup(page_response.close)
        self.assertEqual(page_response.status_code, 200)
        response = self.client.get("/api/fagerh-analytics/v1/catalog")
        self.assertEqual(response.status_code, 200)

    def test_post_indicator_with_signed_session_returns_200(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ])):
            self._set_fagerh_session()
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/people.received.esrp",
                headers={"Origin": "http://localhost"},
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 200)

    def test_post_indicator_with_signed_session_and_invalid_origin_is_refused(self):
        self._set_fagerh_session()
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers={"Origin": "https://evil.example"},
            json={"filters": {}},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"]["code"], "permission_denied")

    def test_post_indicator_with_signed_session_and_no_origin_is_refused(self):
        self._set_fagerh_session()
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            json={"filters": {}},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"]["code"], "permission_denied")

    def test_post_valid_indicator_returns_200(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ])):
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/people.received.esrp",
                headers=self._auth_headers(),
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 200)

    def test_valid_response_respects_json_contract(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json={"filters": {}, "request_id": "req-1"},
        )

        payload = response.get_json()
        self.assertEqual(set(payload.keys()), {
            "api_version", "request_id", "status", "result", "error", "warnings", "generated_at", "freshness_at",
        })

    def test_unknown_indicator_returns_404(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/unknown.indicator",
            headers=self._auth_headers(),
            json={"filters": {}},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["error"]["code"], "indicator_not_found")

    def test_missing_json_returns_400(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers={**self._auth_headers(), "Content-Type": "application/json"},
            data="{invalid",
        )

        self.assertEqual(response.status_code, 400)

    def test_json_root_non_object_returns_400(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json=[],
        )

        self.assertEqual(response.status_code, 400)

    def test_filters_non_object_returns_400(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json={"filters": []},
        )

        self.assertEqual(response.status_code, 400)

    def test_empty_request_id_returns_400(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json={"filters": {}, "request_id": ""},
        )

        self.assertEqual(response.status_code, 400)

    def test_unknown_root_property_returns_400(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json={"filters": {}, "role": "admin_global"},
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_business_filter_returns_400(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/people.received.esrp",
            headers=self._auth_headers(),
            json={"filters": {"campaign_year": "2025"}},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "invalid_filter")

    def test_incompatible_filter_returns_400(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/people.received.pec",
            headers=self._auth_headers(),
            json={"filters": {"dispositifs": "esrp"}},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "incompatible_filter")

    def test_campaign_filter_unavailable_returns_400(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"campaign_year": None, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ])):
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/people.received.esrp",
                headers=self._auth_headers(),
                json={"filters": {"campaign_year": 2025}},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "incompatible_filter")

    def test_campaign_filter_unavailable_returns_400_with_signed_session(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"campaign_year": None, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ])):
            self._set_fagerh_session()
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/people.received.esrp",
                headers={"Origin": "http://localhost"},
                json={"filters": {"campaign_year": 2025}},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "incompatible_filter")

    def test_permission_denied_returns_403(self):
        with patch.object(app, "build_analytics_user_context", return_value=UserContext("u1", "regional_user", region_codes=("44",))):
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/people.received.esrp",
                headers=self._auth_headers(),
                json={"filters": {"region_code": "84"}},
            )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json()["error"]["code"], "permission_denied")

    def test_data_quality_error_returns_422(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": -1},
        ])):
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/people.received.esrp",
                headers=self._auth_headers(),
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json()["error"]["code"], "data_quality_error")

    def test_data_consistency_error_returns_422(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 5},
        ])):
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/people.received.esrp",
                headers=self._auth_headers(),
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.get_json()["error"]["code"], "data_consistency_error")

    def test_unexpected_error_returns_500_without_trace(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=ExplodingRepository()):
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/questionnaires.count",
                headers=self._auth_headers(),
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 500)
        self.assertNotIn("Traceback", response.get_data(as_text=True))

    def test_missing_real_fagerh_configuration_returns_503(self):
        self.repository_patch.stop()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GRIST_DOC_FAGERH", None)
            os.environ.pop("GRIST_TABLE_FAGERH", None)
            os.environ.pop("GRIST_API_KEY_FAGERH", None)
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/questionnaires.count",
                headers=self._auth_headers(),
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"]["code"], "data_source_error")

    def test_list_indicators_with_missing_real_configuration_returns_503(self):
        self.repository_patch.stop()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GRIST_DOC_FAGERH", None)
            os.environ.pop("GRIST_TABLE_FAGERH", None)
            os.environ.pop("GRIST_API_KEY_FAGERH", None)
            response = self.client.get(
                "/api/fagerh-analytics/v1/indicators",
                headers=self._auth_headers(),
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"]["code"], "data_source_error")

    def test_error_responses_remain_json(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
        )

        self.assertTrue(response.is_json)

    def test_endpoint_refuses_client_role(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json={"filters": {}, "role": "regional_user"},
        )

        self.assertEqual(response.status_code, 400)

    def test_endpoint_refuses_client_scope(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json={"filters": {}, "scope": {"region_codes": ["44"]}},
        )

        self.assertEqual(response.status_code, 400)

    def test_existing_admin_user_is_mapped_to_admin_global(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json={"filters": {}},
        )

        self.assertEqual(response.get_json()["result"]["user_role"], "admin_global")

    def test_export_permission_admin_returns_allowed(self):
        response = self.client.get("/api/fagerh-analytics/v1/export-permission", headers=self._auth_headers())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["result"], {"allowed": True, "role": "admin_global"})

    def test_export_permission_with_signed_session_returns_allowed(self):
        self._set_fagerh_session()
        response = self.client.get("/api/fagerh-analytics/v1/export-permission")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["result"], {"allowed": True, "role": "admin_global"})

    def test_dashboard_authenticated_returns_200(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"uuid": "uuid-2", "campaign_year": 2025, "saisie_terminee": False, "finess_main": "010000002", "check_espo": True, "q53_accompagnes__espo": 5},
        ])):
            response = self.client.post(
                "/api/fagerh-analytics/v1/dashboard",
                headers=self._auth_headers(),
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["result"]["overview"]["indicators"]["total"]["value"], 9)
        self.assertNotIn("completion_scope", payload["result"]["filters"]["applied"])

    def test_dashboard_completion_scope_filters_results(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"uuid": "uuid-2", "campaign_year": 2025, "saisie_terminee": False, "finess_main": "010000002", "check_espo": True, "q53_accompagnes__espo": 5},
        ])):
            response = self.client.post(
                "/api/fagerh-analytics/v1/dashboard",
                headers=self._auth_headers(),
                json={"filters": {"completion_scope": "completed"}},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result"]["overview"]["questionnaire_count"], 1)
        self.assertEqual(payload["result"]["overview"]["indicators"]["total"]["value"], 4)
        self.assertEqual(payload["result"]["activity"]["status_comparison"]["questionnaires"], {
            "all": 2,
            "completed": 1,
            "in_progress": 1,
        })

    def test_dashboard_campaign_filter_unavailable_returns_400(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": None, "saisie_terminee": True, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ])):
            response = self.client.post(
                "/api/fagerh-analytics/v1/dashboard",
                headers=self._auth_headers(),
                json={"filters": {"campaign_year": 2025}},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"]["code"], "incompatible_filter")

    def test_analytics_auth_accepts_fagerh_specific_admin_credentials(self):
        self.auth_patch.stop()
        with patch.dict(
            os.environ,
            {
                "ADMIN_USERNAME_FAGERH": "fagerh-admin",
                "ADMIN_PASSWORD_FAGERH": "fagerh-secret",
            },
            clear=False,
        ):
            os.environ.pop("ADMIN_USERNAME", None)
            os.environ.pop("ADMIN_PASSWORD", None)
            token = base64.b64encode(b"fagerh-admin:fagerh-secret").decode("ascii")
            response = self.client.get(
                "/api/fagerh-analytics/v1/catalog",
                headers={"Authorization": f"Basic {token}"},
            )

        self.assertEqual(response.status_code, 200)

    def test_payload_too_large_is_refused(self):
        huge_payload = json.dumps({"filters": {"campaign_year": 2025}, "request_id": "x" * 20000})
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers={**self._auth_headers(), "Content-Type": "application/json"},
            data=huge_payload,
        )

        self.assertEqual(response.status_code, 400)

    def test_too_many_finess_are_refused(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json={"filters": {"finess_main": [f"{i:09d}" for i in range(101)]}},
        )

        self.assertEqual(response.status_code, 400)

    def test_existing_routes_continue_to_work(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_session_contains_no_password_or_grist_key(self):
        response = self.client.get("/admin/fagerh/analytics/", headers=self._auth_headers())
        self.addCleanup(response.close)
        with self.client.session_transaction() as session_data:
            serialized = json.dumps(dict(session_data))
        self.assertNotIn("secret", serialized)
        self.assertNotIn("GRIST", serialized)

    def test_total_national_with_signed_session_returns_expected_value(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 0},
            {"campaign_year": 2025, "finess_main": "010000002", "check_espo": True, "q53_accompagnes__espo": 0},
            {"campaign_year": 2025, "finess_main": "010000003", "check_ueros": True, "q53_accompagnes__ueros": 0},
            {
                "campaign_year": 2025,
                "finess_main": "010000004",
                "prestations_json": {"cond-pec": {"fileActive": 2439}},
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [{"id": "cond-pec", "name": "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"}]}}},
            },
            {
                "campaign_year": 2025,
                "finess_main": "010000005",
                "prestations_json": {"cond-other": {"fileActive": 1499}},
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [{"id": "cond-other", "name": "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH"}]}}},
            },
        ])):
            self._set_fagerh_session()
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/people.received.all",
                headers={"Origin": "http://localhost"},
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result"]["value"], 3938)
        self.assertEqual(payload["result"]["breakdown"], {
            "esrp": 0,
            "espo": 0,
            "ueros": 0,
            "pec": 2439,
            "other_eval": 1499,
        })

    def _auth_headers(self):
        token = base64.b64encode(b"admin:secret").decode("ascii")
        return {"Authorization": f"Basic {token}"}

    def _set_fagerh_session(self, *, role="admin_global"):
        with self.client.session_transaction() as session_data:
            session_data[FAGERH_ANALYTICS_SESSION_KEY] = True
            session_data[FAGERH_ANALYTICS_ROLE_KEY] = role


class ExplodingRepository(QuestionnaireRepository):
    repository_name = "exploding"

    def list_raw_questionnaires(self):
        raise RuntimeError("/Users/private/path should not leak")
