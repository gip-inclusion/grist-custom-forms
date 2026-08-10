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
        self.assertIn('J’accepte la mise en relation via WhatsApp', text_body)
        self.assertIn('Je suis intéressé mais sans WhatsApp', text_body)
        self.assertIn('J’accepte WhatsApp', html_body)
        self.assertIn('Intéressé sans WhatsApp', html_body)
        self.assertIn('julie.barthelemy@arhis.lu', recipient)

    @patch.object(app, 'should_proxy_eures_public_request', return_value=False)
    @patch.object(app, 'get_eures_matching_config')
    @patch.object(app, 'fetch_record_by_id')
    @patch.object(app, '_find_eures_employer_fields_for_matching')
    def test_matching_feedback_contact_first_confirms_employer_phone(
        self,
        find_employer_fields,
        fetch_record_by_id,
        get_eures_matching_config,
        _should_proxy,
    ):
        get_eures_matching_config.return_value = {'doc_id': 'doc', 'table_id': 'Matchings'}
        fetch_record_by_id.return_value = {'id': 57, 'fields': {'besoin_id': 'EMP-1'}}
        find_employer_fields.return_value = {
            'employeur': 'ARHIS',
            'contact': 'Julie',
            'poste': 'Nettoyage',
            'telephone': '+352 123456',
        }
        token = app.get_eures_email_action_serializer().dumps({
            'record_id': 57,
            'response': 'contact_whatsapp',
        })

        response = self.client.get(f'/eures-beta/matching-feedback?token={token}')

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn('Confirmer la mise en relation WhatsApp', body)
        self.assertIn('name="employer_phone"', body)
        self.assertIn('+352 123456', body)

    @patch.object(app, 'should_proxy_eures_public_request', return_value=False)
    @patch.object(app, 'get_eures_matching_config')
    @patch.object(app, 'update_matching_record_by_id')
    def test_matching_feedback_contact_post_records_whatsapp_phone(
        self,
        update_matching_record_by_id,
        get_eures_matching_config,
        _should_proxy,
    ):
        get_eures_matching_config.return_value = {'doc_id': 'doc', 'table_id': 'Matchings'}
        token = app.get_eures_email_action_serializer().dumps({
            'record_id': 57,
            'response': 'contact_whatsapp',
        })

        response = self.client.post('/eures-beta/matching-feedback', data={
            'token': token,
            'employer_phone': ' +352 123456 ',
        })

        self.assertEqual(response.status_code, 200)
        update_matching_record_by_id.assert_called_once()
        fields = update_matching_record_by_id.call_args.args[2]
        self.assertEqual(fields['employer_response'], 'contact')
        self.assertEqual(fields['employer_whatsapp_consent'], 'yes')
        self.assertEqual(fields['employer_whatsapp_phone'], '+352 123456')
        self.assertIn('employer_whatsapp_confirmed_at', fields)

    @patch.object(app, 'should_proxy_eures_public_request', return_value=False)
    @patch.object(app, 'get_eures_matching_config')
    @patch.object(app, 'update_matching_record_by_id')
    def test_matching_feedback_contact_without_whatsapp_records_no_whatsapp(
        self,
        update_matching_record_by_id,
        get_eures_matching_config,
        _should_proxy,
    ):
        get_eures_matching_config.return_value = {'doc_id': 'doc', 'table_id': 'Matchings'}
        token = app.get_eures_email_action_serializer().dumps({
            'record_id': 57,
            'response': 'contact_no_whatsapp',
        })

        response = self.client.get(f'/eures-beta/matching-feedback?token={token}')

        self.assertEqual(response.status_code, 200)
        update_matching_record_by_id.assert_called_once()
        fields = update_matching_record_by_id.call_args.args[2]
        self.assertEqual(fields['employer_response'], 'contact')
        self.assertEqual(fields['employer_whatsapp_consent'], 'no')
        self.assertNotIn('employer_whatsapp_phone', fields)

    def test_build_candidate_matching_notification_email_mentions_company_and_spam_check(self):
        row = {
            'record_id': 57,
            'candidat': {
                'nom': 'Romuald Bernard',
                'email': 'romuald08150@gmail.com',
            },
            'employeur': {
                'employeur': 'ARHIS HR SOLUTIONS',
            },
        }

        recipient, subject, text_body, html_body = app.build_brevo_candidate_matching_notification_email(row)

        self.assertEqual(recipient, 'romuald08150@gmail.com')
        self.assertIn('ARHIS HR SOLUTIONS', subject)
        self.assertIn('ARHIS HR SOLUTIONS', text_body)
        self.assertIn('appels masques', text_body)
        self.assertIn('spams', text_body)
        self.assertIn('ARHIS HR SOLUTIONS', html_body)

    def test_build_candidate_invitation_email_uses_simple_french_greeting(self):
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
        self.assertIn('votre profil nous intéresse', subject)
        self.assertTrue(text_body.startswith("Bonjour,\n\n"))
        self.assertIn("Conseiller EURES - France Travail", text_body)
        self.assertNotIn("Questionnaire candidat EURES beta", text_body)
        self.assertNotIn("Repères de vérification", text_body)
        self.assertIn("France Travail", html_body)
        self.assertNotIn("Questionnaire candidat EURES beta", html_body)
        self.assertNotIn("Repères de vérification", html_body)

    def test_build_candidate_invitation_email_for_eures_cv_deposit_campaign(self):
        invitation = {
            'role': 'candidate',
            'email': 'candidate@example.org',
            'language': 'fr',
            'campaign_type': 'eures_cv_deposit',
            'invite_token': 'token-demo',
            'invite_link': 'https://formulaires.inclusion.gouv.fr/forms/eures-beta/questionnaire-candidate?lang=fr&invite_token=token-demo',
        }

        recipient, subject, text_body, html_body, invite_token, invite_link = app.build_brevo_invitation_email(invitation)

        self.assertEqual(recipient, 'candidate@example.org')
        self.assertEqual(invite_token, 'token-demo')
        self.assertIn('Votre CV EURES peut correspondre à des besoins employeurs', subject)
        self.assertIn('Vous venez de déposer ou d’actualiser votre CV sur EURES', text_body)
        self.assertIn('Match Europe', text_body)
        self.assertIn('Compléter mon profil Match Europe', html_body)

    @patch.object(app, 'send_brevo_transactional_email')
    @patch.object(app, 'update_eures_invitation_record_by_id')
    @patch.object(app, 'build_eures_invitation_conflict_indexes', return_value={
        'blocking_statuses': set(),
        'invitation_by_key': {},
        'questionnaire_by_key': {},
    })
    @patch.object(app, 'fetch_table_records')
    @patch.object(app, 'get_eures_invitations_config')
    def test_admin_invitation_send_allows_force_resend_for_sent_rows(
        self,
        get_eures_invitations_config,
        fetch_table_records,
        build_eures_invitation_conflict_indexes,
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

    @patch.object(app, 'send_brevo_transactional_email')
    @patch.object(app, 'list_eures_admin_matchings')
    @patch.object(app, 'ensure_brevo_ready')
    def test_admin_matching_candidate_email_resends_candidate_notification_only(
        self,
        ensure_brevo_ready,
        list_eures_admin_matchings,
        send_brevo_transactional_email,
    ):
        list_eures_admin_matchings.return_value = [{
            'record_id': 32,
            'candidat': {
                'nom': 'Eric Barthelemy',
                'email': 'eric.barthelemy@me.com',
            },
            'employeur': {
                'employeur': 'ARHIS HR SOLUTIONS',
            },
        }]
        send_brevo_transactional_email.return_value = {'messageId': 'brevo-456'}

        with patch.dict(os.environ, {
            'ADMIN_USERNAME': 'admin',
            'ADMIN_PASSWORD': 'AdminEures2026',
            'BREVO_API_KEY': 'brevo-key',
            'BREVO_FROM_EMAIL': 'eures@example.org',
        }, clear=False):
            response = self.client.post(
                '/api/forms/eures-beta/admin/matchings/32/candidate-email',
                headers=self.admin_auth,
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['ok'])
        self.assertTrue(payload['candidate_email_sent'])
        self.assertEqual(payload['record_id'], 32)
        self.assertEqual(payload['candidate_email'], 'eric.barthelemy@me.com')
        ensure_brevo_ready.assert_called_once_with(check_api=True)
        send_brevo_transactional_email.assert_called_once()

    @patch.object(app, 'send_brevo_transactional_email')
    @patch.object(app, 'ensure_brevo_ready')
    def test_admin_matching_test_emails_send_only_to_fixed_test_recipients(
        self,
        ensure_brevo_ready,
        send_brevo_transactional_email,
    ):
        send_brevo_transactional_email.side_effect = [
            {'messageId': 'brevo-employer-test'},
            {'messageId': 'brevo-candidate-test'},
        ]

        with patch.dict(os.environ, {
            'ADMIN_USERNAME': 'admin',
            'ADMIN_PASSWORD': 'AdminEures2026',
            'BREVO_API_KEY': 'brevo-key',
            'BREVO_FROM_EMAIL': 'eures@example.org',
        }, clear=False):
            response = self.client.post(
                '/api/forms/eures-beta/admin/matchings/test-emails',
                headers=self.admin_auth,
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['employer_email'], 'sci.europe@icloud.com')
        self.assertEqual(payload['candidate_email'], 'eric.barthelemy@me.com')
        ensure_brevo_ready.assert_called_once_with(check_api=True)
        self.assertEqual(send_brevo_transactional_email.call_count, 2)
        employer_call = send_brevo_transactional_email.call_args_list[0]
        candidate_call = send_brevo_transactional_email.call_args_list[1]
        self.assertEqual(employer_call.args[0], 'sci.europe@icloud.com')
        self.assertEqual(candidate_call.args[0], 'eric.barthelemy@me.com')
        self.assertTrue(employer_call.args[1].startswith('[TEST] '))
        self.assertTrue(candidate_call.args[1].startswith('[TEST] '))

    @patch.object(app, 'send_brevo_transactional_email')
    @patch.object(app, 'ensure_brevo_ready')
    def test_admin_email_test_sends_selected_template_to_requested_recipient(
        self,
        ensure_brevo_ready,
        send_brevo_transactional_email,
    ):
        send_brevo_transactional_email.return_value = {'messageId': 'brevo-selected-test'}

        with patch.dict(os.environ, {
            'ADMIN_USERNAME': 'admin',
            'ADMIN_PASSWORD': 'AdminEures2026',
            'BREVO_API_KEY': 'brevo-key',
            'BREVO_FROM_EMAIL': 'eures@example.org',
        }, clear=False):
            response = self.client.post(
                '/api/forms/eures-beta/admin/email-tests/send',
                headers=self.admin_auth,
                json={
                    'email_type': 'candidate_invitation_eures_cv',
                    'recipient_email': 'test@example.org',
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['recipient_email'], 'test@example.org')
        self.assertEqual(payload['email_type'], 'candidate_invitation_eures_cv')
        self.assertIn('Votre CV EURES peut correspondre à des besoins employeurs', payload['subject'])
        ensure_brevo_ready.assert_called_once_with(check_api=True)
        send_brevo_transactional_email.assert_called_once()
        self.assertEqual(send_brevo_transactional_email.call_args.args[0], 'test@example.org')
        self.assertTrue(send_brevo_transactional_email.call_args.args[1].startswith('[TEST] '))


if __name__ == '__main__':
    unittest.main()
