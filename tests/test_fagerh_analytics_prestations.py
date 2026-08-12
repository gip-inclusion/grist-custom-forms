import unittest

from fagerh_analytics.domain import RawQuestionnaireRecord
from fagerh_analytics.engine import DataQualityError
from fagerh_analytics.prestations import (
    DEVICE_VOLUME_DEFINITIONS,
    extract_device_volume_candidates,
    project_received_people_records,
    resolve_device_volume,
)


class PrestationsExtractionTest(unittest.TestCase):
    def test_extract_esrp_positive_value_from_json(self):
        record = _make_raw_record(
            prestations_json={"cond-esrp": {"fileActive": 12}},
            conditional_defs=[("cond-esrp", "Directes ORP CDAPH - ESRP")],
        )

        extracted = extract_device_volume_candidates(
            record,
            DEVICE_VOLUME_DEFINITIONS[0],
            normalize_integer=_normalize_test_integer,
        )

        self.assertEqual(len(extracted), 1)
        self.assertEqual(extracted[0].state, "positive")
        self.assertEqual(extracted[0].value, 12)

    def test_extract_esrp_zero_is_explicit(self):
        record = _make_raw_record(
            prestations_json={"cond-esrp": {"fileActive": 0}},
            conditional_defs=[("cond-esrp", "Directes ORP CDAPH - ESRP")],
        )

        extracted = extract_device_volume_candidates(
            record,
            DEVICE_VOLUME_DEFINITIONS[0],
            normalize_integer=_normalize_test_integer,
        )

        self.assertEqual(extracted[0].state, "zero")
        self.assertEqual(extracted[0].value, 0)

    def test_empty_string_is_distinct_from_zero(self):
        record = _make_raw_record(
            prestations_json={"cond-esrp": {"fileActive": "   "}},
            conditional_defs=[("cond-esrp", "Directes ORP CDAPH - ESRP")],
        )

        extracted = extract_device_volume_candidates(
            record,
            DEVICE_VOLUME_DEFINITIONS[0],
            normalize_integer=_normalize_test_integer,
        )

        self.assertEqual(extracted[0].state, "empty_string")
        self.assertIsNone(extracted[0].value)

    def test_flat_fallback_is_used_only_when_json_block_is_absent(self):
        record = _make_raw_record(q53_accompagnes__esrp=7)

        value, metadata = resolve_device_volume(
            record,
            DEVICE_VOLUME_DEFINITIONS[0],
            flat_value=record.q53_accompagnes__esrp,
            flat_field_name="q53_accompagnes__esrp",
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )

        self.assertEqual(value, 7)
        self.assertTrue(metadata["fallback_used"])

    def test_json_zero_prevents_flat_fallback(self):
        record = _make_raw_record(
            prestations_json={"cond-esrp": {"fileActive": 0}},
            conditional_defs=[("cond-esrp", "Directes ORP CDAPH - ESRP")],
            q53_accompagnes__esrp=9,
        )

        value, metadata = resolve_device_volume(
            record,
            DEVICE_VOLUME_DEFINITIONS[0],
            flat_value=record.q53_accompagnes__esrp,
            flat_field_name="q53_accompagnes__esrp",
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )

        self.assertEqual(value, 0)
        self.assertFalse(metadata["fallback_used"])

    def test_numeric_string_is_accepted(self):
        record = _make_raw_record(
            prestations_json={"cond-espo": {"fileActive": " 8 "}},
            conditional_defs=[("cond-espo", "Directes ORP CDAPH - ESPO")],
        )

        value, _ = resolve_device_volume(
            record,
            DEVICE_VOLUME_DEFINITIONS[1],
            flat_value=record.q53_accompagnes__espo,
            flat_field_name="q53_accompagnes__espo",
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )

        self.assertEqual(value, 8)

    def test_esrp_annual_file_active_includes_definitive_exits(self):
        record = _make_raw_record(
            prestations_json={"cond-esrp": {"fileActive": 71, "sorties": 73}},
            conditional_defs=[("cond-esrp", "Directes ORP CDAPH - ESRP")],
        )

        value, metadata = resolve_device_volume(
            record,
            DEVICE_VOLUME_DEFINITIONS[0],
            flat_value=record.q53_accompagnes__esrp,
            flat_field_name="q53_accompagnes__esrp",
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )

        self.assertEqual(value, 144)
        self.assertEqual(metadata["source_path"], "fileActive+sorties")

    def test_espo_annual_file_active_includes_definitive_exits(self):
        record = _make_raw_record(
            prestations_json={"cond-espo": {"fileActive": 29, "sorties": 112}},
            conditional_defs=[("cond-espo", "Directes ORP CDAPH - ESPO")],
        )

        value, _ = resolve_device_volume(
            record,
            DEVICE_VOLUME_DEFINITIONS[1],
            flat_value=record.q53_accompagnes__espo,
            flat_field_name="q53_accompagnes__espo",
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )

        self.assertEqual(value, 141)

    def test_invalid_value_is_rejected(self):
        record = _make_raw_record(
            prestations_json={"cond-ueros": {"fileActive": "abc"}},
            conditional_defs=[("cond-ueros", "Directes ORP CDAPH - UEROS")],
        )

        with self.assertRaises(DataQualityError):
            resolve_device_volume(
                record,
                DEVICE_VOLUME_DEFINITIONS[2],
                flat_value=record.q53_accompagnes__ueros,
                flat_field_name="q53_accompagnes__ueros",
                normalize_integer=_normalize_test_integer,
                quality_error_cls=DataQualityError,
            )

    def test_projection_does_not_duplicate_same_json_block(self):
        record = _make_raw_record(
            check_esrp=True,
            prestations_json={"cond-esrp": {"fileActive": 4}},
            conditional_defs=[("cond-esrp", "Directes ORP CDAPH - ESRP")],
        )

        projected = project_received_people_records(
            record,
            normalize_integer=_normalize_test_integer,
            quality_error_cls=DataQualityError,
        )

        self.assertEqual(len(projected), 1)
        self.assertEqual(projected[0].dispositif, "esrp")
        self.assertEqual(projected[0].q53_accompagnes__esrp, 4)


