import json
from unittest.mock import patch

from tests.test_main import BaseTest


class DatasetSharedUserResourceTest(BaseTest):
    @patch("botocore.client.BaseClient._make_api_call")
    def test_update_owners(self, mock_api_call):
        """Verifies that a dataset owner is able to update the owner list."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().put(
            f"{self.dataset_route}/1", headers=headers, json={"owners": [3, 4]}
        )
        self.assertEqual(res.status_code, 200)

        headers = self.generate_auth_headers(user_id=4)
        res = self.client().get(f"{self.dataset_route}/1", headers=headers)
        self.assertEqual(res.status_code, 200)
        owners = json.loads(res.data.decode()).get("owners")

        self.assertEqual(len(owners), 2)

    @patch("botocore.client.BaseClient._make_api_call")
    def test_delete_dataset(self, mock_api_call):
        """Verifies that datasets can be deleted."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().delete(f"{self.dataset_route}/1", headers=headers)

        self.assertEqual(202, res.status_code)

    def test_delete_missing_dataset(self):
        """Verifies that an error is thrown when a non-existent dataset is deleted."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().delete(f"{self.dataset_route}/50", headers=headers)

        self.assertEqual(res.status_code, 404)

    def test_delete_unowned_dataset(self):
        """Verifies that an error is thrown when an unowned dataset is deleted."""
        headers = self.generate_auth_headers(user_id=1)

        res = self.client().delete(f"{self.dataset_route}/4", headers=headers)

        self.assertEqual(res.status_code, 401)

    def test_owner_get_dataset(self):
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().get(f"{self.dataset_route}/1", headers=headers)

        self.assertEqual(200, res.status_code)
