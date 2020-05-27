import json

from tests.test_main import BaseTest


class RolePermissionResourceTest(BaseTest):
    def test_get_role_permissions(self):
        """Role owner should be able to retrieve permissions assigned to a given role."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().get(f'{self.role_route}/1/permissions')
        
        self.assertEqual(res.status_code, 200)
        permissions = json.dumps(res.data.decode())
        
        self.assertEqual(len(permissions), 1)
