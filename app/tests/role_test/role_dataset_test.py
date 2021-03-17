import json

from tests.test_main import BaseTest


class RoleDatasetResourceTest(BaseTest):
    def test_get_role_datasets(self):
        """Role owner should be able to retrieve datasets assigned to a given role."""
        headers = self.generate_auth_headers(user_id=4)

        res = self.client().get(f"{self.role_route}/1/dataset", headers=headers)

        self.assertEqual(res.status_code, 200)
        datasets = json.loads(res.data.decode())

        self.assertEqual(len(datasets), 1)
        self.assertEqual(datasets[0].get("dataset_name"), "Call Center Transcripts")

    def test_get_role_datasets_unowned_role(self):
        """User of an unowned role should not be able to see dataset details."""
        headers = self.generate_auth_headers(user_id=2)

        res = self.client().get(f"{self.role_route}/1/dataset", headers=headers)

        self.assertEqual(res.status_code, 401)

    def test_add_new_role_dataset(self):
        """Tests that a role owner can add an individual dataset to a role."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().post(
            f"{self.role_route}/1/dataset", headers=headers, json={"datasets": [2]}
        )

        self.assertEqual(res.status_code, 201)

        res = self.client().get(f"{self.role_route}/1/dataset", headers=headers)
        datasets = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(datasets), 2)

    def test_add_multiple_datasets(self):
        """Verify that owners can add multiple datasets at once to a role."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().post(
            f"{self.role_route}/1/dataset", headers=headers, json={"datasets": [2, 3]}
        )

        self.assertEqual(res.status_code, 201)

        res = self.client().get(f"{self.role_route}/1/dataset", headers=headers)
        permissions = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(permissions), 3)

    def test_add_same_dataset(self):
        """Owners should not be able to add the same dataset to a role."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().post(
            f"{self.role_route}/1/dataset", headers=headers, json={"datasets": [1, 2]}
        )

        self.assertEqual(res.status_code, 400)

    def test_add_unowned_dataset(self):
        """Users should not be able to add a dataset they do not own to a role."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().post(
            f"{self.role_route}/1/dataset", headers=headers, json={"datasets": [4]}
        )

        self.assertEqual(res.status_code, 401)

    def test_update_role_datasets(self):
        """Owners should be able to overwrite role datasets."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().put(
            f"{self.role_route}/1/dataset", json={"datasets": [1, 2]}, headers=headers
        )

        self.assertEqual(res.status_code, 200)
        datasets = json.loads(res.data.decode()).get("datasets")

        self.assertEqual(len(datasets), 2)

    def test_remove_role_dataset(self):
        """Owners should be able to remove role datasets."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().delete(
            f"{self.role_route}/1/dataset", json={"datasets": [1]}, headers=headers
        )

        self.assertEqual(res.status_code, 200)
        permissions = json.loads(res.data.decode()).get("datasets")

        self.assertEqual(len(permissions), 0)

    def test_remove_missing_dataset(self):
        """Validate that owner cannot remove a dataset that is not in the role."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().delete(
            f"{self.role_route}/1/dataset", json={"datasets": [1, 2]}, headers=headers
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("not present", res.data.decode())
