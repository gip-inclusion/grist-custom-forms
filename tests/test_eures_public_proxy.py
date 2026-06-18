import unittest
from unittest.mock import Mock, patch

import app


class EuresPublicProxyTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()

    @patch.object(app.requests, 'request')
    def test_public_domain_proxies_eures_form_root(self, requests_request):
        requests_request.return_value = Mock(
            status_code=200,
            content=b'proxied-eures',
            headers={'Content-Type': 'text/html; charset=utf-8'},
        )

        response = self.client.get(
            '/forms/eures-beta/',
            base_url='https://formulaires.inclusion.gouv.fr',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'proxied-eures')
        requests_request.assert_called_once()
        self.assertEqual(
            requests_request.call_args.kwargs['url'],
            'https://eures-beta.osc-fr1.scalingo.io/forms/eures-beta/',
        )

    @patch.object(app.requests, 'request')
    def test_scalingo_domain_serves_local_eures_form_root(self, requests_request):
        response = self.client.get(
            '/forms/eures-beta/',
            base_url='https://eures-beta.osc-fr1.scalingo.io',
        )

        self.assertEqual(response.status_code, 200)
        requests_request.assert_not_called()


if __name__ == '__main__':
    unittest.main()
