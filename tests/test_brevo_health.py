import os
import unittest
from unittest.mock import Mock, patch

import app


class BrevoHealthTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    def test_get_brevo_health_detects_missing_configuration(self):
        with patch.dict(os.environ, {}, clear=False):
            with patch.dict(os.environ, {'BREVO_API_KEY': '', 'BREVO_FROM_EMAIL': ''}, clear=False):
                health = app.get_brevo_health()

        self.assertFalse(health['configured'])
        self.assertEqual(health['status'], 'missing_config')
        self.assertIn('BREVO_API_KEY', health['message'])

    @patch.object(app.requests, 'get')
    def test_get_brevo_health_checks_api_successfully(self, requests_get):
        requests_get.return_value = Mock(status_code=200, ok=True)

        with patch.dict(os.environ, {
            'BREVO_API_KEY': 'brevo-key',
            'BREVO_FROM_EMAIL': 'eures@example.org',
            'BREVO_FROM_NAME': 'EURES beta',
        }, clear=False):
            health = app.get_brevo_health(check_api=True)

        self.assertTrue(health['configured'])
        self.assertTrue(health['api_ok'])
        self.assertEqual(health['status'], 'ok')
        self.assertEqual(health['http_status'], 200)

    @patch.object(app.requests, 'get')
    def test_get_brevo_health_surfaces_api_error(self, requests_get):
        response = Mock(status_code=401, ok=False)
        response.json.return_value = {'message': 'Key not found'}
        requests_get.return_value = response

        with patch.dict(os.environ, {
            'BREVO_API_KEY': 'bad-key',
            'BREVO_FROM_EMAIL': 'eures@example.org',
        }, clear=False):
            health = app.get_brevo_health(check_api=True)

        self.assertTrue(health['configured'])
        self.assertFalse(health['api_ok'])
        self.assertEqual(health['status'], 'api_error')
        self.assertEqual(health['http_status'], 401)
        self.assertEqual(health['message'], 'Key not found')

    @patch.object(app, 'admin_required', lambda f: f)
    @patch.object(app, 'get_brevo_health')
    def test_health_endpoint_returns_503_when_brevo_degraded(self, get_brevo_health):
        get_brevo_health.return_value = {
            'configured': True,
            'api_ok': False,
            'status': 'api_error',
            'message': 'Key not found',
        }

        response = self.client.get('/health?deep=1')

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()['status'], 'degraded')

    def test_build_matching_email_falls_back_to_employer_email_field(self):
        row = {
            'record_id': 57,
            'raisons': ['langues: français'],
            'candidat': {
                'nom': 'Romuald Bernard',
                'email': 'romuald08150@gmail.com',
                'telephone': '',
                'ville': '',
                'pays': 'France',
                'metier': 'Missions polyvalentes',
                'langues': 'français',
                'mobilite': 'Luxembourg',
                'disponibilite': 'Dès que possible',
            },
            'employeur': {
                'employeur': 'ARHIS',
                'contact': '',
                'email': 'julie.barthelemy@arhis.lu',
                'poste': 'Nettoyage et entretien',
                'pays': 'Luxembourg',
                'langues_requises': 'français',
                'date_debut': 'Dans les prochains jours',
            },
        }

        recipient, subject, text_body, html_body = app.build_brevo_matching_email(row)

        self.assertEqual(recipient, 'julie.barthelemy@arhis.lu')
        self.assertIn('Nettoyage et entretien', subject)
        self.assertIn('Je vais le contacter', text_body)
        self.assertIn('julie.barthelemy@arhis.lu', recipient)


if __name__ == '__main__':
    unittest.main()
