import json

from tests.test_main import BaseTest


class RolePermissionResourceTest(BaseTest):
    def test_get_role_permissions(self):
        """Role owner should be able to retrieve permissions assigned to a given role."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().get(f'{self.role_route}/1/permission', headers=headers)
        
        self.assertEqual(res.status_code, 200)
        permissions = json.loads(res.data.decode())
        
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].get('description'), 'ssn')
    
    def test_get_role_permissions_unowned_role(self):
        """User of an unowned role should not be able to see permission details."""
        headers = self.generate_auth_headers(user_id=2)
        
        res = self.client().get(f'{self.role_route}/1/permission', headers=headers)
        
        self.assertEqual(res.status_code, 401)
    
    def test_add_new_role_permission(self):
        """Tests that a role owner can add an individual permission to a role."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().post(f'{self.role_route}/1/permission', headers=headers, json={'permissions': ['name']})
        
        self.assertEqual(res.status_code, 201)
        
        res = self.client().get(f'{self.role_route}/1/permission', headers=headers)
        permissions = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(permissions), 2)
    
    def test_add_multiple_permissions(self):
        """Verify that owners can add multiple permissions at once to a role."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().post(f'{self.role_route}/1/permission', headers=headers,
                                 json={'permissions': ['address', 'name']})
        
        self.assertEqual(res.status_code, 201)
        
        res = self.client().get(f'{self.role_route}/1/permission', headers=headers)
        permissions = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(permissions), 3)
    
    def test_add_same_permission(self):
        """Owners should not be able to add the same permission to a role."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().post(f'{self.role_route}/1/permission', headers=headers,
                                 json={'permissions': ['ssn', 'name']})
        
        self.assertEqual(res.status_code, 400)
