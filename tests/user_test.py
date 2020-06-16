import json

from tests.test_main import BaseTest


class UserResourceTest(BaseTest):
    def test_valid_user_creation(self):
        """Validates that a user can be created with an entirely correct body."""
        res = self.client().post(
            self.user_route,
            json={
                "first_name": "Test",
                "last_name": "User",
                "email": "test@user.com",
                "password": "testpass",
            },
        )
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data.decode(), "null\n")

    def test_blank_input_user_creation(self):
        """Validates that each input must meet the expected criteria before creating the user."""
        res = self.client().post(
            self.user_route,
            json={"email": "", "password": "", "first_name": "", "last_name": ""},
        )

        self.assertEqual(res.status_code, 422)
        response = res.data.decode()
        self.assertIn("Not a valid email address.", response)
        self.assertIn("Shorter than minimum length 8.", response)
        self.assertIn("Shorter than minimum length 1.", response)

    def test_some_blank_fields(self):
        """Validates that errors are thrown even when some inputs are valid."""
        res = self.client().post(
            self.user_route,
            json={
                "email": "test@user.com",
                "password": "testpassword",
                "first_name": "",
                "last_name": "",
            },
        )

        self.assertEqual(res.status_code, 422)
        self.assertIn("Shorter than minimum length 1.", res.data.decode())

    def test_extra_field_user_creation(self):
        """Validates that an error is thrown when extra fields are present."""
        res = self.client().post(
            self.user_route,
            json={
                "first_name": "Test",
                "last_name": "User",
                "email": "test@user.com",
                "password": "testpass",
                "middle_name": "Middle",
            },
        )

        self.assertEqual(res.status_code, 422)
        self.assertIn("Unknown field.", str(res.data))

    def test_missing_field_user_creation(self):
        """Validates that an error is thrown when fields are missing."""
        res = self.client().post(
            self.user_route,
            json={"first_name": "Test", "last_name": "User", "email": "test@user.com"},
        )

        self.assertEqual(res.status_code, 422)
        self.assertIn("Missing data for required field.", res.data.decode())

    def test_password_too_short(self):
        """Validates that passwords must be of a certain length."""
        res = self.client().post(
            self.user_route,
            json={
                "first_name": "Test",
                "last_name": "User",
                "email": "test@user.com",
                "password": "test",
            },
        )

        self.assertEqual(res.status_code, 422)
        self.assertIn("Shorter than minimum length 8.", res.data.decode())

    def test_invalid_email_format(self):
        """Validates that email addresses must be a valid format."""
        res = self.client().post(
            self.user_route,
            json={
                "first_name": "Test",
                "last_name": "User",
                "email": "test.com",
                "password": "testpass",
            },
        )

        self.assertEqual(res.status_code, 422)
        self.assertIn("Not a valid email address.", res.data.decode())

    def test_invalid_user_update(self):
        """Validates that user e-mails cannot be updated."""
        headers = self.generate_auth_headers(user_id=1)
        res = self.client().patch(
            f"{self.user_route}/1", json={"email": "new@spotlight.ai"}, headers=headers,
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("Cannot edit this field.", res.data.decode())

    def test_duplicate_user_creation(self):
        """Validates that an error is thrown if a user with the same e-mail address already exists."""
        res = self.client().post(
            self.user_route,
            json={
                "first_name": "Test",
                "last_name": "User",
                "email": "dana@spotlight.ai",
                "password": "testpassword",
            },
        )

        self.assertEqual(res.status_code, 400)
        self.assertIn("User already exists.", res.data.decode())

    def test_retrieve_all_users(self):
        """Verifies that all users can be successfully retrieved."""
        headers = self.generate_auth_headers()

        res = self.client().get(self.user_route, headers=headers)
        response_body = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), len(self.users))

    def test_missing_auth_retrieve_all_users(self):
        """Verifies that users cannot be retrieved without an authorization token."""
        res = self.client().get(self.user_route)

        self.assertEqual(res.status_code, 400)
        self.assertIn("Missing authorization header", res.data.decode())

    def test_incorrect_auth_retrieve_all_users(self):
        """Verifies that users cannot be retrieved with an incorrect authorization token."""
        incorrect_header = {"authorization": "Bearer wrong"}

        res = self.client().get(self.user_route, headers=incorrect_header)

        self.assertEqual(res.status_code, 401)

    def test_filter_user_list(self):
        """Verifies that the user list can be filtered based on a query."""
        headers = self.generate_auth_headers()

        res = self.client().get(f"{self.user_route}?query=doug", headers=headers)
        response_body = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 1)

        res = self.client().get(f"{self.user_route}?query=developer", headers=headers)
        response_body = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 2)

        res = self.client().get(f"{self.user_route}?query=doug@spotli", headers=headers)
        response_body = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 1)

    def test_update_user(self):
        """Verifies that user information can be updated."""
        headers = self.generate_auth_headers(user_id=1)

        res = self.client().patch(
            f"{self.user_route}/1",
            headers=headers,
            json={"first_name": "New", "last_name": "User"},
        )

        self.assertEqual(200, res.status_code)

        user = json.loads(res.data.decode())

        self.assertEqual("New", user.get("first_name"))
        self.assertEqual("User", user.get("last_name"))

    def test_delete_user(self):
        """Verifies that a user can be deleted."""
        headers = self.generate_auth_headers(user_id=1)

        res = self.client().delete(f"{self.user_route}/1", headers=headers)

        self.assertEqual(200, res.status_code)

        res = self.client().get(f"{self.user_route}", headers=headers)
        users = json.loads(res.data.decode())
        self.assertEqual(len(self.users) - 1, len(users))

    def test_get_individual_user(self):
        """Verifies that individual user information can be fetched."""
        headers = self.generate_auth_headers(user_id=1)

        res = self.client().get(f"{self.user_route}/1", headers=headers)

        self.assertEqual(200, res.status_code)

        user = json.loads(res.data.decode())
        self.assertEqual(user.get("email"), "doug@spotlightai.com")

    def test_update_user_invalid_input(self):
        """Verifies that fields are valid when updating a user."""
        headers = self.generate_auth_headers(user_id=1)
        res = self.client().patch(
            f"{self.user_route}/1", json={"first_name": ""}, headers=headers,
        )

        self.assertEqual(422, res.status_code)
        self.assertIn("Shorter than minimum length 1.", res.data.decode())

    def test_get_user_doesnt_exist(self):
        """Verifies that an error is thrown when a non-existent user is fetched."""
        headers = self.generate_auth_headers(user_id=1)

        res = self.client().get(f"{self.user_route}/0", headers=headers)

        self.assertEqual(404, res.status_code)

    def test_patch_user_doesnt_exist(self):
        """Verifies that an error is thrown when a non-existent user is updated."""
        headers = self.generate_auth_headers(user_id=1)
        res = self.client().patch(
            f"{self.user_route}/0", json={"first_name": ""}, headers=headers,
        )

        self.assertEqual(res.status_code, 404)
