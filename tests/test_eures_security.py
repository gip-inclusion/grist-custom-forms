import unittest

import app


class EuresSecurityTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_eures_public_record_lookup_is_disabled(self):
        response = self.client.get('/api/forms/eures-beta/record?uuid=test-uuid')

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {
            'error': 'Public record lookup is disabled for this form.',
        })

    def test_eures_public_finess_lookup_is_disabled(self):
        response = self.client.post('/api/forms/eures-beta/check-finess', json={
            'uuid': 'test-uuid',
            'finess': ['123456789'],
        })

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {
            'error': 'Public FINESS lookup is disabled for this form.',
        })

    def test_eures_public_recovery_is_disabled(self):
        response = self.client.post('/api/forms/eures-beta/recover-by-email', json={
            'email': 'victim@example.org',
        })

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {
            'error': 'Public questionnaire recovery is disabled for this form.',
        })


if __name__ == '__main__':
    unittest.main()
