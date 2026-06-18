import os
import unittest
from unittest.mock import patch

import app


class AdminMagicLinkTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.env = {
            'ADMIN_AUTH_MODE_EURES_BETA': 'magic_link',
            'ADMIN_ALLOWED_EMAILS_EURES_BETA': 'admin@example.org',
            'SESSION_SECRET': 'session-secret',
            'BREVO_API_KEY': 'brevo-key',
            'BREVO_FROM_EMAIL': 'eures@example.org',
        }

    def test_magic_link_mode_redirects_admin_page_to_login(self):
        with patch.dict(os.environ, self.env, clear=False):
            response = self.client.get('/admin/eures-beta/')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/admin/eures-beta/login'))

    def test_magic_link_mode_returns_401_on_admin_api_without_session(self):
        with patch.dict(os.environ, self.env, clear=False):
            response = self.client.get('/api/forms/eures-beta/admin/matchings')

        self.assertEqual(response.status_code, 401)
        payload = response.get_json()
        self.assertEqual(payload['error'], 'Authentication required')
        self.assertEqual(payload['login_url'], '/admin/eures-beta/login')

    @patch.object(app, 'send_brevo_transactional_email')
    def test_magic_link_login_sends_email_to_allowed_address(self, send_brevo_transactional_email):
        send_brevo_transactional_email.return_value = {'messageId': 'brevo-789'}

        with patch.dict(os.environ, self.env, clear=False):
            response = self.client.post('/admin/eures-beta/login', data={'email': 'admin@example.org'})

        self.assertEqual(response.status_code, 200)
        self.assertIn("lien de connexion", response.get_data(as_text=True).lower())
        send_brevo_transactional_email.assert_called_once()

    @patch.object(app, 'send_brevo_transactional_email')
    def test_magic_link_login_does_not_send_for_email_outside_allowlist(self, send_brevo_transactional_email):
        with patch.dict(os.environ, self.env, clear=False):
            response = self.client.post('/admin/eures-beta/login', data={'email': 'outsider@example.org'})

        self.assertEqual(response.status_code, 200)
        send_brevo_transactional_email.assert_not_called()

    def test_magic_link_consume_opens_session(self):
        with patch.dict(os.environ, self.env, clear=False):
            token = app.get_admin_magic_link_serializer('eures-beta').dumps({
                'form_id': 'eures-beta',
                'email': 'admin@example.org',
            })
            response = self.client.get(f'/admin/eures-beta/magic-login?token={token}')

            self.assertEqual(response.status_code, 302)
            self.assertIn('/admin/eures-beta', response.headers['Location'])

            admin_response = self.client.get('/admin/eures-beta/')
            self.assertEqual(admin_response.status_code, 200)
            admin_response.close()


if __name__ == '__main__':
    unittest.main()
