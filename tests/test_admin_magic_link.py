import os
import unittest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

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
                'jti': 'token-1',
            })
            response = self.client.get(f'/admin/eures-beta/magic-login?token={token}')

            self.assertEqual(response.status_code, 302)
            self.assertIn('/admin/eures-beta', response.headers['Location'])

            admin_response = self.client.get('/admin/eures-beta/')
            self.assertEqual(admin_response.status_code, 200)
            admin_response.close()

    def test_magic_link_session_cookie_is_not_persistent_by_default(self):
        with patch.dict(os.environ, self.env, clear=False):
            token = app.get_admin_magic_link_serializer('eures-beta').dumps({
                'form_id': 'eures-beta',
                'email': 'admin@example.org',
                'jti': 'token-session-cookie',
            })
            response = self.client.get(f'/admin/eures-beta/magic-login?token={token}')

        self.assertEqual(response.status_code, 302)
        set_cookie = response.headers.get('Set-Cookie', '')
        self.assertNotIn('Expires=', set_cookie)
        self.assertNotIn('Max-Age=', set_cookie)

    def test_magic_link_session_expires_server_side(self):
        with patch.dict(os.environ, self.env | {'ADMIN_SESSION_TTL_SECONDS_EURES_BETA': '300'}, clear=False):
            with self.client.session_transaction() as sess:
                sess['admin_session:eures-beta'] = {
                    'email': 'admin@example.org',
                    'authenticated_at': (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                }

            response = self.client.get('/admin/eures-beta/')

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers['Location'].endswith('/admin/eures-beta/login'))

    def test_magic_link_cannot_be_reused(self):
        with patch.dict(os.environ, self.env, clear=False):
            token = app.get_admin_magic_link_serializer('eures-beta').dumps({
                'form_id': 'eures-beta',
                'email': 'admin@example.org',
                'jti': 'token-replay',
            })
            first = self.client.get(f'/admin/eures-beta/magic-login?token={token}')
            self.assertEqual(first.status_code, 302)

            second = self.client.get(f'/admin/eures-beta/magic-login?token={token}')
            self.assertEqual(second.status_code, 400)
            self.assertIn('Lien deja utilise.', second.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
