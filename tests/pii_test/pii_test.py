import json

from tests.test_main import BaseTest


class PIITest(BaseTest):
    def test_retrieve_pii(self):
        """Verifies that all PII markers can be retrieved."""
        headers = self.generate_auth_headers(user_id=1)

        res = self.client().get(self.pii_route, headers=headers)

        pii = json.loads(res.data.decode())

        self.assertEqual(200, res.status_code)
        self.assertEqual(3, len(pii))
        self.assertIn("description", pii[0])
        self.assertIn("long_description", pii[0])
        self.assertIn("category", pii[0])

    def test_unauthenticated_retrieve_pii(self):
        """Verifies that unauthenticated users cannot retrieve the PII list."""
        res = self.client().get(self.pii_route)

        self.assertEqual(400, res.status_code)