def _make_raw_record(
    *,
    check_esrp=False,
    prestations_json=None,
    conditional_defs=None,
    q53_accompagnes__esrp=0,
    q53_accompagnes__espo=0,
    q53_accompagnes__ueros=0,
):
    return RawQuestionnaireRecord(
        uuid="uuid-1",
        campaign_year=2025,
        finess_main="010000001",
        check_esrp=check_esrp,
        prestations_json=prestations_json or {},
        prestations_details_json={
            "__wizard_v3_state": {
                "runtime": {
                    "conditionalDefs": [
                        {"id": block_id, "name": block_name}
                        for block_id, block_name in (conditional_defs or [])
                    ],
                },
            },
        },
        q53_accompagnes__esrp=q53_accompagnes__esrp,
        q53_accompagnes__espo=q53_accompagnes__espo,
        q53_accompagnes__ueros=q53_accompagnes__ueros,
        raw={
            "prestations_json": prestations_json or {},
            "prestations_details_json": {
                "__wizard_v3_state": {
                    "runtime": {
                        "conditionalDefs": [
                            {"id": block_id, "name": block_name}
                            for block_id, block_name in (conditional_defs or [])
                        ],
                    },
                },
            },
        },
    )


def _normalize_test_integer(value, field_name):
    if value is None:
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
        if not normalized.isdigit():
            raise DataQualityError(f"Invalid numeric value for {field_name}: {value}")
        return int(normalized)
    raise DataQualityError(f"Invalid numeric value for {field_name}: unsupported type")


if __name__ == "__main__":
    unittest.main()
