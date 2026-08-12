import unittest

from fagerh_analytics.catalog import get_indicator_definition
from fagerh_analytics.engine import (
    AnalyticsEngine,
    DataConsistencyError,
    DataQualityError,
    UnknownIndicatorError,
    project_questionnaire,
)
from fagerh_analytics.evaluation_projection import project_evaluation_activities
from fagerh_analytics.filters import FilterValidationError, IncompatibleFilterError
from fagerh_analytics.permissions import (
    InvalidUserContextError,
    PermissionDeniedError,
    ensure_export_allowed,
    get_scope,
)
from fagerh_analytics.repositories.fake import FakeQuestionnaireRepository
from fagerh_analytics.domain import UserContext


class FagerhAnalyticsEngineTest(unittest.TestCase):
    def test_two_distinct_uuids_return_two(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1"},
            {"uuid": "uuid-2"},
        ]))

        result = engine.compute_indicator("questionnaires.count")

        self.assertEqual(result.value, 2)

    def test_duplicate_uuid_is_counted_once(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1"},
            {"uuid": "uuid-1"},
        ]))

        result = engine.compute_indicator("questionnaires.count")

        self.assertEqual(result.value, 1)

    def test_empty_or_missing_uuid_is_ignored(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1"},
            {"uuid": ""},
            {"uuid": "   "},
            {},
        ]))

        result = engine.compute_indicator("questionnaires.count")

        self.assertEqual(result.value, 1)

    def test_empty_dataset_returns_zero(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        result = engine.compute_indicator("questionnaires.count")

        self.assertEqual(result.value, 0)

    def test_unknown_indicator_raises_explicit_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(UnknownIndicatorError) as raised:
            engine.compute_indicator("unknown.indicator")

        self.assertEqual(str(raised.exception), "Unknown indicator: unknown.indicator")

    def test_indicator_result_contains_required_contract_fields(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1"},
        ]))

        result = engine.compute_indicator("questionnaires.count")

        self.assertEqual(result.indicator_id, "questionnaires.count")
        self.assertEqual(result.label, "Questionnaires")
        self.assertEqual(result.value, 1)
        self.assertEqual(result.unit, "count")
        self.assertEqual(result.privacy_status, "visible")
        self.assertEqual(result.confidence_level, "confirmed by the code")
        self.assertEqual(result.source, {
            "dataset": "questionnaires",
            "repository": "fake",
        })

    def test_dui_yes_count_returns_two_distinct_establishments_and_services(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
            {"campaign_year": 2025, "finess_main": "010000002", "dispositif": "espo", "q38_dui": "Oui"},
        ]))

        result = engine.compute_indicator("profile.dui.yes.count")

        self.assertEqual(result.value, 2)

    def test_dui_yes_and_no_counts_are_split(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
            {"campaign_year": 2025, "finess_main": "010000002", "dispositif": "espo", "q38_dui": "Non"},
        ]))

        yes_result = engine.compute_indicator("profile.dui.yes.count")
        no_result = engine.compute_indicator("profile.dui.no.count")

        self.assertEqual(yes_result.value, 1)
        self.assertEqual(no_result.value, 1)

    def test_dui_empty_or_missing_value_is_ignored(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": ""},
            {"campaign_year": 2025, "finess_main": "010000002", "dispositif": "espo"},
            {"campaign_year": 2025, "finess_main": "010000003", "dispositif": "ueros", "q38_dui": "Oui"},
        ]))

        result = engine.compute_indicator("profile.dui.yes.count")

        self.assertEqual(result.value, 1)

    def test_dui_duplicate_business_key_is_counted_once(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
        ]))

        result = engine.compute_indicator("profile.dui.yes.count")

        self.assertEqual(result.value, 1)

    def test_dui_same_finess_two_dispositifs_is_counted_twice(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "espo", "q38_dui": "Oui"},
        ]))

        result = engine.compute_indicator("profile.dui.yes.count")

        self.assertEqual(result.value, 2)

    def test_dui_same_finess_two_campaigns_is_counted_twice(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2024, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
        ]))

        result = engine.compute_indicator("profile.dui.yes.count")

        self.assertEqual(result.value, 2)

    def test_dui_contradictory_values_raise_explicit_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Non"},
        ]))

        with self.assertRaises(DataConsistencyError) as raised:
            engine.compute_indicator("profile.dui.yes.count")

        self.assertEqual(
            str(raised.exception),
            "Contradictory q38_dui values for business key 2025/010000001/esrp: Oui vs Non",
        )

    def test_dui_labels_use_etablissements_et_services_wording(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
        ]))

        yes_result = engine.compute_indicator("profile.dui.yes.count")
        no_result = engine.compute_indicator("profile.dui.no.count")

        self.assertIn("établissements et services", yes_result.label.lower())
        self.assertIn("établissements et services", no_result.label.lower())

    def test_dui_result_source_mentions_dataset_and_q38_dui_field(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q38_dui": "Oui"},
        ]))

        result = engine.compute_indicator("profile.dui.yes.count")

        self.assertEqual(result.source, {
            "dataset": "questionnaires",
            "repository": "fake",
            "field": "q38_dui",
        })

    def test_remuneration_yes_docaposte_counts_in_docaposte(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "Docaposte"},
        ]))

        result = engine.compute_indicator("profile.remuneration.docaposte.count")

        self.assertEqual(result.value, 1)

    def test_remuneration_docaposte_variant_is_recognized(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "  OUI ", "q40_operateur": "Doca Poste"},
        ]))

        result = engine.compute_indicator("profile.remuneration.docaposte.count")

        self.assertEqual(result.value, 1)

    def test_remuneration_yes_asp_counts_in_asp(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "ASP"},
        ]))

        result = engine.compute_indicator("profile.remuneration.asp.count")

        self.assertEqual(result.value, 1)

    def test_remuneration_agence_de_services_et_de_paiement_is_recognized_as_asp(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "q40_remuneration": "Oui",
                "q40_operateur": "Agence de services et de paiement",
            },
        ]))

        result = engine.compute_indicator("profile.remuneration.asp.count")

        self.assertEqual(result.value, 1)

    def test_remuneration_unknown_operator_counts_in_other(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "Operateur X"},
        ]))

        result = engine.compute_indicator("profile.remuneration.other.count")

        self.assertEqual(result.value, 1)

    def test_remuneration_non_with_empty_operator_counts_in_none(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Non", "q40_operateur": ""},
        ]))

        result = engine.compute_indicator("profile.remuneration.none.count")

        self.assertEqual(result.value, 1)

    def test_remuneration_missing_value_counts_in_unknown(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp"},
        ]))

        result = engine.compute_indicator("profile.remuneration.unknown.count")

        self.assertEqual(result.value, 1)

    def test_remuneration_yes_with_empty_operator_counts_in_unknown(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": " "},
        ]))

        result = engine.compute_indicator("profile.remuneration.unknown.count")

        self.assertEqual(result.value, 1)

    def test_remuneration_same_key_two_docaposte_variants_count_once(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "Docaposte"},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "oui", "q40_operateur": "Doca Poste"},
        ]))

        result = engine.compute_indicator("profile.remuneration.docaposte.count")

        self.assertEqual(result.value, 1)

    def test_remuneration_same_finess_two_dispositifs_count_twice(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "Docaposte"},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "espo", "q40_remuneration": "Oui", "q40_operateur": "Docaposte"},
        ]))

        result = engine.compute_indicator("profile.remuneration.docaposte.count")

        self.assertEqual(result.value, 2)

    def test_remuneration_same_finess_two_campaigns_count_twice(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2024, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "Docaposte"},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "Docaposte"},
        ]))

        result = engine.compute_indicator("profile.remuneration.docaposte.count")

        self.assertEqual(result.value, 2)

    def test_remuneration_docaposte_then_asp_raises_contradiction(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "Docaposte"},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "ASP"},
        ]))

        with self.assertRaises(DataConsistencyError) as raised:
            engine.compute_indicator("profile.remuneration.docaposte.count")

        self.assertEqual(
            str(raised.exception),
            "Contradictory remuneration values for business key 2025/010000001/esrp: docaposte vs asp",
        )

    def test_remuneration_yes_then_non_raises_contradiction(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "Docaposte"},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Non", "q40_operateur": ""},
        ]))

        with self.assertRaises(DataConsistencyError) as raised:
            engine.compute_indicator("profile.remuneration.docaposte.count")

        self.assertEqual(
            str(raised.exception),
            "Contradictory remuneration values for business key 2025/010000001/esrp: docaposte vs none",
        )

    def test_remuneration_non_with_operator_raises_incoherence(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Non", "q40_operateur": "Docaposte"},
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("profile.remuneration.none.count")

        self.assertEqual(
            str(raised.exception),
            "Inconsistent remuneration values: q40_remuneration=Non but q40_operateur is set to Docaposte",
        )

    def test_remuneration_word_containing_asp_is_not_recognized_as_asp(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q40_remuneration": "Oui", "q40_operateur": "caspian services"},
        ]))

        result = engine.compute_indicator("profile.remuneration.other.count")

        self.assertEqual(result.value, 1)

    def test_mdph_epe_adds_origine_and_limitrophes(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {
                        "indirect": {
                            "rows": {
                                "epe": {"origine": 2, "limitrophes": 3},
                            },
                        },
                    },
                },
            },
        ]))

        result = engine.compute_indicator("institution.mdph.epe.count")

        self.assertEqual(result.value, 5)

    def test_mdph_cdaph_accepts_numeric_strings(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {
                        "indirect": {
                            "rows": {
                                "cdaph": {"origine": " 4 ", "limitrophes": "5"},
                            },
                        },
                    },
                },
            },
        ]))

        result = engine.compute_indicator("institution.mdph.cdaph.count")

        self.assertEqual(result.value, 9)

    def test_mdph_working_groups_missing_block_returns_zero(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {},
            },
        ]))

        result = engine.compute_indicator("institution.mdph.working_groups.count")

        self.assertEqual(result.value, 0)

    def test_mdph_empty_field_is_treated_as_zero(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {
                        "indirect": {
                            "rows": {
                                "epe": {"origine": "", "limitrophes": "2"},
                            },
                        },
                    },
                },
            },
        ]))

        result = engine.compute_indicator("institution.mdph.epe.count")

        self.assertEqual(result.value, 2)

    def test_mdph_negative_value_raises_data_quality_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {
                        "indirect": {
                            "rows": {
                                "epe": {"origine": -1, "limitrophes": 0},
                            },
                        },
                    },
                },
            },
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("institution.mdph.epe.count")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for epe.origine: negative values are not accepted",
        )

    def test_mdph_non_numeric_text_raises_data_quality_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {
                        "indirect": {
                            "rows": {
                                "cdaph": {"origine": "abc", "limitrophes": 0},
                            },
                        },
                    },
                },
            },
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("institution.mdph.cdaph.count")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for cdaph.origine: abc",
        )

    def test_mdph_boolean_value_is_refused(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {
                        "indirect": {
                            "rows": {
                                "groupes_travail": {"origine": True, "limitrophes": 0},
                            },
                        },
                    },
                },
            },
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("institution.mdph.working_groups.count")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for groupes_travail.origine: booleans are not accepted",
        )

    def test_mdph_non_integer_decimal_is_refused(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {
                        "indirect": {
                            "rows": {
                                "epe": {"origine": 2.5, "limitrophes": 0},
                            },
                        },
                    },
                },
            },
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("institution.mdph.epe.count")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for epe.origine: non-integer decimals are not accepted",
        )

    def test_mdph_integer_decimal_is_accepted(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {
                        "indirect": {
                            "rows": {
                                "epe": {"origine": 3.0, "limitrophes": "2.0"},
                            },
                        },
                    },
                },
            },
        ]))

        result = engine.compute_indicator("institution.mdph.epe.count")

        self.assertEqual(result.value, 5)

    def test_mdph_two_questionnaires_add_their_participations(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {"indirect": {"rows": {"epe": {"origine": 1, "limitrophes": 2}}}},
                },
            },
            {
                "campaign_year": 2025,
                "finess_main": "010000002",
                "dispositif": "espo",
                "prestations_json": {
                    "cond-1": {"indirect": {"rows": {"epe": {"origine": 3, "limitrophes": 4}}}},
                },
            },
        ]))

        result = engine.compute_indicator("institution.mdph.epe.count")

        self.assertEqual(result.value, 10)

    def test_mdph_same_key_identical_data_counts_once(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {"indirect": {"rows": {"cdaph": {"origine": 2, "limitrophes": 1}}}},
                },
            },
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-99": {"indirect": {"rows": {"cdaph": {"origine": 2, "limitrophes": 1}}}},
                },
            },
        ]))

        result = engine.compute_indicator("institution.mdph.cdaph.count")

        self.assertEqual(result.value, 3)

    def test_mdph_same_key_contradictory_data_raises_consistency_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {"indirect": {"rows": {"groupes_travail": {"origine": 2, "limitrophes": 1}}}},
                },
            },
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-2": {"indirect": {"rows": {"groupes_travail": {"origine": 2, "limitrophes": 2}}}},
                },
            },
        ]))

        with self.assertRaises(DataConsistencyError) as raised:
            engine.compute_indicator("institution.mdph.working_groups.count")

        self.assertEqual(
            str(raised.exception),
            "Contradictory MDPH participation values for business key 2025/010000001/esrp and block groupes_travail: (2, 1) vs (2, 2)",
        )

    def test_mdph_indicators_remain_separate(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {
                        "indirect": {
                            "rows": {
                                "epe": {"origine": 1, "limitrophes": 1},
                                "cdaph": {"origine": 2, "limitrophes": 0},
                                "groupes_travail": {"origine": 3, "limitrophes": 0},
                            },
                        },
                    },
                },
            },
        ]))

        self.assertEqual(engine.compute_indicator("institution.mdph.epe.count").value, 2)
        self.assertEqual(engine.compute_indicator("institution.mdph.cdaph.count").value, 2)
        self.assertEqual(engine.compute_indicator("institution.mdph.working_groups.count").value, 3)

    def test_mdph_result_source_mentions_block_and_subfields(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "prestations_json": {
                    "cond-1": {"indirect": {"rows": {"epe": {"origine": 1, "limitrophes": 1}}}},
                },
            },
        ]))

        result = engine.compute_indicator("institution.mdph.epe.count")

        self.assertEqual(result.source, {
            "dataset": "questionnaires",
            "repository": "fake",
            "field": "prestations_json",
            "block": "epe",
            "subfields": "origine,limitrophes",
            "business_key": "campaign_year+finess_main+dispositif",
        })

    def test_people_received_esrp_with_integer_returns_expected_volume(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q53_accompagnes__esrp": 7},
        ]))

        result = engine.compute_indicator("people.received.esrp")

        self.assertEqual(result.value, 7)

    def test_people_received_espo_with_numeric_string_is_accepted(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "espo", "q53_accompagnes__espo": " 8 "},
        ]))

        result = engine.compute_indicator("people.received.espo")

        self.assertEqual(result.value, 8)

    def test_people_received_ueros_missing_value_returns_zero(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "ueros"},
        ]))

        result = engine.compute_indicator("people.received.ueros")

        self.assertEqual(result.value, 0)

    def test_people_received_deac_accepts_integer_float(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "deac", "q53_accompagnes__deac": 3.0},
        ]))

        result = engine.compute_indicator("people.received.deac")

        self.assertEqual(result.value, 3)

    def test_people_received_negative_value_raises_data_quality_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q53_accompagnes__esrp": -1},
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("people.received.esrp")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for q53_accompagnes__esrp: negative values are not accepted",
        )

    def test_people_received_non_numeric_text_raises_data_quality_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "espo", "q53_accompagnes__espo": "abc"},
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("people.received.espo")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for q53_accompagnes__espo: abc",
        )

    def test_people_received_boolean_is_refused(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "ueros", "q53_accompagnes__ueros": True},
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("people.received.ueros")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for q53_accompagnes__ueros: booleans are not accepted",
        )

    def test_people_received_non_integer_decimal_is_refused(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "deac", "q53_accompagnes__deac": 2.5},
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("people.received.deac")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for q53_accompagnes__deac: non-integer decimals are not accepted",
        )

    def test_people_received_two_distinct_keys_are_added(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q53_accompagnes__esrp": 2},
            {"campaign_year": 2025, "finess_main": "010000002", "dispositif": "esrp", "q53_accompagnes__esrp": 3},
        ]))

        result = engine.compute_indicator("people.received.esrp")

        self.assertEqual(result.value, 5)

    def test_people_received_same_key_same_value_counts_once(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "espo", "q53_accompagnes__espo": 4},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "espo", "q53_accompagnes__espo": 4},
        ]))

        result = engine.compute_indicator("people.received.espo")

        self.assertEqual(result.value, 4)

    def test_people_received_same_key_different_values_raise_consistency_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "ueros", "q53_accompagnes__ueros": 4},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "ueros", "q53_accompagnes__ueros": 5},
        ]))

        with self.assertRaises(DataConsistencyError) as raised:
            engine.compute_indicator("people.received.ueros")

        self.assertEqual(
            str(raised.exception),
            "Contradictory annual people received values for business key 2025/010000001/ueros and field q53_accompagnes__ueros: 4 vs 5",
        )

    def test_people_received_same_finess_two_dispositifs_stay_separate(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q53_accompagnes__esrp": 3},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "espo", "q53_accompagnes__espo": 6},
        ]))

        self.assertEqual(engine.compute_indicator("people.received.esrp").value, 3)
        self.assertEqual(engine.compute_indicator("people.received.espo").value, 6)

    def test_people_received_same_finess_two_campaigns_are_counted_separately(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2024, "finess_main": "010000001", "dispositif": "deac", "q53_accompagnes__deac": 1},
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "deac", "q53_accompagnes__deac": 2},
        ]))

        result = engine.compute_indicator("people.received.deac")

        self.assertEqual(result.value, 3)

    def test_people_received_uses_only_its_canonical_q53_field(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "q53_accompagnes__esrp": 4,
                "prestations_json": {"cond-1": {"indirect": {"rows": {"epe": {"origine": -1, "limitrophes": 0}}}}},
            },
        ]))

        result = engine.compute_indicator("people.received.esrp")

        self.assertEqual(result.value, 4)

    def test_people_received_inconsistent_other_dispositif_field_raises_data_quality_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "finess_main": "010000001",
                "dispositif": "esrp",
                "q53_accompagnes__esrp": 4,
                "q53_accompagnes__espo": 2,
            },
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("people.received.esrp")

        self.assertEqual(
            str(raised.exception),
            "Inconsistent annual people received values: logical dispositif esrp cannot carry a positive value in q53_accompagnes__espo",
        )

    def test_people_received_result_source_mentions_exact_flat_field(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q53_accompagnes__esrp": 4},
        ]))

        result = engine.compute_indicator("people.received.esrp")

        self.assertEqual(result.source, {
            "dataset": "questionnaires",
            "repository": "fake",
            "field": "q53_accompagnes__esrp",
            "fallback_field": "q53_accompagnes__esrp",
            "business_key": "campaign_year+finess_main+dispositif",
            "source_type": "prestations_json_with_flat_fallback",
            "prestations_paths": "prestations_json.<conditional_id>.fileActive",
            "conditional_defs_path": "prestations_details_json.__wizard_v3_state.runtime.conditionalDefs",
        })

    def test_people_received_indicators_remain_distinct(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "dispositif": "esrp", "q53_accompagnes__esrp": 1},
            {"campaign_year": 2025, "finess_main": "010000002", "dispositif": "espo", "q53_accompagnes__espo": 2},
            {"campaign_year": 2025, "finess_main": "010000003", "dispositif": "ueros", "q53_accompagnes__ueros": 3},
            {"campaign_year": 2025, "finess_main": "010000004", "dispositif": "deac", "q53_accompagnes__deac": 4},
        ]))

        self.assertEqual(engine.compute_indicator("people.received.esrp").value, 1)
        self.assertEqual(engine.compute_indicator("people.received.espo").value, 2)
        self.assertEqual(engine.compute_indicator("people.received.ueros").value, 3)
        self.assertEqual(engine.compute_indicator("people.received.deac").value, 4)

    def test_projection_esrp_only_produces_one_esrp_line(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "check_esrp": True},
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual(len(projected), 1)
        self.assertEqual(projected[0].dispositif, "esrp")

    def test_projection_esrp_and_espo_produce_two_lines(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "check_espo": True},
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual([row.dispositif for row in projected], ["esrp", "espo"])

    def test_projection_keeps_same_uuid_on_both_lines(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "check_espo": True},
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual([row.uuid for row in projected], ["uuid-1", "uuid-1"])

    def test_projection_keeps_only_canonical_q53_field_per_line(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-1",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "check_espo": True,
                "q53_accompagnes__esrp": 20,
                "q53_accompagnes__espo": 8,
            },
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual(projected[0].q53_accompagnes__esrp, 20)
        self.assertEqual(projected[0].q53_accompagnes__espo, 0)
        self.assertEqual(projected[1].q53_accompagnes__esrp, 0)
        self.assertEqual(projected[1].q53_accompagnes__espo, 8)

    def test_projection_inactive_zero_q53_produces_no_line(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__espo": 0},
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual([row.dispositif for row in projected], ["esrp"])

    def test_projection_inactive_positive_q53_raises_data_quality_error(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__espo": 2},
        ])

        with self.assertRaises(DataQualityError) as raised:
            project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual(
            str(raised.exception),
            "Inconsistent annual people received values: logical dispositif esrp cannot carry a positive value in q53_accompagnes__espo",
        )

    def test_projection_no_active_dispositif_and_no_dispositif_data_produces_zero_lines(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "q38_dui": "Oui"},
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual(projected, ())

    def test_projection_no_active_dispositif_with_positive_q53_raises_error(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "q53_accompagnes__esrp": 2},
        ])

        with self.assertRaises(DataQualityError) as raised:
            project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual(
            str(raised.exception),
            "Questionnaire uuid-1 has no active dispositif but q53_accompagnes__esrp is positive",
        )

    def test_projection_copies_dui_information_on_two_active_lines(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "check_espo": True, "q38_dui": "Oui"},
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual([row.q38_dui for row in projected], ["Oui", "Oui"])

    def test_projection_copies_remuneration_information_on_two_active_lines(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-1",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "check_espo": True,
                "q40_remuneration": "Oui",
                "q40_operateur": "Docaposte",
            },
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual([row.q40_operateur for row in projected], ["Docaposte", "Docaposte"])

    def test_projection_multi_dispositif_questionnaire_counts_in_existing_q53_indicators(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-1",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "check_espo": True,
                "q53_accompagnes__esrp": 20,
                "q53_accompagnes__espo": 8,
            },
        ]))

        self.assertEqual(engine.compute_indicator("people.received.esrp").value, 20)
        self.assertEqual(engine.compute_indicator("people.received.espo").value, 8)

    def test_projection_same_questionnaire_contributes_once_to_esrp_and_once_to_espo(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-1",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "check_espo": True,
                "q53_accompagnes__esrp": 20,
                "q53_accompagnes__espo": 8,
            },
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual(sum(1 for row in projected if row.dispositif == "esrp"), 1)
        self.assertEqual(sum(1 for row in projected if row.dispositif == "espo"), 1)

    def test_projection_does_not_create_unselected_deac_or_ueros_lines(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "check_esrp": True},
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual([row.dispositif for row in projected], ["esrp"])

    def test_projection_normalizes_valid_flag_forms(self):
        repository = FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-1",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": " oui ",
                "check_espo": "0",
                "check_ueros": 0,
                "check_deac": False,
            },
        ])

        projected = project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual([row.dispositif for row in projected], ["esrp"])

    def test_projection_unknown_flag_form_raises_explicit_error(self):
        repository = FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-1", "campaign_year": 2025, "finess_main": "010000001", "check_esrp": "peut-etre"},
        ])

        with self.assertRaises(DataQualityError) as raised:
            project_questionnaire(repository.list_raw_questionnaires()[0])

        self.assertEqual(
            str(raised.exception),
            "Invalid activation flag for check_esrp: peut-etre",
        )

    def test_multi_dispositif_questionnaire_does_not_duplicate_mdph_participations(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-1",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "check_espo": True,
                "prestations_json": {
                    "cond-1": {"indirect": {"rows": {"epe": {"origine": 2, "limitrophes": 3}}}},
                },
            },
        ]))

        result = engine.compute_indicator("institution.mdph.epe.count")

        self.assertEqual(result.value, 5)

    def test_projection_pec_with_orp_block_uses_file_active_volume(self):
        repository = FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                conditional_defs=[("cond-pec-avec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH")],
                prestations_json={"cond-pec-avec": {"fileActive": 7}},
            ),
        ])

        projected = project_evaluation_activities(
            repository.list_raw_questionnaires()[0],
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )

        self.assertEqual(len(projected), 1)
        self.assertEqual(projected[0].evaluation_type, "pec")
        self.assertEqual(projected[0].orientation_cdaph, "avec_orp_cdaph")
        self.assertEqual(projected[0].declared_volume, 7)
        self.assertEqual(projected[0].source_path, "fileActive")

    def test_people_received_pec_adds_with_and_without_orp_variants(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={
                    "cond-pec-avec": {"fileActive": 4},
                    "cond-pec-sans": {"fileActive": "6"},
                },
                conditional_defs=[
                    ("cond-pec-avec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                    ("cond-pec-sans", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Sans ORP CDAPH"),
                ],
            ),
        ]))

        result = engine.compute_indicator("people.received.pec")

        self.assertEqual(result.value, 10)

    def test_projection_other_eval_hors_orp_uses_beneficiaires_volume(self):
        repository = FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                conditional_defs=[("cond-eval", "Directes hors ORP CDAPH - Évaluations professionnelles")],
                prestations_json={
                    "cond-eval": {
                        "directSansOrp": {"rows": {"pec": {"beneficiaires": 9}}},
                    },
                },
            ),
        ])

        projected = project_evaluation_activities(
            repository.list_raw_questionnaires()[0],
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )

        self.assertEqual(len(projected), 1)
        self.assertEqual(projected[0].evaluation_type, "other_eval")
        self.assertEqual(projected[0].orientation_cdaph, "sans_orp_cdaph")
        self.assertEqual(projected[0].declared_volume, 9)
        self.assertEqual(projected[0].source_path, "directSansOrp.rows.pec.beneficiaires")

    def test_people_received_other_eval_adds_with_and_without_orp_variants(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={
                    "cond-autre-avec": {"fileActive": 3},
                    "cond-eval-sans": {
                        "directSansOrp": {"rows": {"pec": {"beneficiaires": 5}}},
                    },
                },
                conditional_defs=[
                    ("cond-autre-avec", "Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH"),
                    ("cond-eval-sans", "Directes hors ORP CDAPH - Évaluations professionnelles"),
                ],
            ),
        ]))

        result = engine.compute_indicator("people.received.other_eval")

        self.assertEqual(result.value, 8)

    def test_pec_and_other_eval_can_coexist_in_same_questionnaire(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={
                    "cond-pec": {"fileActive": 4},
                    "cond-other": {"fileActive": 6},
                },
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                    ("cond-other", "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH"),
                ],
            ),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.pec").value, 4)
        self.assertEqual(engine.compute_indicator("people.received.other_eval").value, 6)

    def test_no_deduplication_is_performed_between_pec_and_other_eval(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={
                    "cond-pec": {"fileActive": 5},
                    "cond-other": {"fileActive": 5},
                },
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                    ("cond-other", "Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH"),
                ],
            ),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.pec").value, 5)
        self.assertEqual(engine.compute_indicator("people.received.other_eval").value, 5)

    def test_absent_evaluation_block_returns_zero(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(prestations_json={}, conditional_defs=[]),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.pec").value, 0)
        self.assertEqual(engine.compute_indicator("people.received.other_eval").value, 0)

    def test_present_evaluation_block_with_empty_volume_returns_zero(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": ""}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.pec").value, 0)

    def test_evaluation_numeric_string_is_accepted(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": " 12 "}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Sans ORP CDAPH"),
                ],
            ),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.pec").value, 12)

    def test_evaluation_negative_value_raises_data_quality_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": -1}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("people.received.pec")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH.fileActive: negative values are not accepted",
        )

    def test_evaluation_boolean_value_raises_data_quality_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": True}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("people.received.pec")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH.fileActive: booleans are not accepted",
        )

    def test_evaluation_text_value_raises_data_quality_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": "abc"}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Sans ORP CDAPH"),
                ],
            ),
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("people.received.pec")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Sans ORP CDAPH.fileActive: abc",
        )

    def test_same_evaluation_key_same_value_counts_once(self):
        row = _make_evaluation_row(
            prestations_json={"cond-pec": {"fileActive": 4}},
            conditional_defs=[
                ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
            ],
        )
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[row, row]))

        result = engine.compute_indicator("people.received.pec")

        self.assertEqual(result.value, 4)

    def test_same_evaluation_key_different_value_raises_consistency_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": 4}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": 5}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
        ]))

        with self.assertRaises(DataConsistencyError) as raised:
            engine.compute_indicator("people.received.pec")

        self.assertEqual(
            str(raised.exception),
            "Contradictory evaluation activity values for business key 2025/010000001/pec/avec_orp_cdaph/cond-pec: 4 vs 5",
        )

    def test_two_distinct_evaluation_blocks_same_category_both_contribute(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={
                    "cond-pec-1": {"fileActive": 4},
                    "cond-pec-2": {"fileActive": 6},
                },
                conditional_defs=[
                    ("cond-pec-1", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                    ("cond-pec-2", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Sans ORP CDAPH"),
                ],
            ),
        ]))

        result = engine.compute_indicator("people.received.pec")

        self.assertEqual(result.value, 10)

    def test_projection_keeps_orientation_and_source_block_id(self):
        repository = FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-other": {"fileActive": 2}},
                conditional_defs=[
                    ("cond-other", "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH"),
                ],
            ),
        ])

        projected = project_evaluation_activities(
            repository.list_raw_questionnaires()[0],
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )

        self.assertEqual(projected[0].orientation_cdaph, "sans_orp_cdaph")
        self.assertEqual(projected[0].source_block_id, "cond-other")

    def test_evaluation_result_source_exposes_paths_and_grain(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": 1}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
        ]))

        result = engine.compute_indicator("people.received.pec")

        self.assertEqual(result.source, {
            "dataset": "questionnaires",
            "repository": "fake",
            "field": "prestations_json",
            "block_categories": "pec",
            "orientation_variants": "avec_orp_cdaph,sans_orp_cdaph",
            "grain": "campaign_year+finess_main+evaluation_type+orientation_cdaph+source_block_id",
            "business_key": "campaign_year+finess_main+evaluation_type+orientation_cdaph+source_block_id",
            "source_type": "prestations_json",
            "paths": (
                "prestations_json.<conditional_id>.fileActive;"
                "prestations_json.<conditional_id>.directSansOrp.rows.pec.beneficiaires"
            ),
        })

    def test_mdph_indicators_still_use_questionnaire_grain_when_evaluation_blocks_exist(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={
                    "cond-mdph": {"indirect": {"rows": {"epe": {"origine": 2, "limitrophes": 1}}}},
                    "cond-pec": {"fileActive": 4},
                },
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
                check_esrp=True,
                check_espo=True,
            ),
        ]))

        self.assertEqual(engine.compute_indicator("institution.mdph.epe.count").value, 3)

    def test_existing_q53_indicators_still_use_dispositif_grain_when_evaluation_blocks_exist(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": 4}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
                check_esrp=True,
                q53_accompagnes__esrp=11,
            ),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.esrp").value, 11)

    def test_people_received_esrp_prefers_json_over_flat_field(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                check_esrp=True,
                q53_accompagnes__esrp=4,
                prestations_json={"cond-esrp": {"fileActive": 11}},
                conditional_defs=[("cond-esrp", "Directes ORP CDAPH - ESRP")],
            ),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.esrp").value, 11)

    def test_people_received_esrp_uses_flat_fallback_when_json_block_is_absent(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 7},
        ]))

        self.assertEqual(engine.compute_indicator("people.received.esrp").value, 7)

    def test_people_received_json_zero_does_not_fallback_to_flat_value(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                check_esrp=True,
                q53_accompagnes__esrp=9,
                prestations_json={"cond-esrp": {"fileActive": 0}},
                conditional_defs=[("cond-esrp", "Directes ORP CDAPH - ESRP")],
            ),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.esrp").value, 0)

    def test_people_received_other_eval_exposes_additive_breakdown(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={
                    "cond-prof": {"directSansOrp": {"rows": {"pec": {"beneficiaires": 5}}}},
                    "cond-sans": {"fileActive": 3},
                    "cond-avec": {"fileActive": 2},
                },
                conditional_defs=[
                    ("cond-prof", "Directes hors ORP CDAPH - Évaluations professionnelles"),
                    ("cond-sans", "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH"),
                    ("cond-avec", "Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH"),
                ],
            ),
        ]))

        result = engine.compute_indicator("people.received.other_eval")

        self.assertEqual(result.value, 10)
        self.assertEqual(result.breakdown, {
            "professional_assessment": 5,
            "without_orp_cdaph": 3,
            "with_orp_cdaph": 2,
        })

    def test_people_received_other_eval_detail_indicators_are_individually_available(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={
                    "cond-prof": {"directSansOrp": {"rows": {"pec": {"beneficiaires": 5}}}},
                    "cond-sans": {"fileActive": 3},
                    "cond-avec": {"fileActive": 2},
                },
                conditional_defs=[
                    ("cond-prof", "Directes hors ORP CDAPH - Évaluations professionnelles"),
                    ("cond-sans", "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH"),
                    ("cond-avec", "Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH"),
                ],
            ),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.other_eval.professional_assessment").value, 5)
        self.assertEqual(engine.compute_indicator("people.received.other_eval.without_orp_cdaph").value, 3)
        self.assertEqual(engine.compute_indicator("people.received.other_eval.with_orp_cdaph").value, 2)

    def test_people_received_all_adds_the_five_expected_components(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-a",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "q53_accompagnes__esrp": 10,
            },
            {
                "uuid": "uuid-b",
                "campaign_year": 2025,
                "finess_main": "010000002",
                "check_espo": True,
                "q53_accompagnes__espo": 5,
            },
            {
                "uuid": "uuid-c",
                "campaign_year": 2025,
                "finess_main": "010000003",
                "check_ueros": True,
                "q53_accompagnes__ueros": 2,
            },
            _make_evaluation_row(
                uuid="uuid-d",
                finess_main="010000004",
                prestations_json={"cond-pec": {"fileActive": 3}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
            _make_evaluation_row(
                uuid="uuid-e",
                finess_main="010000005",
                prestations_json={"cond-other": {"fileActive": 4}},
                conditional_defs=[
                    ("cond-other", "Directes ORP CDAPH - Autre dispositif d'évaluation - Sans ORP CDAPH"),
                ],
            ),
        ]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(result.value, 24)

    def test_people_received_all_excludes_deac(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-a",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "q53_accompagnes__esrp": 10,
            },
            {
                "uuid": "uuid-b",
                "campaign_year": 2025,
                "finess_main": "010000002",
                "check_deac": True,
                "q53_accompagnes__deac": 99,
            },
        ]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(result.value, 10)

    def test_people_received_all_does_not_deduplicate_between_categories(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-a",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "q53_accompagnes__esrp": 5,
            },
            _make_evaluation_row(
                uuid="uuid-b",
                finess_main="010000001",
                prestations_json={"cond-pec": {"fileActive": 5}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
        ]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(result.value, 10)

    def test_people_received_all_missing_components_contribute_zero(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-a",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "q53_accompagnes__esrp": 7,
            },
        ]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(result.value, 7)
        self.assertEqual(result.breakdown, {
            "esrp": 7,
            "espo": 0,
            "ueros": 0,
            "pec": 0,
            "other_eval": 0,
        })

    def test_people_received_all_includes_pec_and_other_eval_together(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={
                    "cond-pec": {"fileActive": 3},
                    "cond-other": {"fileActive": 4},
                },
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                    ("cond-other", "Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH"),
                ],
            ),
        ]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(result.value, 7)

    def test_people_received_all_breakdown_contains_five_components(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(set(result.breakdown.keys()), {"esrp", "espo", "ueros", "pec", "other_eval"})

    def test_people_received_all_breakdown_sum_matches_total(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-a",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "q53_accompagnes__esrp": 8,
            },
            _make_evaluation_row(
                uuid="uuid-b",
                finess_main="010000002",
                prestations_json={"cond-other": {"fileActive": 6}},
                conditional_defs=[
                    ("cond-other", "Directes ORP CDAPH - Autre dispositif d'évaluation - Avec ORP CDAPH"),
                ],
            ),
        ]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(sum(result.breakdown.values()), result.value)

    def test_people_received_all_provenance_mentions_two_grains(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(
            result.source["grains"],
            "campaign_year+finess_main+dispositif;campaign_year+finess_main+evaluation_type+orientation_cdaph+source_block_id",
        )

    def test_people_received_all_provenance_mentions_deac_exclusion(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(result.source["deac"], "excluded from total")

    def test_people_received_all_quality_error_from_esrp_is_propagated(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-a",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "q53_accompagnes__esrp": -1,
            },
        ]))

        with self.assertRaises(DataQualityError) as raised:
            engine.compute_indicator("people.received.all")

        self.assertEqual(
            str(raised.exception),
            "Invalid numeric value for q53_accompagnes__esrp: negative values are not accepted",
        )

    def test_people_received_all_consistency_error_from_pec_is_propagated(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": 4}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
            _make_evaluation_row(
                prestations_json={"cond-pec": {"fileActive": 5}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
        ]))

        with self.assertRaises(DataConsistencyError) as raised:
            engine.compute_indicator("people.received.all")

        self.assertEqual(
            str(raised.exception),
            "Contradictory evaluation activity values for business key 2025/010000001/pec/avec_orp_cdaph/cond-pec: 4 vs 5",
        )

    def test_people_received_all_components_remain_calculable_separately(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-a",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "q53_accompagnes__esrp": 2,
            },
            _make_evaluation_row(
                uuid="uuid-b",
                finess_main="010000002",
                prestations_json={"cond-pec": {"fileActive": 3}},
                conditional_defs=[
                    ("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"),
                ],
            ),
        ]))

        self.assertEqual(engine.compute_indicator("people.received.esrp").value, 2)
        self.assertEqual(engine.compute_indicator("people.received.pec").value, 3)
        self.assertEqual(engine.compute_indicator("people.received.all").value, 5)

    def test_people_received_all_does_not_include_mdph_or_other_nested_metrics(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "uuid": "uuid-a",
                "campaign_year": 2025,
                "finess_main": "010000001",
                "check_esrp": True,
                "q53_accompagnes__esrp": 1,
                "prestations_json": {
                    "cond-mdph": {
                        "indirect": {"rows": {"epe": {"origine": 9, "limitrophes": 9}}},
                    },
                },
            },
        ]))

        result = engine.compute_indicator("people.received.all")

        self.assertEqual(result.value, 1)

    def test_filter_campaign_year_selects_only_requested_campaign(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2024, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 2},
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 7},
        ]))

        result = engine.compute_indicator("people.received.esrp", filters={"campaign_year": 2025})

        self.assertEqual(result.value, 7)

    def test_filter_campaign_year_absent_from_dataset_returns_zero_with_warning(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 7},
        ]))

        result = engine.compute_indicator("people.received.esrp", filters={"campaign_year": 2024})

        self.assertEqual(result.value, 0)
        self.assertEqual(result.resolved_filters.warnings, ("campaign_year 2024 absent from dataset; result will be empty",))

    def test_filter_campaign_year_invalid_type_raises_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(FilterValidationError) as raised:
            engine.compute_indicator("people.received.esrp", filters={"campaign_year": "2025"})

        self.assertEqual(
            str(raised.exception),
            "Invalid filter campaign_year='2025': expected positive integer",
        )

    def test_filter_campaign_year_is_unavailable_when_source_has_no_campaign(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": None, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 7},
        ]))

        with self.assertRaises(IncompatibleFilterError) as raised:
            engine.compute_indicator("people.received.esrp", filters={"campaign_year": 2025})

        self.assertEqual(
            str(raised.exception),
            "Le filtre de campagne n’est pas disponible pour cette source de données.",
        )

    def test_indicator_still_computes_when_source_has_no_campaign_and_no_campaign_filter(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": None, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 7},
        ]))

        result = engine.compute_indicator("people.received.esrp")

        self.assertEqual(result.value, 7)

    def test_filter_region_selects_only_requested_region(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "region_code": "11", "department_code": "75", "finess_main": "010000002", "check_esrp": True, "q53_accompagnes__esrp": 9},
        ]))

        result = engine.compute_indicator("people.received.esrp", filters={"region_code": " 84 "})

        self.assertEqual(result.value, 4)

    def test_filter_department_selects_only_requested_department(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "region_code": "84", "department_code": "38", "finess_main": "010000002", "check_esrp": True, "q53_accompagnes__esrp": 9},
        ]))

        result = engine.compute_indicator("people.received.esrp", filters={"department_code": "69"})

        self.assertEqual(result.value, 4)

    def test_filter_region_and_department_incompatibility_raises_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ]))

        with self.assertRaises(FilterValidationError) as raised:
            engine.compute_indicator("people.received.esrp", filters={"region_code": "11", "department_code": "69"})

        self.assertEqual(
            str(raised.exception),
            "Invalid filter department_code='69' for indicator people.received.esrp: incompatible with region_code='11'",
        )

    def test_filter_finess_preserves_leading_zeroes(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "finess_main": "910000001", "check_esrp": True, "q53_accompagnes__esrp": 9},
        ]))

        result = engine.compute_indicator("people.received.esrp", filters={"finess_main": " 010000001 "})

        self.assertEqual(result.value, 4)

    def test_filter_finess_accepts_eight_digit_input_and_applies_canonical_value(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "12345678", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "finess_main": "912345678", "check_esrp": True, "q53_accompagnes__esrp": 9},
        ]))

        result = engine.compute_indicator("people.received.esrp", filters={"finess_main": "12345678"})

        self.assertEqual(result.value, 4)
        self.assertEqual(result.resolved_filters.applied["finess_main"], ("012345678",))

    def test_canonical_finess_grouping_uses_normalized_repository_value(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "12345678", "check_esrp": True, "q53_accompagnes__esrp": 6},
            {"campaign_year": 2025, "finess_main": "012345678", "check_esrp": True, "q53_accompagnes__esrp": 6},
        ]))

        result = engine.compute_indicator("people.received.esrp", filters={"finess_main": "012345678"})

        self.assertEqual(result.value, 6)

    def test_filter_finess_invalid_value_raises_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(FilterValidationError) as raised:
            engine.compute_indicator("people.received.esrp", filters={"finess_main": "A100"})

        self.assertEqual(
            str(raised.exception),
            "Invalid filter finess_main='A100': expected 8 or 9 digits",
        )

    def test_filter_dispositif_esrp_selects_only_esrp_rows(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "finess_main": "010000002", "check_espo": True, "q53_accompagnes__espo": 9},
        ]))

        result = engine.compute_indicator("profile.dui.yes.count", filters={"dispositifs": "esrp"})

        self.assertEqual(result.value, 0)

    def test_filter_multiple_dispositifs_are_accepted(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"uuid": "uuid-a", "campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"uuid": "uuid-b", "campaign_year": 2025, "finess_main": "010000002", "check_espo": True, "q53_accompagnes__espo": 9},
        ]))

        result = engine.compute_indicator("questionnaires.count", filters={"campaign_year": 2025})
        filtered = engine.compute_indicator("people.received.esrp", filters={"dispositifs": ["ESRP", " ESPO "]})

        self.assertEqual(result.value, 2)
        self.assertEqual(filtered.value, 4)

    def test_filter_unknown_dispositif_raises_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(FilterValidationError) as raised:
            engine.compute_indicator("people.received.esrp", filters={"dispositifs": "pec"})

        self.assertEqual(
            str(raised.exception),
            "Invalid filter dispositifs='pec': expected one of esrp, espo, ueros, deac",
        )

    def test_filter_dispositif_is_incompatible_with_mdph_indicator(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(IncompatibleFilterError) as raised:
            engine.compute_indicator("institution.mdph.epe.count", filters={"dispositifs": "esrp"})

        self.assertEqual(
            str(raised.exception),
            "Incompatible filter dispositifs='esrp' for indicator institution.mdph.epe.count",
        )

    def test_filter_dispositif_is_incompatible_with_pec_indicator(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(IncompatibleFilterError) as raised:
            engine.compute_indicator("people.received.pec", filters={"dispositifs": "esrp"})

        self.assertEqual(
            str(raised.exception),
            "Incompatible filter dispositifs='esrp' for indicator people.received.pec",
        )

    def test_no_filters_preserve_existing_result(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 7},
        ]))

        result = engine.compute_indicator("people.received.esrp")

        self.assertEqual(result.value, 7)
        self.assertEqual(result.resolved_filters.requested, {})
        self.assertEqual(result.resolved_filters.applied, {})

    def test_filters_are_applied_before_aggregation(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2024, "region_code": "84", "department_code": "69", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 2},
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 3},
        ]))

        result = engine.compute_indicator("people.received.esrp", filters={"campaign_year": 2025})

        self.assertEqual(result.value, 3)

    def test_filters_are_applied_before_deduplication(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2024, "finess_main": "010000001", "check_esrp": True, "q38_dui": "Oui"},
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q38_dui": "Oui"},
        ]))

        result = engine.compute_indicator("profile.dui.yes.count", filters={"campaign_year": 2025})

        self.assertEqual(result.value, 1)

    def test_contradiction_outside_filtered_scope_does_not_block(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2024, "finess_main": "010000001", "check_esrp": True, "q38_dui": "Oui"},
            {"campaign_year": 2024, "finess_main": "010000001", "check_esrp": True, "q38_dui": "Non"},
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q38_dui": "Oui"},
        ]))

        result = engine.compute_indicator("profile.dui.yes.count", filters={"campaign_year": 2025})

        self.assertEqual(result.value, 1)

    def test_contradiction_inside_filtered_scope_still_blocks(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q38_dui": "Oui"},
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q38_dui": "Non"},
        ]))

        with self.assertRaises(DataConsistencyError):
            engine.compute_indicator("profile.dui.yes.count", filters={"campaign_year": 2025})

    def test_projections_preserve_region_and_department(self):
        repository = FakeQuestionnaireRepository(rows=[
            _make_evaluation_row(
                region_code="84",
                department_code="69",
                prestations_json={"cond-pec": {"fileActive": 3}},
                conditional_defs=[("cond-pec", "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH")],
                check_esrp=True,
                q53_accompagnes__esrp=2,
            ),
        ])

        raw_record = repository.list_raw_questionnaires()[0]
        projected_questionnaire = project_questionnaire(raw_record)[0]
        projected_evaluation = project_evaluation_activities(
            raw_record,
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )[0]

        self.assertEqual(projected_questionnaire.region_code, "84")
        self.assertEqual(projected_questionnaire.department_code, "69")
        self.assertEqual(projected_evaluation.region_code, "84")
        self.assertEqual(projected_evaluation.department_code, "69")

    def test_requested_and_applied_filters_are_present_in_result(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 7},
        ]))

        result = engine.compute_indicator("people.received.esrp", filters={"campaign_year": 2025, "region_code": "84"})

        self.assertEqual(result.resolved_filters.requested, {"campaign_year": 2025, "region_code": "84"})
        self.assertEqual(result.resolved_filters.applied, {"campaign_year": 2025, "region_code": "84"})

    def test_invalid_filter_is_never_ignored_silently(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(FilterValidationError):
            engine.compute_indicator("people.received.esrp", filters={"unknown_filter": "x"})

    def test_catalog_declares_filter_compatibility(self):
        self.assertEqual(
            get_indicator_definition("people.received.pec").compatible_filters,
            ("campaign_year", "region_code", "department_code", "finess_main", "completion_scope"),
        )

    def test_people_received_all_rejects_dispositif_filter_as_ambiguous(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(IncompatibleFilterError) as raised:
            engine.compute_indicator("people.received.all", filters={"dispositifs": "esrp"})

        self.assertEqual(
            str(raised.exception),
            "Incompatible filter dispositifs='esrp' for indicator people.received.all",
        )

    def test_admin_global_sees_all_data(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "84", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "region_code": "11", "finess_main": "010000002", "check_esrp": True, "q53_accompagnes__esrp": 6},
        ]))

        result = engine.compute_indicator("people.received.esrp", user_context=UserContext("u1", "admin_global"))

        self.assertEqual(result.value, 10)
        self.assertEqual(result.user_role, "admin_global")

    def test_national_readonly_sees_all_data(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "84", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "region_code": "11", "finess_main": "010000002", "check_esrp": True, "q53_accompagnes__esrp": 6},
        ]))

        result = engine.compute_indicator("people.received.esrp", user_context=UserContext("u2", "national_readonly"))

        self.assertEqual(result.value, 10)
        self.assertEqual(result.user_role, "national_readonly")

    def test_national_readonly_cannot_export(self):
        with self.assertRaises(PermissionDeniedError) as raised:
            ensure_export_allowed(get_scope(UserContext("u2", "national_readonly")))

        self.assertEqual(
            str(raised.exception),
            "Permission denied for role='national_readonly': export is not allowed",
        )

    def test_regional_user_without_filter_gets_automatic_region_scope(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "44", "department_code": "44", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000002", "check_esrp": True, "q53_accompagnes__esrp": 6},
        ]))

        result = engine.compute_indicator(
            "people.received.esrp",
            user_context=UserContext("u3", "regional_user", region_codes=("44",)),
        )

        self.assertEqual(result.value, 4)
        self.assertEqual(result.resolved_filters.scope_constraints["region_code"], ("44",))

    def test_regional_user_can_request_own_region(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "44", "department_code": "44", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ]))

        result = engine.compute_indicator(
            "people.received.esrp",
            filters={"region_code": "44"},
            user_context=UserContext("u3", "regional_user", region_codes=("44",)),
        )

        self.assertEqual(result.value, 4)

    def test_regional_user_cannot_request_other_region(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(PermissionDeniedError) as raised:
            engine.compute_indicator(
                "people.received.esrp",
                filters={"region_code": "84"},
                user_context=UserContext("u3", "regional_user", region_codes=("44",)),
            )

        self.assertEqual(
            str(raised.exception),
            "Permission denied for filter region_code on indicator people.received.esrp: value outside user scope",
        )

    def test_regional_user_does_not_see_finess_outside_region(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "44", "department_code": "44", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000002", "check_esrp": True, "q53_accompagnes__esrp": 6},
        ]))

        result = engine.compute_indicator(
            "people.received.esrp",
            user_context=UserContext("u3", "regional_user", region_codes=("44",)),
        )

        self.assertEqual(result.value, 4)

    def test_establishment_user_sees_only_own_finess(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
            {"campaign_year": 2025, "finess_main": "010000002", "check_esrp": True, "q53_accompagnes__esrp": 6},
        ]))

        result = engine.compute_indicator(
            "people.received.esrp",
            user_context=UserContext("u4", "establishment_user", finess_values=("010000001",)),
        )

        self.assertEqual(result.value, 4)

    def test_establishment_user_requesting_other_finess_gets_error(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(PermissionDeniedError) as raised:
            engine.compute_indicator(
                "people.received.esrp",
                filters={"finess_main": "010000002"},
                user_context=UserContext("u4", "establishment_user", finess_values=("010000001",)),
            )

        self.assertEqual(
            str(raised.exception),
            "Permission denied for filter finess_main on indicator people.received.esrp: value outside user scope",
        )

    def test_mixed_authorized_and_unauthorized_finess_request_is_fully_refused(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(PermissionDeniedError):
            engine.compute_indicator(
                "people.received.esrp",
                filters={"finess_main": ["010000001", "010000002"]},
                user_context=UserContext("u4", "establishment_user", finess_values=("010000001",)),
            )

    def test_scope_limited_to_esrp_allows_esrp_indicator(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "44", "department_code": "44", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ]))

        result = engine.compute_indicator(
            "people.received.esrp",
            user_context=UserContext("u5", "regional_user", region_codes=("44",), allowed_dispositifs=("esrp",)),
        )

        self.assertEqual(result.value, 4)

    def test_scope_limited_to_esrp_refuses_espo_indicator(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(PermissionDeniedError) as raised:
            engine.compute_indicator(
                "people.received.espo",
                user_context=UserContext("u5", "regional_user", region_codes=("44",), allowed_dispositifs=("esrp",)),
            )

        self.assertEqual(
            str(raised.exception),
            "Permission denied for role='regional_user': indicator people.received.espo is outside allowed dispositifs",
        )

    def test_scope_dispositif_restriction_does_not_silently_alter_mdph(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "region_code": "44",
                "department_code": "44",
                "finess_main": "010000001",
                "prestations_json": {"cond-1": {"indirect": {"rows": {"epe": {"origine": 2, "limitrophes": 1}}}}},
            },
        ]))

        result = engine.compute_indicator(
            "institution.mdph.epe.count",
            user_context=UserContext("u5", "regional_user", region_codes=("44",), allowed_dispositifs=("esrp",)),
        )

        self.assertEqual(result.value, 3)

    def test_transverse_indicator_remains_territorially_filtered(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {
                "campaign_year": 2025,
                "region_code": "44",
                "department_code": "44",
                "finess_main": "010000001",
                "prestations_json": {"cond-pec": {"fileActive": 3}},
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [{"id": "cond-pec", "name": "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"}]}}},
            },
            {
                "campaign_year": 2025,
                "region_code": "84",
                "department_code": "69",
                "finess_main": "010000002",
                "prestations_json": {"cond-pec": {"fileActive": 5}},
                "prestations_details_json": {"__wizard_v3_state": {"runtime": {"conditionalDefs": [{"id": "cond-pec", "name": "Directes ORP CDAPH - Prestation d'Evaluations et de Conseils - Avec ORP CDAPH"}]}}},
            },
        ]))

        result = engine.compute_indicator(
            "people.received.pec",
            user_context=UserContext("u5", "regional_user", region_codes=("44",), allowed_dispositifs=("esrp",)),
        )

        self.assertEqual(result.value, 3)

    def test_people_received_all_refused_if_scope_dispositif_is_incomplete(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[]))

        with self.assertRaises(PermissionDeniedError) as raised:
            engine.compute_indicator(
                "people.received.all",
                user_context=UserContext("u5", "regional_user", region_codes=("44",), allowed_dispositifs=("esrp",)),
            )

        self.assertEqual(
            str(raised.exception),
            "Permission denied for role='regional_user': indicator people.received.all requires esrp, espo and ueros access",
        )

    def test_people_received_all_allowed_if_scope_covers_esrp_espo_ueros(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "44", "department_code": "44", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 2},
        ]))

        result = engine.compute_indicator(
            "people.received.all",
            user_context=UserContext("u5", "regional_user", region_codes=("44",), allowed_dispositifs=("esrp", "espo", "ueros")),
        )

        self.assertEqual(result.value, 2)

    def test_unknown_role_produces_invalid_user_context_error(self):
        with self.assertRaises(InvalidUserContextError) as raised:
            get_scope(UserContext("u6", "unknown_role"))

        self.assertEqual(
            str(raised.exception),
            "Invalid user context role='unknown_role': unknown role",
        )

    def test_regional_context_without_region_produces_error(self):
        with self.assertRaises(InvalidUserContextError) as raised:
            get_scope(UserContext("u6", "regional_user"))

        self.assertEqual(
            str(raised.exception),
            "Invalid user context role='regional_user': region_codes is required",
        )

    def test_establishment_context_without_finess_produces_error(self):
        with self.assertRaises(InvalidUserContextError) as raised:
            get_scope(UserContext("u6", "establishment_user"))

        self.assertEqual(
            str(raised.exception),
            "Invalid user context role='establishment_user': finess_values is required",
        )

    def test_filter_outside_scope_produces_permission_denied(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 1},
        ]))

        with self.assertRaises(PermissionDeniedError):
            engine.compute_indicator(
                "people.received.esrp",
                filters={"department_code": "69"},
                user_context=UserContext("u3", "regional_user", region_codes=("44",)),
            )

    def test_scope_restriction_appears_in_result(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "44", "department_code": "44", "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ]))

        result = engine.compute_indicator(
            "people.received.esrp",
            user_context=UserContext("u3", "regional_user", region_codes=("44",)),
        )

        self.assertEqual(result.permission_scope.role, "regional_user")
        self.assertEqual(result.resolved_filters.scope_constraints["region_code"], ("44",))

    def test_contradiction_outside_scope_does_not_block(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000001", "check_esrp": True, "q38_dui": "Oui"},
            {"campaign_year": 2025, "region_code": "84", "department_code": "69", "finess_main": "010000001", "check_esrp": True, "q38_dui": "Non"},
            {"campaign_year": 2025, "region_code": "44", "department_code": "44", "finess_main": "010000002", "check_esrp": True, "q38_dui": "Oui"},
        ]))

        result = engine.compute_indicator(
            "profile.dui.yes.count",
            user_context=UserContext("u3", "regional_user", region_codes=("44",)),
        )

        self.assertEqual(result.value, 1)

    def test_contradiction_inside_scope_still_blocks(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "region_code": "44", "department_code": "44", "finess_main": "010000001", "check_esrp": True, "q38_dui": "Oui"},
            {"campaign_year": 2025, "region_code": "44", "department_code": "44", "finess_main": "010000001", "check_esrp": True, "q38_dui": "Non"},
        ]))

        with self.assertRaises(DataConsistencyError):
            engine.compute_indicator(
                "profile.dui.yes.count",
                user_context=UserContext("u3", "regional_user", region_codes=("44",)),
            )

    def test_export_allowed_for_admin_global(self):
        ensure_export_allowed(get_scope(UserContext("u1", "admin_global")))

    def test_export_refused_for_establishment_user(self):
        with self.assertRaises(PermissionDeniedError):
            ensure_export_allowed(get_scope(UserContext("u4", "establishment_user", finess_values=("010000001",))))

    def test_historical_calls_without_user_context_still_pass(self):
        engine = AnalyticsEngine(FakeQuestionnaireRepository(rows=[
            {"campaign_year": 2025, "finess_main": "010000001", "check_esrp": True, "q53_accompagnes__esrp": 4},
        ]))

        result = engine.compute_indicator("people.received.esrp")

        self.assertEqual(result.value, 4)
        self.assertEqual(result.user_role, "admin_global")

