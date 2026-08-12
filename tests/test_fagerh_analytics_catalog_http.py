import base64
import unittest
from unittest.mock import patch

import app
from fagerh_analytics.auth import FAGERH_ANALYTICS_ROLE_KEY, FAGERH_ANALYTICS_SESSION_KEY
from fagerh_analytics.repositories.base import QuestionnaireRepository, RepositoryResponseError
from fagerh_analytics.schema import validate_schema_columns


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


class FagerhAnalyticsCatalogHttpTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.previous_secret_key = app.app.config.get("SECRET_KEY")
        app.app.config["SECRET_KEY"] = "test-secret-key"
        self.auth_patch = patch.object(app, "_get_admin_credentials", return_value=("admin", "secret"))
        self.auth_patch.start()
        self.addCleanup(self.auth_patch.stop)
        self.repository_patch = patch.object(app, "get_fagerh_analytics_repository", return_value=CatalogRepository())
        self.repository_patch.start()
        self.addCleanup(self.repository_patch.stop)
        self.addCleanup(self._restore_secret_key)

    def _restore_secret_key(self):
        app.app.config["SECRET_KEY"] = self.previous_secret_key

    def test_catalog_authenticated_returns_200(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog", headers=self._auth_headers())
        self.assertEqual(response.status_code, 200)

    def test_catalog_without_authentication_returns_401(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog")
        self.assertEqual(response.status_code, 401)

    def test_catalog_with_signed_session_returns_200_without_basic_auth(self):
        with self.client.session_transaction() as session_data:
            session_data[FAGERH_ANALYTICS_SESSION_KEY] = True
            session_data[FAGERH_ANALYTICS_ROLE_KEY] = "admin_global"
        response = self.client.get("/api/fagerh-analytics/v1/catalog")
        self.assertEqual(response.status_code, 200)

    def test_catalog_with_non_fagerh_session_returns_401(self):
        with self.client.session_transaction() as session_data:
            session_data[FAGERH_ANALYTICS_SESSION_KEY] = True
            session_data[FAGERH_ANALYTICS_ROLE_KEY] = "regional_user"
        response = self.client.get("/api/fagerh-analytics/v1/catalog")
        self.assertEqual(response.status_code, 401)

    def test_catalog_contains_api_and_catalog_versions(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog", headers=self._auth_headers())
        payload = response.get_json()
        self.assertEqual(payload["api_version"], "v1")
        self.assertEqual(payload["catalog_version"], "1")

    def test_catalog_contains_expected_indicators_for_admin_global(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog", headers=self._auth_headers())
        ids = [item["indicator_id"] for item in response.get_json()["indicators"]]
        self.assertIn("profile.dui.yes.count", ids)
        self.assertIn("people.received.pec", ids)

    def test_visibility_observatory_filter_excludes_internal(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog?visibility=observatory", headers=self._auth_headers())
        ids = [item["indicator_id"] for item in response.get_json()["indicators"]]
        self.assertNotIn("profile.dui.yes.count", ids)
        self.assertIn("people.received.pec", ids)

    def test_visibility_internal_filter_excludes_observatory(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog?visibility=internal", headers=self._auth_headers())
        ids = [item["indicator_id"] for item in response.get_json()["indicators"]]
        self.assertIn("profile.dui.yes.count", ids)
        self.assertNotIn("people.received.pec", ids)

    def test_grain_filter_works(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog?grain=composite", headers=self._auth_headers())
        ids = [item["indicator_id"] for item in response.get_json()["indicators"]]
        self.assertEqual(ids, ["people.received.other_eval", "people.received.all"])

    def test_available_true_filter_works(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog?available=true", headers=self._auth_headers())
        self.assertTrue(all(item["available"] for item in response.get_json()["indicators"]))

    def test_available_false_filter_works(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=CatalogRepository(columns=ALL_COLUMNS - {"prestations_json"})):
            response = self.client.get("/api/fagerh-analytics/v1/catalog?available=false", headers=self._auth_headers())
        ids = [item["indicator_id"] for item in response.get_json()["indicators"]]
        self.assertIn("people.received.pec", ids)
        self.assertIn("people.received.all", ids)

    def test_invalid_visibility_returns_400(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog?visibility=bad", headers=self._auth_headers())
        self.assertEqual(response.status_code, 400)

    def test_invalid_grain_returns_400(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog?grain=bad", headers=self._auth_headers())
        self.assertEqual(response.status_code, 400)

    def test_invalid_available_returns_400(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog?available=maybe", headers=self._auth_headers())
        self.assertEqual(response.status_code, 400)

    def test_unknown_query_parameter_returns_400(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog?search=x", headers=self._auth_headers())
        self.assertEqual(response.status_code, 400)

    def test_detail_of_known_indicator_returns_200(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog/people.received.pec", headers=self._auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["indicator"]["indicator_id"], "people.received.pec")

    def test_detail_with_signed_session_returns_200_without_basic_auth(self):
        with self.client.session_transaction() as session_data:
            session_data[FAGERH_ANALYTICS_SESSION_KEY] = True
            session_data[FAGERH_ANALYTICS_ROLE_KEY] = "admin_global"
        response = self.client.get("/api/fagerh-analytics/v1/catalog/people.received.pec")
        self.assertEqual(response.status_code, 200)

    def test_detail_of_unknown_indicator_returns_404(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog/unknown.indicator", headers=self._auth_headers())
        self.assertEqual(response.status_code, 404)

    def test_detail_exposes_source_fields_and_paths(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog/people.received.pec", headers=self._auth_headers())
        indicator = response.get_json()["indicator"]
        self.assertIn("prestations_json", indicator["source_fields"])
        self.assertTrue(indicator["source_paths"])

    def test_no_local_paths_or_secrets_exposed(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog/people.received.pec", headers=self._auth_headers())
        body = response.get_data(as_text=True)
        self.assertNotIn("/Users/", body)
        self.assertNotIn("Bearer", body)
        self.assertNotIn("GRIST_", body)

    def test_people_received_all_exposes_exact_components_without_deac(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog/people.received.all", headers=self._auth_headers())
        components = response.get_json()["indicator"]["component_indicators"]
        self.assertEqual(components, [
            "people.received.esrp",
            "people.received.espo",
            "people.received.ueros",
            "people.received.pec",
            "people.received.other_eval",
        ])

    def test_unavailable_indicator_exposes_reason(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=CatalogRepository(columns=ALL_COLUMNS - {"prestations_json"})):
            response = self.client.get("/api/fagerh-analytics/v1/catalog/people.received.pec", headers=self._auth_headers())
        indicator = response.get_json()["indicator"]
        self.assertFalse(indicator["available"])
        self.assertTrue(indicator["unavailable_reason"])

    def test_schema_unavailable_returns_503(self):
        with patch.object(app, "get_fagerh_analytics_repository", return_value=BrokenCatalogRepository()):
            response = self.client.get("/api/fagerh-analytics/v1/catalog", headers=self._auth_headers())
        self.assertEqual(response.status_code, 503)

    def test_catalog_order_is_deterministic(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog", headers=self._auth_headers())
        ids = [item["indicator_id"] for item in response.get_json()["indicators"]]
        self.assertEqual(ids, sorted(ids, key=_expected_sort_key))

    def test_catalog_response_is_json_compatible(self):
        response = self.client.get("/api/fagerh-analytics/v1/catalog", headers=self._auth_headers())
        self.assertTrue(response.is_json)

    def test_catalog_does_not_trigger_indicator_calculation_or_full_questionnaire_read(self):
        repository = CountingCatalogRepository()
        with patch.object(app, "get_fagerh_analytics_repository", return_value=repository):
            response = self.client.get("/api/fagerh-analytics/v1/catalog", headers=self._auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(repository.validate_schema_calls, 1)
        self.assertEqual(repository.list_raw_questionnaires_calls, 0)

    def test_existing_indicator_endpoint_continues_to_work(self):
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/questionnaires.count",
            headers=self._auth_headers(),
            json={"filters": {}},
        )
        self.assertEqual(response.status_code, 200)

    def _auth_headers(self):
        token = base64.b64encode(b"admin:secret").decode("ascii")
        return {"Authorization": f"Basic {token}"}


class CatalogRepository(QuestionnaireRepository):
    def __init__(self, columns=None):
        self._schema = validate_schema_columns(set(columns or ALL_COLUMNS))

    def list_raw_questionnaires(self):
        return []

    def validate_schema(self):
        return self._schema


class BrokenCatalogRepository(QuestionnaireRepository):
    def list_raw_questionnaires(self):
        return []

    def validate_schema(self):
        raise RepositoryResponseError("schema unavailable")


class CountingCatalogRepository(CatalogRepository):
    def __init__(self):
        super().__init__()
        self.validate_schema_calls = 0
        self.list_raw_questionnaires_calls = 0

    def list_raw_questionnaires(self):
        self.list_raw_questionnaires_calls += 1
        raise AssertionError("catalog must not calculate indicators")

    def validate_schema(self):
        self.validate_schema_calls += 1
        return super().validate_schema()


def _expected_sort_key(indicator_id):
    visibility_order = {"internal": 0, "both": 1, "observatory": 2}
    grain_order = {
        "questionnaire": 0,
        "establishment_service_device": 1,
        "evaluation_activity": 2,
        "composite": 3,
    }
    catalog = {
        "questionnaires.count": ("Questionnaires", "internal", "questionnaire"),
        "profile.dui.yes.count": ("Établissements et services utilisant un DUI", "internal", "establishment_service_device"),
        "profile.dui.no.count": ("Établissements et services n'utilisant pas de DUI", "internal", "establishment_service_device"),
        "profile.remuneration.docaposte.count": ("Établissements et services utilisant Docaposte", "internal", "establishment_service_device"),
        "profile.remuneration.asp.count": ("Établissements et services utilisant l'ASP", "internal", "establishment_service_device"),
        "profile.remuneration.other.count": ("Établissements et services utilisant un autre opérateur", "internal", "establishment_service_device"),
        "profile.remuneration.none.count": ("Établissements et services sans opérateur", "internal", "establishment_service_device"),
        "profile.remuneration.unknown.count": ("Établissements et services — situation non renseignée", "internal", "establishment_service_device"),
        "institution.mdph.cdaph.count": ("Participations aux CDAPH", "observatory", "questionnaire"),
        "institution.mdph.epe.count": ("Participations aux EPE de la MDPH", "observatory", "questionnaire"),
        "institution.mdph.working_groups.count": ("Participations aux groupes de travail MDPH", "observatory", "questionnaire"),
        "people.received.deac": ("Volume annuel déclaré de personnes accompagnées en DEAc", "observatory", "establishment_service_device"),
        "people.received.espo": ("Volume annuel déclaré de personnes accompagnées en ESPO", "observatory", "establishment_service_device"),
        "people.received.esrp": ("Volume annuel déclaré de personnes accompagnées en ESRP", "observatory", "establishment_service_device"),
        "people.received.ueros": ("Volume annuel déclaré de personnes accompagnées en UEROS", "observatory", "establishment_service_device"),
        "people.received.other_eval.professional_assessment": ("Évaluations professionnelles", "observatory", "evaluation_activity"),
        "people.received.other_eval.without_orp_cdaph": ("Autres évaluations sans ORP CDAPH", "observatory", "evaluation_activity"),
        "people.received.other_eval.with_orp_cdaph": ("Autres évaluations avec ORP CDAPH", "observatory", "evaluation_activity"),
        "people.received.other_eval": ("Volume déclaré de personnes reçues dans les autres dispositifs d'évaluation", "observatory", "composite"),
        "people.received.pec": ("Volume déclaré de personnes reçues en PEC", "observatory", "evaluation_activity"),
        "people.received.all": ("Volume déclaré de personnes reçues toutes catégories confondues", "observatory", "composite"),
    }
    label, visibility, grain = catalog[indicator_id]
    return (visibility_order[visibility], grain_order[grain], label.casefold(), indicator_id)


if __name__ == "__main__":
    unittest.main()
