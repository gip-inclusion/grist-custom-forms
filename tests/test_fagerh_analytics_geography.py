import unittest

from fagerh_analytics.geography import normalize_department_code, resolve_region_code


class FagerhAnalyticsGeographyTest(unittest.TestCase):
    def test_metropolitan_departments_are_mapped(self):
        self.assertEqual(resolve_region_code("69"), "84")
        self.assertEqual(resolve_region_code("75"), "11")

    def test_corsica_departments_are_mapped(self):
        self.assertEqual(resolve_region_code("2A"), "94")
        self.assertEqual(resolve_region_code("2B"), "94")

    def test_overseas_departments_are_mapped(self):
        self.assertEqual(resolve_region_code("971"), "01")
        self.assertEqual(resolve_region_code("976"), "06")

    def test_numeric_department_values_keep_leading_zeroes(self):
        self.assertEqual(normalize_department_code(1), "01")
        self.assertEqual(resolve_region_code(1), "84")

    def test_unknown_department_returns_none(self):
        self.assertIsNone(resolve_region_code("999"))

    def test_empty_department_returns_none(self):
        self.assertIsNone(resolve_region_code(""))
        self.assertIsNone(resolve_region_code(None))


if __name__ == "__main__":
    unittest.main()