def _make_evaluation_row(
    *,
    uuid="uuid-1",
    campaign_year=2025,
    region_code=None,
    department_code=None,
    finess_main="010000001",
    prestations_json,
    conditional_defs,
    check_esrp=False,
    check_espo=False,
    check_ueros=False,
    check_deac=False,
    q53_accompagnes__esrp=0,
):
    return {
        "uuid": uuid,
        "campaign_year": campaign_year,
        "region_code": region_code,
        "department_code": department_code,
        "finess_main": finess_main,
        "check_esrp": check_esrp,
        "check_espo": check_espo,
        "check_ueros": check_ueros,
        "check_deac": check_deac,
        "q53_accompagnes__esrp": q53_accompagnes__esrp,
        "prestations_json": prestations_json,
        "prestations_details_json": {
            "__wizard_v3_state": {
                "runtime": {
                    "conditionalDefs": [
                        {"id": block_id, "name": block_name}
                        for block_id, block_name in conditional_defs
                    ],
                },
            },
        },
    }


def _normalize_test_integer(value, field_name):
    if value is None or value == "":
        return 0
    if isinstance(value, bool):
        raise DataQualityError(f"Invalid numeric value for {field_name}: booleans are not accepted")
    if isinstance(value, int):
        if value < 0:
            raise DataQualityError(f"Invalid numeric value for {field_name}: negative values are not accepted")
        return value
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return 0
        if not normalized.lstrip("-").isdigit():
            raise DataQualityError(f"Invalid numeric value for {field_name}: {value}")
        integer_value = int(normalized)
        if integer_value < 0:
            raise DataQualityError(f"Invalid numeric value for {field_name}: negative values are not accepted")
        return integer_value
    return int(value)


if __name__ == "__main__":
    unittest.main()
