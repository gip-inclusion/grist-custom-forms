import base64
import os
import unittest
from unittest.mock import patch

import app
from fagerh_analytics.health import (
    build_fagerh_analytics_health_probe,
    check_fagerh_analytics_configuration,
)
from fagerh_analytics.repositories.base import (
    QuestionnaireRepository,
    RepositoryConnectionError,
    RepositoryResponseError,
)
from fagerh_analytics.repositories.fake import FakeQuestionnaireRepository


class FagerhAnalyticsConfigurationTest(unittest.TestCase):
    def test_complete_configuration_is_valid(self):
        result = check_fagerh_analytics_configuration({
            "GRIST_BASE_URL": "https://grist.example.test",
            "GRIST_DOC_FAGERH": "doc",
            "GRIST_TABLE_FAGERH": "table",
            "GRIST_API_KEY_FAGERH": "token",
        })

        self.assertEqual(result.doc_id, "doc")

    def test_missing_doc_is_invalid(self):
        with self.assertRaises(Exception):
            check_fagerh_analytics_configuration({
                "GRIST_BASE_URL": "https://grist.example.test",
                "GRIST_TABLE_FAGERH": "table",
                "GRIST_API_KEY_FAGERH": "token",
            })

    def test_missing_table_is_invalid(self):
        with self.assertRaises(Exception):
            check_fagerh_analytics_configuration({
                "GRIST_BASE_URL": "https://grist.example.test",
                "GRIST_DOC_FAGERH": "doc",
                "GRIST_API_KEY_FAGERH": "token",
            })

    def test_missing_api_key_is_invalid(self):
        with self.assertRaises(Exception):
            check_fagerh_analytics_configuration({
                "GRIST_BASE_URL": "https://grist.example.test",
                "GRIST_DOC_FAGERH": "doc",
                "GRIST_TABLE_FAGERH": "table",
            })

    def test_missing_base_url_is_invalid(self):
        with self.assertRaises(Exception):
            check_fagerh_analytics_configuration({
                "GRIST_DOC_FAGERH": "doc",
                "GRIST_TABLE_FAGERH": "table",
                "GRIST_API_KEY_FAGERH": "token",
            })

    def test_eures_variables_do_not_compensate_missing_fagerh_ones(self):
        with self.assertRaises(Exception):
            check_fagerh_analytics_configuration({
                "GRIST_BASE_URL": "https://grist.example.test",
                "GRIST_DOC_EURES_BETA": "doc-eures",
                "GRIST_TABLE_EURES_BETA": "table-eures",
                "GRIST_API_KEY_EURES_BETA": "token-eures",
            })

    def test_invalid_timeout_is_detected(self):
        with self.assertRaises(Exception):
            check_fagerh_analytics_configuration({
                "GRIST_BASE_URL": "https://grist.example.test",
                "GRIST_DOC_FAGERH": "doc",
                "GRIST_TABLE_FAGERH": "table",
                "GRIST_API_KEY_FAGERH": "token",
                "FAGERH_ANALYTICS_GRIST_TIMEOUT_SECONDS": "0",
            })

    def test_invalid_page_size_is_detected(self):
        with self.assertRaises(Exception):
            check_fagerh_analytics_configuration({
                "GRIST_BASE_URL": "https://grist.example.test",
                "GRIST_DOC_FAGERH": "doc",
                "GRIST_TABLE_FAGERH": "table",
                "GRIST_API_KEY_FAGERH": "token",
                "FAGERH_ANALYTICS_GRIST_PAGE_SIZE": "-1",
            })

    def test_invalid_max_pages_is_detected(self):
        with self.assertRaises(Exception):
            check_fagerh_analytics_configuration({
                "GRIST_BASE_URL": "https://grist.example.test",
                "GRIST_DOC_FAGERH": "doc",
                "GRIST_TABLE_FAGERH": "table",
                "GRIST_API_KEY_FAGERH": "token",
                "FAGERH_ANALYTICS_GRIST_MAX_PAGES": "0",
            })

    def test_invalid_base_url_is_detected(self):
        with self.assertRaises(Exception):
            check_fagerh_analytics_configuration({
                "GRIST_BASE_URL": "not-a-url",
                "GRIST_DOC_FAGERH": "doc",
                "GRIST_TABLE_FAGERH": "table",
                "GRIST_API_KEY_FAGERH": "token",
            })


