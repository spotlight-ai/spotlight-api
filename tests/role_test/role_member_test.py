import json
from unittest.mock import patch

from tests.test_main import BaseTest


class RoleMemberResourceTest(BaseTest):
    def test_get_role_members(self):
        """Retrieves all members for a given role."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().get(f"{self.role_route}/1/member", headers=headers)

        members = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(members), 3)

    def test_get_role_members_missing_role(self):
        """Verifies that an error is thrown when requested role does not exist."""
        headers = self.generate_auth_headers()

        res = self.client().get(f"{self.role_route}/10/member", headers=headers)

        self.assertEqual(res.status_code, 401)
        self.assertIn(
            "Role either does not exist or user does not have permissions.",
            res.data.decode(),
        )

    def test_add_owner_to_unowned_role(self):
        """Verifies that an error is thrown if a user tries to add an owner to a role they don't own."""
        headers = self.generate_auth_headers()

        res = self.client().post(
            f"{self.role_route}/2/member",
            json={"owners": [2], "users": [3]},
            headers=headers,
        )

        self.assertEqual(res.status_code, 401)
        self.assertIn(
            "Role either does not exist or user does not have permissions.",
            res.data.decode(),
        )

    def test_add_owner(self):
        """Adds an owner to a role."""
        headers = self.generate_auth_headers(user_id=4)

        res = self.client().post(
            f"{self.role_route}/1/member",
            json={"owners": [2], "users": []},
            headers=headers,
        )

        self.assertEqual(res.status_code, 201)

        res = self.client().get(f"{self.role_route}/1/member", headers=headers)
        members = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(members), 4)

    @patch("resources.roles.role_member.send_notifications")
    def test_add_members(self, mock_notif):
        """Adds multiple members to a role."""
        headers = self.generate_auth_headers(user_id=4)

        res = self.client().post(
            f"{self.role_route}/1/member",
            json={"owners": [], "users": [5, 6]},
            headers=headers,
        )

        self.assertEqual(res.status_code, 201)

        res = self.client().get(f"{self.role_route}/1/member", headers=headers)
        members = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(members), 5)

        owner_count = 0

        for member in members:
            if member.get("is_owner"):
                owner_count += 1

        self.assertEqual(owner_count, 2)

    @patch("resources.roles.role_member.send_notifications")
    def test_add_combo(self, mock_notif):
        """Adds a combination of users and owners."""
        headers = self.generate_auth_headers(user_id=4)

        res = self.client().get(f"{self.role_route}/1/member", headers=headers)
        members = json.loads(res.data.decode())
        res = self.client().post(
            f"{self.role_route}/1/member",
            json={"owners": [5], "users": [2]},
            headers=headers,
        )

        self.assertEqual(res.status_code, 201)

        res = self.client().get(f"{self.role_route}/1/member", headers=headers)
        members = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(members), 5)

        owner_count = 0

        for member in members:
            if member.get("is_owner"):
                owner_count += 1

        self.assertEqual(owner_count, 3)

    @patch("resources.roles.role_member.send_notifications")
    def test_replace_combo(self, mock_notif):
        """Replaces role members and owners with new sets."""
        headers = self.generate_auth_headers(user_id=3)
        member_path = f"{self.role_route}/1/member"

        res = self.client().put(
            member_path,
            json={"owners": [2, 3], "users": [4]},
            headers=headers,
        )

        self.assertEqual(200, res.status_code)

        res = self.client().get(member_path, headers=headers)
        members = json.loads(res.data.decode())

        self.assertEqual(200, res.status_code)
        self.assertEqual(3, len(members))

        owner_count = 0

        for member in members:
            if member.get("is_owner"):
                owner_count += 1

        self.assertEqual(owner_count, 2)

    def test_add_existing_combo(self):
        """Should not be able to add owners or members that already exist."""
        headers = self.generate_auth_headers(user_id=4)

        res = self.client().post(
            f"{self.role_route}/1/member",
            json={"owners": [4], "users": [2]},
            headers=headers,
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("Role member already exists.", res.data.decode())

    def test_wrong_key(self):
        """Validates that an error is thrown when the wrong key is placed in the request body."""
        headers = self.generate_auth_headers()

        res = self.client().post(
            f"{self.role_route}/1/member",
            json={"owners": [2], "members": [3]},
            headers=headers,
        )

        self.assertEqual(res.status_code, 422)
        self.assertIn(
            "Body must have only the accepted keys: ['owners', 'users']",
            res.data.decode(),
        )

    def test_delete_all_owners(self):
        """Validates that an error is thrown when all owners are deleted."""
        headers = self.generate_auth_headers(user_id=4)

        res = self.client().delete(
            f"{self.role_route}/1/member",
            json={"owners": [3, 4], "members": []},
            headers=headers,
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("Role must have at least one owner.", res.data.decode())

    def test_delete_owner(self):
        """Validates that an owner may be deleted by another owner."""
        headers = self.generate_auth_headers(user_id=4)

        res = self.client().delete(
            f"{self.role_route}/1/member",
            json={"owners": [3], "members": []},
            headers=headers,
        )

        self.assertEqual(res.status_code, 200)

        res = self.client().get(f"{self.role_route}/1/member", headers=headers)
        members = json.loads(res.data.decode())

        self.assertEqual(len(members), 2)

        owner_count = 0
        for member in members:
            if member.get("is_owner"):
                owner_count += 1

        self.assertEqual(owner_count, 1)

    def test_delete_combo(self):
        """Validates that multiple members may be deleted at once."""
        headers = self.generate_auth_headers(user_id=4)

        res = self.client().delete(
            f"{self.role_route}/1/member",
            json={"owners": [3], "members": [1]},
            headers=headers,
        )

        self.assertEqual(res.status_code, 200)

        res = self.client().get(f"{self.role_route}/1/member", headers=headers)
        members = json.loads(res.data.decode())

        self.assertEqual(len(members), 1)

        owner_count = 0
        for member in members:
            if member.get("is_owner"):
                owner_count += 1

        self.assertEqual(owner_count, 1)

    def test_put_empty_owners(self):
        """Validates that a blank owner list is not replacing the old owner list."""
        headers = self.generate_auth_headers(user_id=4)

        res = self.client().put(
            f"{self.role_route}/1/member",
            json={"owners": [], "users": [4]},
            headers=headers,
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("Role must have at least one owner.", res.data.decode())
