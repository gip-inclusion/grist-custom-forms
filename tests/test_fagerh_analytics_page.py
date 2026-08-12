import base64
import json
import subprocess
import textwrap
import unittest
from unittest.mock import patch

import app
from fagerh_analytics.auth import FAGERH_ANALYTICS_ROLE_KEY, FAGERH_ANALYTICS_SESSION_KEY
from fagerh_analytics.repositories.fake import FakeQuestionnaireRepository


PAGE_PATH = "/Users/ericbarthelemy/Documents/EURES beta/grist-custom-forms/forms/fagerh/analytics.js"


class FagerhAnalyticsPageTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.previous_secret_key = app.app.config.get("SECRET_KEY")
        app.app.config["SECRET_KEY"] = "test-secret-key"
        self.auth_patch = patch.object(app, "_get_admin_credentials", return_value=("admin", "secret"))
        self.auth_patch.start()
        self.addCleanup(self.auth_patch.stop)
        self.repository_patch = patch.object(app, "get_fagerh_analytics_repository", return_value=_overview_repository())
        self.repository_patch.start()
        self.addCleanup(self.repository_patch.stop)
        self.addCleanup(self._restore_secret_key)

    def _restore_secret_key(self):
        app.app.config["SECRET_KEY"] = self.previous_secret_key

    def test_page_authenticated_returns_200(self):
        response = self._get("/admin/fagerh/analytics/", headers=self._auth_headers())
        self.assertEqual(response.status_code, 200)

    def test_page_without_authentication_returns_401(self):
        response = self._get("/admin/fagerh/analytics/")
        self.assertEqual(response.status_code, 401)

    def test_page_returns_503_when_session_signing_is_not_configured(self):
        app.app.config["SECRET_KEY"] = None
        response = self._get("/admin/fagerh/analytics/", headers=self._auth_headers())
        self.assertEqual(response.status_code, 503)
        self.assertIn("FLASK_SECRET_KEY", response.get_data(as_text=True))

    def test_page_contains_required_sections(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertIn("Vue d’ensemble", html)
        self.assertIn("Le réseau en un regard", html)
        self.assertIn("Activité", html)
        self.assertIn("Modalités d’accompagnement", html)
        self.assertIn("Insertion professionnelle", html)
        self.assertIn("Participation institutionnelle", html)
        self.assertIn("Informations internes", html)

    def test_page_uses_etablissements_et_services_terminology(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertIn("Établissements et services", html)
        self.assertNotIn("Prestations directes", html)

    def test_page_does_not_expose_removed_overview_indicators(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertNotIn("Nombre d’établissements et services", html)
        self.assertNotIn("Nombre d'établissements et services", html)
        self.assertNotIn("% CDI", html)
        self.assertNotIn("pourcentage de CDI", html)

    def test_page_contains_etp_analysis_in_activity_tab(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertIn("Analyse des ETP", html)
        self.assertIn('id="activity-etp-grid"', html)
        self.assertIn('id="activity-etp-details"', html)
        self.assertIn('id="activity-etp-metiers"', html)

    def test_page_contains_priority_labels_from_catherine(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertIn("Évaluations préliminaires", html)
        self.assertIn("Hors les murs", html)
        self.assertIn("UEROS", html)
        self.assertIn("ESPO", html)
        self.assertIn("DUI", html)
        self.assertIn("Rémunération", html)

    def test_page_contains_accessible_tab_navigation(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertIn('role="tablist"', html)
        self.assertEqual(html.count('role="tab"'), 7)
        self.assertEqual(html.count('role="tabpanel"'), 7)
        self.assertIn('aria-controls="section-modalites"', html)
        self.assertIn('aria-labelledby="tab-overview"', html)

    def test_page_starts_with_a_single_active_panel(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertIn('<section id="section-overview" class="analytics-card analytics-panel" role="tabpanel" aria-labelledby="tab-overview">', html)
        self.assertIn('id="section-activity" class="analytics-card analytics-panel" role="tabpanel" aria-labelledby="tab-activity" hidden', html)
        self.assertIn('id="section-network-overview" class="analytics-card analytics-panel" role="tabpanel" aria-labelledby="tab-network-overview" hidden', html)

    def test_page_contains_repliable_details_and_print_styles_hook(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        css = self._get("/forms/fagerh/analytics.css").get_data(as_text=True)
        self.assertIn('id="quality-accordion"', html)
        self.assertIn('id="activity-esrp-accordion"', html)
        self.assertIn("@media print", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)

    def test_page_contains_data_quality_block(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertIn("Qualité des données", html)
        self.assertIn('id="quality-invalid-finess"', html)
        self.assertIn('id="quality-unknown-departments"', html)
        self.assertIn('id="quality-unresolved-regions"', html)
        self.assertIn('id="quality-normalized-finess"', html)

    def test_page_contains_double_count_and_deac_notes(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertIn("Une même personne peut être comptée plusieurs fois", html)
        self.assertIn("DEAc n’est pas inclus", html)

    def test_labels_are_associated_to_filters(self):
        html = self._get("/admin/fagerh/analytics/", headers=self._auth_headers()).get_data(as_text=True)
        self.assertIn('for="completion-scope"', html)
        self.assertIn('for="campaign-year"', html)
        self.assertIn('for="region-code"', html)
        self.assertIn('for="department-code"', html)
        self.assertIn('for="finess-main"', html)
        self.assertIn('for="dispositif-filter"', html)

    def test_page_authenticated_initializes_fagerh_session(self):
        response = self._get("/admin/fagerh/analytics/", headers=self._auth_headers())
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as session_data:
            self.assertTrue(session_data.get(FAGERH_ANALYTICS_SESSION_KEY))
            self.assertEqual(session_data.get(FAGERH_ANALYTICS_ROLE_KEY), "admin_global")

    def test_session_does_not_store_password_or_grist_key(self):
        self._get("/admin/fagerh/analytics/", headers=self._auth_headers())
        with self.client.session_transaction() as session_data:
            serialized = json.dumps(dict(session_data))
        self.assertNotIn("secret", serialized)
        self.assertNotIn("GRIST", serialized)

    def test_page_does_not_expose_grist_identifiers_or_admin_password(self):
        response = self._get("/admin/fagerh/analytics/", headers=self._auth_headers())
        body = response.get_data(as_text=True)
        self.assertNotIn("GRIST_API_KEY", body)
        self.assertNotIn("GRIST_DOC_", body)
        self.assertNotIn("secret", body)

    def test_admin_contains_link_to_analytics_page(self):
        response = self._get("/admin/fagerh/", headers=self._auth_headers())
        self.assertIn("/admin/fagerh/analytics/", response.get_data(as_text=True))

    def test_javascript_uses_only_health_and_dashboard_endpoints(self):
        js = self._get("/forms/fagerh/analytics.js").get_data(as_text=True)
        self.assertIn("/api/fagerh-analytics/v1/health", js)
        self.assertIn("/api/fagerh-analytics/v1/dashboard", js)
        self.assertIn('credentials: "same-origin"', js)
        self.assertNotIn("/api/docs/", js)
        self.assertNotIn("GRIST_BASE_URL", js)
        self.assertNotIn("Authorization", js)
        self.assertNotIn("localStorage", js)
        self.assertNotIn("sessionStorage", js)

    def test_build_dashboard_filters_keeps_only_supported_fields(self):
        payload = self._run_node_script(
            """
            const analytics = require(process.argv[1]);
            const filters = analytics.buildDashboardFilters({
              completion_scope: "completed",
              region_code: "11",
              department_code: "75",
              finess_main: "001234567",
              campaign_year: "2025",
              dispositifs: "esrp"
            });
            process.stdout.write(JSON.stringify(filters));
            """
        )
        filters = json.loads(payload)
        self.assertEqual(filters, {
            "completion_scope": "completed",
            "region_code": "11",
            "department_code": "75",
            "finess_main": "001234567",
            "dispositifs": "esrp",
        })

    def test_build_dashboard_filters_defaults_to_all_completion_scope(self):
        payload = self._run_node_script(
            """
            const analytics = require(process.argv[1]);
            process.stdout.write(JSON.stringify(analytics.buildDashboardFilters({})));
            """
        )
        filters = json.loads(payload)
        self.assertEqual(filters, {"completion_scope": "all"})

    def test_sync_capability_driven_filters_hides_campaign_when_unavailable(self):
        payload = self._run_node_script(
            """
            const analytics = require(process.argv[1]);
            const elements = {
              campaignField: {
                hidden: false,
                className: "",
              },
              campaignInput: {
                value: "2025",
                disabled: false,
                attrs: {},
                setAttribute(name, value) { this.attrs[name] = value; },
                removeAttribute(name) { delete this.attrs[name]; }
              }
            };
            analytics.syncCapabilityDrivenFilters(elements, { unavailable_capabilities: ["campaign"] });
            process.stdout.write(JSON.stringify({
              hidden: elements.campaignField.hidden,
              className: elements.campaignField.className,
              disabled: elements.campaignInput.disabled,
              value: elements.campaignInput.value,
              ariaDisabled: elements.campaignInput.attrs["aria-disabled"] || null
            }));
            """
        )
        data = json.loads(payload)
        self.assertEqual(data["hidden"], True)
        self.assertEqual(data["disabled"], True)
        self.assertEqual(data["value"], "")
        self.assertEqual(data["ariaDisabled"], "true")
        self.assertIn("is-disabled", data["className"])

    def test_sync_capability_driven_filters_reenables_campaign_when_available(self):
        payload = self._run_node_script(
            """
            const analytics = require(process.argv[1]);
            const elements = {
              campaignField: {
                hidden: true,
                className: "field is-disabled",
                classList: {
                  add() {},
                  remove() {}
                }
              },
              campaignInput: {
                value: "",
                disabled: true,
                attrs: { "aria-disabled": "true" },
                setAttribute(name, value) { this.attrs[name] = value; },
                removeAttribute(name) { delete this.attrs[name]; }
              }
            };
            analytics.syncCapabilityDrivenFilters(elements, { unavailable_capabilities: [] });
            process.stdout.write(JSON.stringify({
              hidden: elements.campaignField.hidden,
              disabled: elements.campaignInput.disabled,
              ariaDisabled: elements.campaignInput.attrs["aria-disabled"] || null
            }));
            """
        )
        data = json.loads(payload)
        self.assertEqual(data, {"hidden": False, "disabled": False, "ariaDisabled": None})

    def test_overview_model_uses_dashboard_payload(self):
        payload = self._run_node_script(
            """
            const analytics = require(process.argv[1]);
            const model = analytics.buildOverviewModel({
              dashboard: {
                overview: {
                  title: "Vue d’ensemble",
                  questionnaire_count: 12,
                  formula: "Total = ESRP + ESPO + UEROS + PEC + autres dispositifs d’évaluation",
                  completion_notice: "Tous + en cours",
                  indicators: {
                    total: { value: 24, label: "Total", unit: "personnes déclarées" },
                    esrp: { value: 10, label: "ESRP", unit: "personnes déclarées" },
                    espo: { value: 5, label: "ESPO", unit: "personnes déclarées" },
                    ueros: { value: 2, label: "UEROS", unit: "personnes déclarées" },
                    pec: { value: 3, label: "PEC", unit: "personnes déclarées" },
                    other_eval: { value: 4, label: "Autres dispositifs d’évaluation", unit: "personnes déclarées" },
                    preliminary_evaluations: {
                      value: 7,
                      label: "Évaluations préliminaires",
                      unit: "personnes déclarées",
                      children: [
                        { label: "PEC", value: 3 },
                        { label: "Autres dispositifs d’évaluation", value: 4 }
                      ]
                    }
                  },
                  deac: { value: 6, unit: "personnes déclarées", message: "DEAc est affiché séparément et reste exclu du total général." }
                },
                activity: {
                  other_evaluations: {
                    items: [
                      { label: "Évaluations professionnelles", value: 2, unit: "personnes déclarées" },
                      { label: "Sans ORP CDAPH", value: 1, unit: "personnes déclarées" },
                      { label: "Avec ORP CDAPH", value: 1, unit: "personnes déclarées" }
                    ]
                  }
                }
              }
            });
            const rendered = analytics.renderOverviewMarkup(model);
            process.stdout.write(JSON.stringify({ model, rendered }));
            """
        )
        data = json.loads(payload)
        self.assertEqual(data["model"]["totalValue"], 24)
        self.assertEqual(data["model"]["questionnaireCount"], 12)
        self.assertEqual(data["model"]["preliminaryEvaluations"]["value"], 7)
        self.assertIn("Évaluations préliminaires", data["model"]["preliminaryEvaluations"]["label"])
        self.assertIn("10", data["rendered"]["breakdownHtml"])
        self.assertIn("5", data["rendered"]["breakdownHtml"])
        self.assertIn("2", data["rendered"]["breakdownHtml"])
        self.assertIn("3", data["rendered"]["breakdownHtml"])
        self.assertIn("4", data["rendered"]["breakdownHtml"])
        self.assertIn("Évaluations professionnelles", data["rendered"]["otherEvaluationDetailsHtml"])

    def test_network_overview_model_uses_dashboard_payload(self):
        payload = self._run_node_script(
            """
            const analytics = require(process.argv[1]);
            const model = analytics.buildNetworkOverviewModel({
              dashboard: {
                network_overview: {
                  title: "Le réseau en un regard",
                  status: "available",
                  message: "Comparatif dynamique chargé.",
                  devices: [
                    {
                      id: "ueros",
                      label: "UEROS",
                      subtitle: "Unités d’évaluation",
                      public: {
                        text: "Personnes atteintes de lésions cérébrales acquises.",
                        metrics: [
                          { label: "Personnes reçues", value: 2, unit: "personnes déclarées" }
                        ]
                      },
                      dispositifs: {
                        text: "Lecture au grain FINESS canonique distinct.",
                        metrics: [
                          { label: "Établissements et services distincts", value: 1, unit: "FINESS canoniques distincts" }
                        ]
                      },
                      objectives: {
                        items: ["Préconiser une orientation concrète."]
                      },
                      results: {
                        items: [
                          {
                            label: "Préconisations UEROS",
                            children: [{ label: "Maintien dans l’emploi", value: 1, unit: "préconisations" }]
                          }
                        ]
                      }
                    }
                  ]
                }
              }
            });
            process.stdout.write(JSON.stringify(model));
            """
        )
        model = json.loads(payload)
        self.assertEqual(model["title"], "Le réseau en un regard")
        self.assertEqual(model["devices"][0]["id"], "ueros")
        self.assertEqual(model["devices"][0]["public"]["metrics"][0]["value"], 2)

    def test_resolve_tab_id_supports_direct_hashes_and_legacy_hashes(self):
        payload = self._run_node_script(
            """
            const analytics = require(process.argv[1]);
            process.stdout.write(JSON.stringify({
              defaultTab: analytics.resolveTabId(""),
              direct: analytics.resolveTabId("#section-participation"),
              short: analytics.resolveTabId("#network"),
              legacy: analytics.resolveTabId("#section-modalites"),
              unknown: analytics.resolveTabId("#does-not-exist")
            }));
            """
        )
        data = json.loads(payload)
        self.assertEqual(data["defaultTab"], "section-overview")
        self.assertEqual(data["direct"], "section-participation")
        self.assertEqual(data["short"], "section-network-overview")
        self.assertEqual(data["legacy"], "section-modalites")
        self.assertEqual(data["unknown"], "section-overview")

    def test_existing_routes_and_analytics_endpoints_continue_to_work(self):
        self.assertEqual(self._get("/health").status_code, 200)
        response = self.client.post(
            "/api/fagerh-analytics/v1/indicators/people.received.all",
            headers=self._auth_headers(),
            json={"filters": {}},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["result"]["value"], 24)

    def _get(self, path, **kwargs):
        response = self.client.get(path, **kwargs)
        self.addCleanup(response.close)
        return response

    def _run_node_script(self, script):
        completed = subprocess.run(
            ["node", "-e", textwrap.dedent(script), PAGE_PATH],
            check=True,
            text=True,
            capture_output=True,
        )
        return completed.stdout

    def _auth_headers(self):
        token = base64.b64encode(b"admin:secret").decode("ascii")
        return {"Authorization": f"Basic {token}"}


def _overview_repository():
    return FakeQuestionnaireRepository(rows=[
        {
            "uuid": "uuid-esrp",
            "campaign_year": 2025,
            "saisie_terminee": True,
            "finess_main": "010000001",
            "es_departement": "75",
            "check_esrp": True,
            "q53_accompagnes__esrp": 10,
            "q38_dui": "Oui",
            "q38_dui_lequel": "Ogyris",
            "q40_remuneration": "Oui",
            "q40_operateur": "Docaposte",
        },
        {
            "uuid": "uuid-espo",
            "campaign_year": 2025,
            "saisie_terminee": False,
            "finess_main": "010000002",
            "es_departement": "69",
            "check_espo": True,
            "q53_accompagnes__espo": 5,
            "q38_dui": "Non",
            "q40_remuneration": "Oui",
            "q40_operateur": "ASP",
        },
        {
            "uuid": "uuid-ueros",
            "campaign_year": 2025,
            "saisie_terminee": True,
            "finess_main": "010000003",
            "es_departement": "13",
            "check_ueros": True,
            "q53_accompagnes__ueros": 2,
        },
        {
            "uuid": "uuid-pec",
            "campaign_year": 2025,
            "saisie_terminee": True,
            "finess_main": "010000004",
            "es_departement": "59",
            "prestations_json": {"cond-pec": {"fileActive": 3}},
            "prestations_details_json": {
                "__wizard_v3_state": {
                    "runtime": {
                        "conditionalDefs": [
                            {"id": "cond-pec", "name": "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"}
                        ]
                    }
                }
            },
            "nombre_participations_epe": 2,
            "nombre_participations_cdaph": 1,
            "nombre_groupes_travail_mdph": 4,
        },
        {
            "uuid": "uuid-other",
            "campaign_year": 2025,
            "saisie_terminee": False,
            "finess_main": "010000005",
            "es_departement": "44",
            "prestations_json": {
                "cond-prof": {"directSansOrp": {"rows": {"pec": {"beneficiaires": 2}}}},
                "cond-other-sans": {"fileActive": 1},
                "cond-other-avec": {"fileActive": 1},
            },
            "prestations_details_json": {
                "__wizard_v3_state": {
                    "runtime": {
                        "conditionalDefs": [
                            {"id": "cond-prof", "name": "Directes hors ORP CDAPH - Évaluations professionnelles"},
                            {"id": "cond-other-sans", "name": "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH"},
                            {"id": "cond-other-avec", "name": "Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH"},
                        ]
                    }
                }
            },
        },
    ])


if __name__ == "__main__":
    unittest.main()