class FagerhAnalyticsHealthProbeTest(unittest.TestCase):
    def test_available_probe_returns_success(self):
        probe = build_fagerh_analytics_health_probe(
            repository_factory=lambda: HealthyRepository(),
            cache_ttl_seconds=0,
        )

        result = probe()

        self.assertEqual(result.http_status, 200)
        self.assertEqual(result.analytics_status, "available")

    def test_timeout_returns_unavailable(self):
        probe = build_fagerh_analytics_health_probe(
            repository_factory=lambda: TimeoutRepository(),
            cache_ttl_seconds=0,
        )

        result = probe()

        self.assertEqual(result.http_status, 503)
        self.assertEqual(result.analytics_status, "unavailable")

    def test_invalid_response_returns_unavailable(self):
        probe = build_fagerh_analytics_health_probe(
            repository_factory=lambda: BrokenRepository(),
            cache_ttl_seconds=0,
        )

        result = probe()

        self.assertEqual(result.http_status, 503)
        self.assertEqual(result.error["code"], "repository_unavailable")


class FagerhAnalyticsHealthHttpTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.auth_patch = patch.object(app, "_get_admin_credentials", return_value=("admin", "secret"))
        self.auth_patch.start()
        self.addCleanup(self.auth_patch.stop)
        self.repository_patch = patch.object(app, "get_fagerh_analytics_repository", return_value=FakeQuestionnaireRepository(rows=[]))
        self.repository_patch.start()
        self.addCleanup(self.repository_patch.stop)

    def test_health_endpoint_available_returns_200(self):
        response = self.client.get("/api/fagerh-analytics/v1/health")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertEqual(response.get_json()["analytics_status"], "available")

    def test_health_endpoint_misconfigured_returns_503(self):
        self.repository_patch.stop()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GRIST_DOC_FAGERH", None)
            os.environ.pop("GRIST_TABLE_FAGERH", None)
            os.environ.pop("GRIST_API_KEY_FAGERH", None)
            response = self.client.get("/api/fagerh-analytics/v1/health")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["analytics_status"], "misconfigured")

    def test_health_endpoint_unavailable_returns_503(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=TimeoutRepository()):
            response = self.client.get("/api/fagerh-analytics/v1/health")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["analytics_status"], "unavailable")

    def test_health_endpoint_never_exposes_questionnaire_data(self):
        response = self.client.get("/api/fagerh-analytics/v1/health")

        self.assertNotIn("records", response.get_data(as_text=True))

    def test_health_endpoint_never_exposes_api_key(self):
        response = self.client.get("/api/fagerh-analytics/v1/health")

        self.assertNotIn("Bearer", response.get_data(as_text=True))
        self.assertNotIn("token", response.get_data(as_text=True))

    def test_health_endpoint_never_exposes_traceback(self):
        with patch.object(app, "get_fagerh_analytics_repository", side_effect=RuntimeError("/Users/secret boom")):
            response = self.client.get("/api/fagerh-analytics/v1/health")

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("Traceback", response.get_data(as_text=True))
        self.assertNotIn("/Users/", response.get_data(as_text=True))

    def test_health_global_route_still_works(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_other_routes_keep_working_without_analytics_config(self):
        self.repository_patch.stop()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GRIST_DOC_FAGERH", None)
            os.environ.pop("GRIST_TABLE_FAGERH", None)
            os.environ.pop("GRIST_API_KEY_FAGERH", None)
            response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_indicator_endpoints_still_return_503_when_configuration_is_missing(self):
        self.repository_patch.stop()
        token = base64.b64encode(b"admin:secret").decode("ascii")
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GRIST_DOC_FAGERH", None)
            os.environ.pop("GRIST_TABLE_FAGERH", None)
            os.environ.pop("GRIST_API_KEY_FAGERH", None)
            response = self.client.post(
                "/api/fagerh-analytics/v1/indicators/questionnaires.count",
                headers={"Authorization": f"Basic {token}"},
                json={"filters": {}},
            )

        self.assertEqual(response.status_code, 503)
        self.assertTrue(response.is_json)


class HealthyRepository(QuestionnaireRepository):
    def check_connection(self):
        return None

    def list_raw_questionnaires(self):
        return []


class TimeoutRepository(QuestionnaireRepository):
    def check_connection(self):
        raise RepositoryConnectionError("timeout")

    def list_raw_questionnaires(self):
        return []


class BrokenRepository(QuestionnaireRepository):
    def check_connection(self):
        raise RepositoryResponseError("bad payload")

    def list_raw_questionnaires(self):
        return []


if __name__ == "__main__":
    unittest.main()
