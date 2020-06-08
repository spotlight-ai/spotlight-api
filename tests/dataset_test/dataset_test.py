import json
from unittest.mock import patch

from tests.test_main import BaseTest


class DatasetSharedUserResourceTest(BaseTest):
    @patch('botocore.client.BaseClient._make_api_call')
    def test_update_owners(self, mock_api_call):
        """Verifies that a dataset owner is able to update the owner list."""
        headers = self.generate_auth_headers(user_id=3)
        
        res = self.client().put(f'{self.dataset_route}/1', headers=headers, json={'owners': [3, 4]})
        self.assertEqual(res.status_code, 200)
        
        headers = self.generate_auth_headers(user_id=4)
        res = self.client().get(f'{self.dataset_route}/1', headers=headers)
        self.assertEqual(res.status_code, 200)
        owners = json.loads(res.data.decode()).get('owners')
        
        self.assertEqual(len(owners), 2)
