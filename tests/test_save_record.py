import unittest
from unittest.mock import Mock, patch

import app


class SaveRecordTest(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        self.fields = {
            'uuid': 'fagerh-test-uuid',
            'validateur_email': 'test@example.org',
        }
        self.config_patch = patch.object(app, 'get_form_config', return_value={
            'doc_id': 'doc-id',
            'table_id': 'Reponses',
            'api_key': 'api-key',
        })
        self.columns_patch = patch.object(app, 'get_table_columns', return_value=set(self.fields))
        self.duplicates_patch = patch.object(app, 'find_duplicate_finess', return_value=set())
        self.config_patch.start()
        self.columns_patch.start()
        self.duplicates_patch.start()
        self.addCleanup(self.config_patch.stop)
        self.addCleanup(self.columns_patch.stop)
        self.addCleanup(self.duplicates_patch.stop)

    @patch.object(app.requests, 'post')
    @patch.object(app, 'fetch_record_by_uuid')
    def test_save_returns_compact_success_after_uuid_verification(self, fetch_record_by_uuid, post):
        post.return_value = Mock(status_code=200)
        lookup_response = Mock(status_code=200)
        fetch_record_by_uuid.side_effect = [
            (None, lookup_response),
            ({'id': 42, 'fields': {'uuid': self.fields['uuid']}}, lookup_response),
        ]

        response = self.client.post('/api/forms/fagerh/record', json={'fields': self.fields})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            'ok': True,
            'action': 'created',
            'uuid': self.fields['uuid'],
            'record_id': 42,
        })

    @patch.object(app.requests, 'post')
    @patch.object(app, 'fetch_record_by_uuid')
    def test_save_fails_when_grist_success_cannot_be_verified(self, fetch_record_by_uuid, post):
        post.return_value = Mock(status_code=200)
        lookup_response = Mock(status_code=200)
        fetch_record_by_uuid.side_effect = [
            (None, lookup_response),
            (None, lookup_response),
        ]

        response = self.client.post('/api/forms/fagerh/record', json={'fields': self.fields})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.get_json(), {
            'error': 'Grist write returned success, but the questionnaire was not found after saving.',
        })


if __name__ == '__main__':
    unittest.main()
