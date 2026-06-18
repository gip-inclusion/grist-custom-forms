import os
import unittest
from unittest.mock import Mock, patch

import app


class BrevoHealthTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.admin_auth = {
            'Authorization': 'Basic YWRtaW46QWRtaW5FdXJlczIwMjY='
        }

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

    def test_build_candidate_invitation_email_uses_official_trust_markers(self):
        invitation = {
            'role': 'candidate',
            'email': 'candidate@example.org',
            'first_name': 'Marie',
            'language': 'fr',
            'invite_token': 'token-demo',
            'invite_link': 'https://formulaires.inclusion.gouv.fr/forms/eures-beta/questionnaire-candidate?lang=fr&invite_token=token-demo',
        }

        recipient, subject, text_body, html_body, invite_token, invite_link = app.build_brevo_invitation_email(invitation)

        self.assertEqual(recipient, 'candidate@example.org')
        self.assertEqual(invite_token, 'token-demo')
        self.assertEqual(invite_link, invitation['invite_link'])
        self.assertIn('Questionnaire candidat', subject)
        self.assertIn("conseiller EURES", text_body)
        self.assertIn("domaine officiel", text_body)
        self.assertIn("France Travail", html_body)
        self.assertIn("formulaires.inclusion.gouv.fr", html_body)

    @patch.object(app, 'send_brevo_transactional_email')
    @patch.object(app, 'update_eures_invitation_record_by_id')
    @patch.object(app, 'fetch_table_records')
    @patch.object(app, 'get_eures_invitations_config')
    def test_admin_invitation_send_allows_force_resend_for_sent_rows(
        self,
        get_eures_invitations_config,
        fetch_table_records,
        update_eures_invitation_record_by_id,
        send_brevo_transactional_email,
    ):
        get_eures_invitations_config.return_value = {
            'doc_id': 'doc-id',
            'table_id': 'Invitations',
            'api_key': 'grist-key',
        }
        fetch_table_records.return_value = [{
            'id': 159,
            'fields': {
                'role': 'candidate',
                'email': 'candidate@example.org',
                'first_name': 'Marie',
                'language': 'fr',
                'invite_token': 'token-demo',
                'invite_link': 'https://formulaires.inclusion.gouv.fr/forms/eures-beta/questionnaire-candidate?lang=fr&invite_token=token-demo',
                'invitation_status': 'invitation_envoyee',
            },
        }]
        send_brevo_transactional_email.return_value = {'messageId': 'brevo-123'}

        with patch.dict(os.environ, {
            'ADMIN_USERNAME': 'admin',
            'ADMIN_PASSWORD': 'AdminEures2026',
        }, clear=False):
            response = self.client.post(
                '/api/forms/eures-beta/admin/invitations/send',
                json={'record_ids': [159], 'force_resend': True},
                headers=self.admin_auth,
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['ok'])
        self.assertTrue(payload['force_resend'])
        self.assertEqual(len(payload['sent']), 1)
        self.assertEqual(payload['sent'][0]['record_id'], 159)
        self.assertTrue(payload['sent'][0]['force_resend'])
        send_brevo_transactional_email.assert_called_once()
        update_eures_invitation_record_by_id.assert_called_once()


if __name__ == '__main__':
    unittest.main()
