import unittest
from unittest.mock import patch

from fagerh_analytics.dashboard import build_dashboard_payload
from fagerh_analytics.domain import UserContext
from fagerh_analytics.repositories.fake import FakeQuestionnaireRepository


class FagerhAnalyticsDashboardTest(unittest.TestCase):
    def test_dashboard_returns_expected_values_for_all_completed_and_in_progress(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "u1", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 10},
            {"uuid": "u2", "campaign_year": 2025, "saisie_terminee": False, "finess_main": "010000002", "check_espo": True, "q53_accompagnes__espo": 5},
            {"uuid": "u3", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000003", "check_ueros": True, "q53_accompagnes__ueros": 2},
            {"uuid": "u3b", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000003", "check_deac": True, "q53_accompagnes__deac": 6},
            {
                "uuid": "u4",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "010000004",
                "prestations_json": {"cond-pec": {"fileActive": 3}},
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [
                    {"id": "cond-pec", "name": "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"},
                ]}}},
            },
            {
                "uuid": "u5",
                "campaign_year": 2025,
                "saisie_terminee": False,
                "finess_main": "010000005",
                "prestations_json": {"cond-other": {"fileActive": 4}},
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [
                    {"id": "cond-other", "name": "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH"},
                ]}}},
            },
        ])

        all_payload = build_dashboard_payload(repository, UserContext("u", "admin_global")).payload
        completed_payload = build_dashboard_payload(repository, UserContext("u", "admin_global"), {"completion_scope": "completed"}).payload
        in_progress_payload = build_dashboard_payload(repository, UserContext("u", "admin_global"), {"completion_scope": "in_progress"}).payload

        self.assertEqual(all_payload["overview"]["status"], "available")
        self.assertEqual(all_payload["overview"]["questionnaire_count"], 6)
        self.assertEqual(all_payload["overview"]["indicators"]["preliminary_evaluations"]["value"], 7)
        self.assertEqual(all_payload["overview"]["indicators"]["total"]["value"], 24)
        self.assertEqual(all_payload["overview"]["deac"]["value"], 6)
        self.assertEqual([item["id"] for item in all_payload["network_overview"]["devices"]], ["ueros", "espo", "esrp"])
        self.assertEqual(all_payload["network_overview"]["devices"][0]["public"]["metrics"][0]["value"], 2)
        self.assertEqual(all_payload["network_overview"]["devices"][1]["public"]["metrics"][0]["value"], 5)
        self.assertEqual(all_payload["network_overview"]["devices"][2]["public"]["metrics"][0]["value"], 10)
        self.assertEqual(completed_payload["overview"]["questionnaire_count"], 4)
        self.assertEqual(completed_payload["overview"]["indicators"]["total"]["value"], 15)
        self.assertEqual(in_progress_payload["overview"]["questionnaire_count"], 2)
        self.assertEqual(in_progress_payload["overview"]["indicators"]["total"]["value"], 9)

    def test_dashboard_keeps_quality_section_non_blocking_when_quality_fails(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "u1", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 10},
        ])

        with patch("fagerh_analytics.dashboard._build_quality_section", side_effect=ValueError("boom")):
            payload = build_dashboard_payload(repository, UserContext("u", "admin_global")).payload

        self.assertEqual(payload["overview"]["status"], "available")
        self.assertEqual(payload["activity"]["status"], "available")
        self.assertEqual(payload["quality"]["status"], "error")
        self.assertIn("Qualité des données indisponible", payload["quality"]["message"])

    def test_establishments_expose_identity_status_devices_and_volumes(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "u-establishment",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "440036440",
                "es_nom": "ESRP La Tourmaline",
                "department_code": "44",
                "check_esrp": True,
                "prestations_json": {"cond-esrp": {"fileActive": 71, "sorties": 73}},
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [
                    {"id": "cond-esrp", "name": "Directes ORP CDAPH - ESRP"},
                ]}}},
            },
        ])

        payload = build_dashboard_payload(repository, UserContext("u", "admin_global")).payload
        establishment = payload["establishments"]["items"][0]

        self.assertEqual(establishment["name"], "ESRP La Tourmaline")
        self.assertEqual(establishment["finess_main"], "440036440")
        self.assertEqual(establishment["department_code"], "44")
        self.assertEqual(establishment["statuses"], ["completed"])
        self.assertEqual(establishment["dispositifs"], ["ESRP"])
        self.assertEqual(establishment["totals"]["esrp"], 144)

    def test_dashboard_keeps_overview_when_participation_fails(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "u1", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 10},
        ])

        with patch("fagerh_analytics.dashboard._build_participation_section", side_effect=ValueError("boom")):
            payload = build_dashboard_payload(repository, UserContext("u", "admin_global")).payload

        self.assertEqual(payload["overview"]["status"], "available")
        self.assertEqual(payload["participation_institutionnelle"]["status"], "error")
        self.assertIn("Participation institutionnelle indisponible", payload["participation_institutionnelle"]["message"])

    def test_dashboard_supports_dispositif_filter(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "u1", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 10},
            {"uuid": "u2", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000002", "check_espo": True, "q53_accompagnes__espo": 5},
            {"uuid": "u3", "campaign_year": 2025, "saisie_terminee": True, "finess_main": "010000003", "check_deac": True, "q53_accompagnes__deac": 4},
        ])

        payload = build_dashboard_payload(
            repository,
            UserContext("u", "admin_global"),
            {"dispositifs": "esrp"},
        ).payload

        self.assertEqual(payload["overview"]["indicators"]["total"]["value"], 10)
        self.assertEqual(payload["overview"]["indicators"]["esrp"]["value"], 10)
        self.assertEqual(payload["overview"]["indicators"]["espo"]["value"], 0)
        self.assertEqual(payload["overview"]["questionnaire_count"], 1)
        self.assertEqual(payload["filters"]["applied"]["dispositifs"], ("esrp",))
        self.assertEqual([item["id"] for item in payload["network_overview"]["devices"]], ["esrp"])

        deac_payload = build_dashboard_payload(
            repository,
            UserContext("u", "admin_global"),
            {"dispositifs": "deac"},
        ).payload
        self.assertEqual(deac_payload["overview"]["indicators"]["total"]["value"], 0)
        self.assertEqual(deac_payload["overview"]["deac"]["value"], 4)
        self.assertEqual(deac_payload["overview"]["questionnaire_count"], 1)
        self.assertEqual(deac_payload["network_overview"]["devices"], [])

    def test_dashboard_network_overview_uses_declared_etp_from_metiers_json(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "u1",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "010000001",
                "check_esrp": True,
                "q53_accompagnes__esrp": 10,
                "etp_esrp": "2.0",
                "etp_espo": "0.5",
                "etp_ueros": "0.25",
                "metiers_json": [
                    {"metier": "Formateur", "mode": "Externe", "etp": "1.5"},
                    {"metier": "Psychologue", "mode": "Interne", "etpCdi": "0.5", "etpCdd": "0.25"},
                ],
            },
            {
                "uuid": "u2",
                "campaign_year": 2025,
                "saisie_terminee": False,
                "finess_main": "010000002",
                "check_esrp": True,
                "q53_accompagnes__esrp": 5,
                "etp_esrp": "1.0",
                "etp_deac": "0.75",
                "metiers_json": '[{"metier":"Assistant social","mode":"Externe","etp":"2"}]',
            },
        ])

        payload = build_dashboard_payload(repository, UserContext("u", "admin_global")).payload
        esrp_device = next(device for device in payload["network_overview"]["devices"] if device["id"] == "esrp")
        etp_metric = esrp_device["dispositifs"]["metrics"][3]

        self.assertEqual(etp_metric["label"], "ETP déclarés")
        self.assertEqual(etp_metric["unit"], "ETP déclarés")
        self.assertEqual(etp_metric["value"], 4.25)
        self.assertEqual(etp_metric["status"], "available")

        etp_analysis = payload["activity"]["etp_analysis"]
        self.assertEqual(etp_analysis["cards"][0]["label"], "ETP déclarés tous dispositifs")
        self.assertEqual(etp_analysis["cards"][0]["value"], 4.5)
        self.assertEqual(etp_analysis["cards"][1]["value"], 3)
        self.assertEqual(etp_analysis["cards"][4]["value"], 0.75)
        self.assertEqual(etp_analysis["cards"][5]["value"], 4.25)
        self.assertEqual(etp_analysis["details"][0]["label"], "Cible dispositifs hors DEAc")
        self.assertEqual(etp_analysis["details"][0]["value"], 3.75)
        self.assertEqual(etp_analysis["details"][1]["value"], 0.5)
        self.assertEqual(etp_analysis["details"][2]["value"], 0.25)
        self.assertEqual(etp_analysis["details"][3]["value"], 3.5)
        self.assertEqual(etp_analysis["details"][4]["value"], 0.5)
        self.assertEqual(etp_analysis["top_metiers"][0]["label"], "Assistant social")

    def test_dashboard_computes_employment_rates_from_questionnaire_fields(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "u-emploi-1",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "010000011",
                "prestations_json": {
                    "cond-emploi-1": {
                        "directAvecOrp": {
                            "row": {
                                "emploi_sorties_n_1": "18",
                                "emploi_nb_repondants": "12",
                                "emploi_acces_nb": "6",
                                "emploi_presence_nb": "4",
                                "emploi_acces_cdi": "2",
                            },
                        },
                    },
                },
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [
                    {"id": "cond-emploi-1", "name": "Directes ORP CDAPH - Parcours à visée socio-professionnelle - Préparation d'un projet professionnel (orientation hors ESPO)"},
                ]}}},
            },
            {
                "uuid": "u-emploi-2",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "010000012",
                "prestations_json": {
                    "cond-emploi-2": {
                        "directAvecOrp": {
                            "row": {
                                "emploi_sorties_n_1": "10",
                                "emploi_nb_repondants": "8",
                                "emploi_acces_nb": "2",
                                "emploi_presence_nb": "1",
                                "emploi_acces_cdd_plus6": "1",
                            },
                        },
                    },
                },
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [
                    {"id": "cond-emploi-2", "name": "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"},
                ]}}},
            },
        ])

        payload = build_dashboard_payload(repository, UserContext("u", "admin_global")).payload
        insertion_items = payload["insertion"]["items"]
        access_rate = next(item for item in insertion_items if item["id"] == "employment.access_rate")
        presence_rate = next(item for item in insertion_items if item["id"] == "employment.presence_rate")
        snapshot = next(item for item in insertion_items if item["id"] == "employment_snapshot")

        self.assertEqual(access_rate["status"], "available")
        self.assertEqual(access_rate["value"], 40.0)
        self.assertEqual(access_rate["children"][0]["value"], 8)
        self.assertEqual(access_rate["children"][1]["value"], 20)
        self.assertEqual(presence_rate["value"], 25.0)
        self.assertEqual(snapshot["children"][0]["value"], 28)
        self.assertEqual(snapshot["children"][1]["value"], 20)
        self.assertEqual(snapshot["children"][2]["value"], 8)
        self.assertEqual(snapshot["children"][3]["value"], 5)

    def test_dashboard_maps_committee_participation_from_fields_and_snapshot(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "u-comm-1",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "010000021",
                "q48_cle": "Oui",
                "q49_cre": "Non (FAGERH représentée)",
                "q50_fiphfp": "Non",
            },
            {
                "uuid": "u-comm-2",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "010000022",
                "prestations_details_json": {
                    "__wizard_v3_state": {
                        "controls": {
                            "byName": {
                                "ctx-q48": {"type": "radio", "value": "Non"},
                                "ctx-q49": {"type": "radio", "value": "Oui"},
                                "ctx-q50": {"type": "radio", "value": "Non (FAGERH représentée)"},
                            },
                        },
                    },
                },
            },
        ])

        payload = build_dashboard_payload(repository, UserContext("u", "admin_global")).payload
        items = payload["participation_institutionnelle"]["items"]
        cle_cre = next(item for item in items if item["id"] == "territorial_cle_cre")
        fiphfp = next(item for item in items if item["id"] == "territorial_fiphfp")

        self.assertEqual(cle_cre["status"], "available")
        self.assertEqual(cle_cre["value"], 3)
        self.assertEqual(cle_cre["children"][0]["label"], "CLE en direct")
        self.assertEqual(cle_cre["children"][0]["value"], 1)
        self.assertEqual(cle_cre["children"][1]["label"], "CRE en direct")
        self.assertEqual(cle_cre["children"][1]["value"], 1)
        self.assertEqual(cle_cre["children"][2]["label"], "CRE via FAGERH")
        self.assertEqual(cle_cre["children"][2]["value"], 1)
        self.assertEqual(fiphfp["value"], 1)
        self.assertEqual(fiphfp["children"][0]["label"], "FIPHFP via FAGERH")
        self.assertEqual(fiphfp["children"][0]["value"], 1)

    def test_dashboard_internal_dui_and_remuneration_count_each_questionnaire_once(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "u-internal-1",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "010000031",
                "check_esrp": True,
                "check_espo": True,
                "q38_dui": "Oui",
                "q38_dui_lequel": "Ogyris",
                "q40_remuneration": "Oui",
                "q40_operateur": "Docaposte",
            },
            {
                "uuid": "u-internal-2",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "010000032",
                "check_ueros": True,
                "q38_dui": "Non",
                "q40_remuneration": "Non",
                "q40_operateur": "",
            },
        ])

        payload = build_dashboard_payload(repository, UserContext("u", "admin_global")).payload
        internal = payload["internal"]

        self.assertEqual(internal["dui"]["yes"], 1)
        self.assertEqual(internal["dui"]["no"], 1)
        self.assertEqual(internal["dui"]["unknown"], 0)
        self.assertEqual(internal["dui"]["tools"][0]["label"], "Ogyris")
        self.assertEqual(internal["dui"]["tools"][0]["count"], 1)
        self.assertEqual(internal["remuneration"]["docaposte"], 1)
        self.assertEqual(internal["remuneration"]["none"], 1)

    def test_dashboard_network_overview_exposes_espo_and_ueros_journees_when_available(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "u-espo",
                "campaign_year": 2025,
                "saisie_terminee": True,
                "finess_main": "010000010",
                "check_espo": True,
                "q53_accompagnes__espo": 12,
                "prestations_json": {
                    "cond-espo": {
                        "journees": "120",
                        "journeesTheoriques": "150",
                        "preconisationsBloc": {"emploi_ordinaire": "4"},
                    },
                    "cond-ueros": {
                        "journees": "45",
                        "journeesTheoriques": "60",
                        "preconisationsBloc": {"maintien_emploi": "2"},
                    },
                },
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [
                    {"id": "cond-espo", "name": "Directes ORP CDAPH - ESPO"},
                    {"id": "cond-ueros", "name": "Directes ORP CDAPH - UEROS"},
                ]}}},
            },
        ])

        payload = build_dashboard_payload(repository, UserContext("u", "admin_global")).payload
        espo_device = next(device for device in payload["network_overview"]["devices"] if device["id"] == "espo")
        ueros_device = next(device for device in payload["network_overview"]["devices"] if device["id"] == "ueros")
        espo_activity = espo_device["results"]["items"][1]
        ueros_activity = ueros_device["results"]["items"][1]

        self.assertEqual(espo_activity["label"], "Journées ou volumes d’activité")
        self.assertEqual(espo_activity["children"][0]["label"], "Journées réalisées")
        self.assertEqual(espo_activity["children"][0]["value"], 120)
        self.assertEqual(espo_activity["children"][1]["value"], 150)
        self.assertEqual(ueros_activity["children"][0]["value"], 45)
        self.assertEqual(ueros_activity["children"][1]["value"], 60)


if __name__ == "__main__":
    unittest.main()
