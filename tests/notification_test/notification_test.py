import json

from tests.test_main import BaseTest


class NotificationTest(BaseTest):
    def test_retrieve_notifications(self):
        """"Verifies that notifications can be retrieved for a given user."""
        headers = self.generate_auth_headers(user_id=1)

        res = self.client().get(self.notification_route, headers=headers)

        notifications = json.loads(res.data.decode())

        self.assertEqual(200, res.status_code)
        self.assertEqual(2, len(notifications))
        self.assertIn("created_ts", notifications[0])
        self.assertIn("viewed", notifications[0])
        self.assertIn("last_updated_ts", notifications[0])
        self.assertIn("notification_id", notifications[0])
        self.assertIn("title", notifications[0])
        self.assertIn("detail", notifications[0])

        for notification in notifications:
            self.assertFalse(notification.get("viewed"))

    def test_retrieve_notifications_user_with_none(self):
        """Verifies that a user with no notifications returns an empty list."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().get(self.notification_route, headers=headers)

        notifications = json.loads(res.data.decode())

        self.assertEqual(200, res.status_code)
        self.assertEqual(0, len(notifications))

    def test_retrieve_notifications_all_viewed(self):
        """Verifies that an error is thrown when notifications are fetched for a user that doesn't exist."""
        headers = self.generate_auth_headers(user_id=2)

        res = self.client().get(self.notification_route, headers=headers)

        notifications = json.loads(res.data.decode())

        self.assertEqual(200, res.status_code)
        self.assertEqual(0, len(notifications))

    def test_update_notifications(self):
        """Verifies that a notification can be updated."""
        headers = self.generate_auth_headers(user_id=2)

        res = self.client().patch(
            f"{self.notification_route}/4", headers=headers, json={"viewed": False}
        )

        notification = json.loads(res.data.decode())

        self.assertEqual(200, res.status_code)
        self.assertFalse(notification.get("viewed"))
        self.assertNotEqual(
            notification.get("last_updated_ts"), notification.get("created_ts")
        )

    def test_update_notification_bad_keys(self):
        """Verifies that an error is thrown if a user tries to update invalid keys."""
        headers = self.generate_auth_headers(user_id=2)

        res = self.client().patch(
            f"{self.notification_route}/4",
            headers=headers,
            json={"viewed": False, "otherTitle": "New Title"},
        )

        self.assertEqual(422, res.status_code)

    def test_update_notification_no_keys(self):
        """Verifies that an error is thrown if a user tries to update invalid keys."""
        headers = self.generate_auth_headers(user_id=2)

        res = self.client().patch(
            f"{self.notification_route}/4", headers=headers, json={},
        )

        notification = json.loads(res.data.decode())

        self.assertEqual(200, res.status_code)
        self.assertEqual(notification.get("title"), "Third Notification")
        self.assertEqual(notification.get("detail"), "More Detail")
        self.assertEqual(notification.get("viewed"), True)

    def test_update_notification_viewed_not_bool(self):
        """Verifies that an error is thrown if a user tries to update viewed with a non-boolean."""
        headers = self.generate_auth_headers(user_id=2)

        res = self.client().patch(
            f"{self.notification_route}/4", headers=headers, json={"viewed": "cat"},
        )

        self.assertEqual(422, res.status_code)

    def test_update_notification_doesnt_exist(self):
        """Verifies that an error is thrown if a user tries to update viewed with a non-boolean."""
        headers = self.generate_auth_headers(user_id=2)

        res = self.client().patch(
            f"{self.notification_route}/59", headers=headers, json={"viewed": False},
        )

        self.assertEqual(404, res.status_code)
        self.assertIn(
            "Notification not found.", res.data.decode(),
        )

    def test_update_notification_doesnt_own(self):
        """Verifies that an error is thrown if a user tries to update a notification that isn't theirs."""
        headers = self.generate_auth_headers(user_id=2)

        res = self.client().patch(
            f"{self.notification_route}/1", headers=headers, json={"viewed": False},
        )

        self.assertEqual(401, res.status_code)
