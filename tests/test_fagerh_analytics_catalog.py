import unittest

from fagerh_analytics.api import list_available_indicators, serialize_indicator_result
from fagerh_analytics.catalog import INDICATORS, validate_indicator_catalog
from fagerh_analytics.domain import IndicatorResult, PermissionScope, ResolvedFilters, UserContext
from fagerh_analytics.repositories.base import QuestionnaireRepository
from fagerh_analytics.schema import validate_schema_columns


class FagerhAnalyticsCatalogTest(unittest.TestCase):
    def test_all_indicator_ids_are_unique(self):
        self.assertEqual(len(INDICATORS), len(set(INDICATORS)))

    def test_all_labels_are_non_empty(self):
        for indicator_id, definition in INDICATORS.items():
            self.assertTrue(definition.label.strip(), indicator_id)

    def test_all_definitions_are_non_empty(self):
        for indicator_id, definition in INDICATORS.items():
            self.assertTrue(definition.definition.strip(), indicator_id)

    def test_all_grains_are_recognized(self):
        validate_indicator_catalog(INDICATORS)

    def test_all_referenced_capabilities_exist(self):
        validate_indicator_catalog(INDICATORS)

    def test_all_compatible_filters_exist(self):
        validate_indicator_catalog(INDICATORS)

    def test_all_component_indicators_exist(self):
        validate_indicator_catalog(INDICATORS)

    def test_circular_dependency_is_rejected(self):
        broken = dict(INDICATORS)
        broken["loop.a"] = broken["people.received.esrp"].__class__(
            **{**broken["people.received.esrp"].__dict__, "id": "loop.a", "component_indicators": ("loop.b",), "source_fields": (), "required_capabilities": (), "grain": "composite"}
        )
        broken["loop.b"] = broken["people.received.esrp"].__class__(
            **{**broken["people.received.esrp"].__dict__, "id": "loop.b", "component_indicators": ("loop.a",), "source_fields": (), "required_capabilities": (), "grain": "composite"}
        )
        with self.assertRaises(ValueError):
            validate_indicator_catalog(broken)

    def test_people_received_all_has_exact_expected_components(self):
        definition = INDICATORS["people.received.all"]
        self.assertEqual(definition.component_indicators, (
            "people.received.esrp",
            "people.received.espo",
            "people.received.ueros",
            "people.received.pec",
            "people.received.other_eval",
        ))

    def test_people_received_all_excludes_deac(self):
        self.assertNotIn("people.received.deac", INDICATORS["people.received.all"].component_indicators)

    def test_non_composite_indicator_declares_sources(self):
        definition = INDICATORS["people.received.esrp"]
        self.assertTrue(definition.source_fields or definition.source_paths)

    def test_composite_indicator_declares_components(self):
        self.assertTrue(INDICATORS["people.received.all"].component_indicators)

    def test_other_eval_declares_exact_child_components(self):
        self.assertEqual(INDICATORS["people.received.other_eval"].component_indicators, (
            "people.received.other_eval.professional_assessment",
            "people.received.other_eval.without_orp_cdaph",
            "people.received.other_eval.with_orp_cdaph",
        ))

    def test_dui_indicators_are_internal(self):
        self.assertEqual(INDICATORS["profile.dui.yes.count"].visibility, "internal")
        self.assertEqual(INDICATORS["profile.dui.no.count"].visibility, "internal")

    def test_remuneration_indicators_are_internal(self):
        self.assertEqual(INDICATORS["profile.remuneration.asp.count"].visibility, "internal")
        self.assertEqual(INDICATORS["profile.remuneration.docaposte.count"].visibility, "internal")

    def test_people_received_warn_about_non_unique_people(self):
        self.assertTrue(any("non uniques" in warning or "ne sont pas uniques" in warning for warning in INDICATORS["people.received.pec"].business_warnings))

    def test_mdph_warns_about_multiple_participations(self):
        self.assertTrue(any("participations multiples" in warning for warning in INDICATORS["institution.mdph.epe.count"].business_warnings))

    def test_device_indicators_document_their_business_key(self):
        self.assertIn("campagne + FINESS + dispositif", INDICATORS["people.received.esrp"].double_counting_policy or "campagne + FINESS + dispositif")

    def test_list_available_indicators_exposes_grain_capabilities_visibility_and_warnings(self):
        indicators = list_available_indicators(UserContext("u1", "admin_global"), NoReadRepository())
        item = next(item for item in indicators if item["indicator_id"] == "people.received.pec")
        self.assertEqual(item["grain"], "evaluation_activity")
        self.assertIn("evaluation_activities", item["required_capabilities"])
        self.assertEqual(item["visibility"], "observatory")
        self.assertIsInstance(item["business_warnings"], list)

    def test_list_available_indicators_stays_json_compatible(self):
        indicators = list_available_indicators(UserContext("u1", "admin_global"), NoReadRepository())
        for item in indicators:
            self.assertIsInstance(item["required_capabilities"], list)
            self.assertIsInstance(item["component_indicators"], list)
            self.assertIsInstance(item["source_fields"], list)
            self.assertIsInstance(item["source_paths"], list)
            self.assertIsInstance(item["business_warnings"], list)

    def test_availability_continues_to_reflect_schema_capabilities(self):
        repository = SchemaRepository(validate_schema_columns({
            "uuid", "finess_main", "es_departement", "check_esrp", "check_espo", "check_ueros", "check_deac",
            "q53_accompagnes__esrp", "q53_accompagnes__espo", "q53_accompagnes__ueros",
        }))
        indicators = list_available_indicators(UserContext("u1", "admin_global"), repository)
        pec = next(item for item in indicators if item["indicator_id"] == "people.received.pec")
        esrp = next(item for item in indicators if item["indicator_id"] == "people.received.esrp")
        self.assertFalse(pec["available"])
        self.assertTrue(esrp["available"])

    def test_missing_capability_only_disables_concerned_indicators(self):
        repository = SchemaRepository(validate_schema_columns({
            "uuid", "finess_main", "es_departement", "check_esrp", "check_espo", "check_ueros", "check_deac",
            "q40_remuneration", "q40_operateur", "q53_accompagnes__esrp", "q53_accompagnes__espo", "q53_accompagnes__ueros",
        }))
        indicators = list_available_indicators(UserContext("u1", "admin_global"), repository)
        dui = next(item for item in indicators if item["indicator_id"] == "profile.dui.yes.count")
        remuneration = next(item for item in indicators if item["indicator_id"] == "profile.remuneration.asp.count")
        self.assertFalse(dui["available"])
        self.assertTrue(remuneration["available"])

    def test_people_received_all_unavailable_if_component_unavailable(self):
        repository = SchemaRepository(validate_schema_columns({
            "uuid", "finess_main", "es_departement", "check_esrp", "check_espo", "check_ueros", "check_deac",
            "q53_accompagnes__esrp", "q53_accompagnes__espo", "q53_accompagnes__ueros",
        }))
        indicators = list_available_indicators(UserContext("u1", "admin_global"), repository)
        total = next(item for item in indicators if item["indicator_id"] == "people.received.all")
        self.assertFalse(total["available"])

    def test_serialize_indicator_result_exposes_catalog_metadata(self):
        result = IndicatorResult(
            indicator_id="people.received.esrp",
            label="X",
            value=1,
            unit="count",
            privacy_status="visible",
            confidence_level="high",
            source={},
            resolved_filters=ResolvedFilters(),
            permission_scope=PermissionScope(True, (), (), (), (), True, "admin_global"),
        )
        serialized = serialize_indicator_result(result)
        self.assertEqual(serialized["metadata"]["grain"], "establishment_service_device")
        self.assertIn("annual_volumes_esrp", serialized["metadata"]["required_capabilities"])


class NoReadRepository(QuestionnaireRepository):
    def list_raw_questionnaires(self):
        raise AssertionError("should not calculate")


class SchemaRepository(QuestionnaireRepository):
    def __init__(self, schema_result):
        self._schema_result = schema_result

    def list_raw_questionnaires(self):
        raise AssertionError("should not calculate")

    def validate_schema(self):
        return self._schema_result


if __name__ == "__main__":
    unittest.main()
