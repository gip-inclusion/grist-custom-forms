import unittest

from fagerh_analytics.finess import diagnose_finess, normalize_finess


class FagerhAnalyticsFinessTest(unittest.TestCase):
    def test_eight_digit_finess_gets_leading_zero(self):
        self.assertEqual(normalize_finess("50002450"), "050002450")

    def test_nine_digit_finess_is_preserved(self):
        self.assertEqual(normalize_finess("970209573"), "970209573")

    def test_empty_finess_stays_none(self):
        self.assertIsNone(normalize_finess(""))

    def test_non_digit_finess_is_invalid(self):
        diagnostic = diagnose_finess("12A45678")
        self.assertEqual(diagnostic.issue_code, "invalid_finess")

    def test_seven_digit_finess_is_invalid(self):
        diagnostic = diagnose_finess("1234567")
        self.assertEqual(diagnostic.issue_code, "invalid_finess")

    def test_ten_digit_finess_is_invalid(self):
        diagnostic = diagnose_finess("1234567890")
        self.assertEqual(diagnostic.issue_code, "invalid_finess")


if __name__ == "__main__":
    unittest.main()
