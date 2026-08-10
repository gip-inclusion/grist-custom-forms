import unittest

import app


class EuresSalaryMatchingTest(unittest.TestCase):
    def candidate(self, period="Par mois", amount_type="gross", minimum="2500"):
        return {
            "tally_q38_salary_type": period,
            "tally_q38_salary_amount_type": amount_type,
            "tally_q38_salary_min": minimum,
        }

    def employer(self, period="Per month", amount_type="gross", minimum="2600", maximum="3000"):
        return {
            "tally_q40_salary_type": period,
            "tally_q40_salary_amount_type": amount_type,
            "tally_q40_salary_min": minimum,
            "tally_q40_salary_max": maximum,
        }

    def test_salary_is_compared_when_period_and_gross_net_basis_match(self):
        score, reason = app.eures_score_salary(
            "industrie_production",
            self.candidate(),
            self.employer(),
        )

        self.assertEqual(score, 12)
        self.assertIn("attente sous la fourchette", reason)

    def test_salary_requires_manual_review_when_gross_net_basis_differs(self):
        score, reason = app.eures_score_salary(
            "industrie_production",
            self.candidate(amount_type="net"),
            self.employer(amount_type="gross"),
        )

        self.assertEqual(score, 6)
        self.assertIn("brut/net", reason)

    def test_salary_requires_manual_review_when_period_differs(self):
        score, reason = app.eures_score_salary(
            "industrie_production",
            self.candidate(period="Par heure"),
            self.employer(period="Pro Monat"),
        )

        self.assertEqual(score, 6)
        self.assertIn("periodicites", reason)

    def test_salary_requires_manual_review_for_legacy_answer_without_basis(self):
        score, reason = app.eures_score_salary(
            "industrie_production",
            self.candidate(amount_type=""),
            self.employer(),
        )

        self.assertEqual(score, 6)
        self.assertIn("verification manuelle", reason)


if __name__ == "__main__":
    unittest.main()
