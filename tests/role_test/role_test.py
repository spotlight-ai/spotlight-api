import json

from tests.test_main import BaseTest


class RoleResourceTest(BaseTest):
    def test_create_role(self):
        """Tests functionality of creating a role with a single owner. The role should be returned."""
        headers = self.generate_auth_headers()
        
        res = self.client().post(self.role_route, json=self.role_object, headers=headers)
        
        self.assertEqual(201, res.status_code)
        self.assertIn(self.role_object.get('role_name'), res.data.decode())
        
        res = self.client().get(self.role_route, headers=headers)
        members = json.loads(res.data.decode())[0].get('members')
        
        self.assertEqual(len(members), 1)
        self.assertTrue(members[0].get('is_owner'))
    
    def test_create_role_multiple_owners(self):
        """Tests functionality of creating a role with more than one owner."""
        headers = self.generate_auth_headers()
        
        new_role = self.role_object.copy()
        new_role['owners'] = [1, 2]
        
        res = self.client().post(self.role_route, json=new_role, headers=headers)
        self.assertEqual(res.status_code, 201)
        
        res = self.client().get(self.role_route, headers=headers)
        members = json.loads(res.data.decode())[0].get('members')
        
        self.assertEqual(len(members), 2)
        self.assertTrue(members[0].get('is_owner'))
        self.assertTrue(members[1].get('is_owner'))
    
    def test_create_role_creator_not_owner(self):
        """Creator should not be able to create a dataset where they are not an owner."""
        headers = self.generate_auth_headers()
        
        new_role = self.role_object.copy()
        new_role['owners'] = [2, 3]
        
        res = self.client().post(self.role_route, json=new_role, headers=headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Creator must be listed as a dataset owner.', res.data.decode())
    
    def test_create_role_authentication(self):
        """Ensures that role endpoints require authentication."""
        res = self.client().post(self.role_route, json=self.role_object)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Missing authorization header", res.data.decode())
        
        res = self.client().get(self.role_route)
        
        self.assertEqual(res.status_code, 400)
        self.assertIn("Missing authorization header", res.data.decode())
        
        res = self.client().get(f'{self.role_route}/1')
        self.assertEqual(res.status_code, 400)
        self.assertIn("Missing authorization header", res.data.decode())
        
        res = self.client().delete(f'{self.role_route}/1')
        self.assertEqual(res.status_code, 400)
        self.assertIn("Missing authorization header", res.data.decode())
    
    def test_get_roles(self):
        """Tests GET /role endpoint. Should return only roles owned by the requester."""
        headers = self.generate_auth_headers()
        
        res = self.client().get(self.role_route, headers=headers)
        roles = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(roles), 0)
        
        self.client().post(self.role_route, json=self.role_object, headers=headers)
        res = self.client().get(self.role_route, headers=headers)
        roles = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(roles), 1)
    
    def test_get_single_role(self):
        """Get a single, existing role."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().get(f'{self.role_route}/1', headers=headers)
        role = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(role.get('role_name'), 'Financial Developers')
    
    def test_get_missing_role(self):
        """Attempt to retrieve a role that doesn't exist."""
        headers = self.generate_auth_headers()
        
        res = self.client().get(f'{self.role_route}/10', headers=headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn('Role either does not exist or user does not have permissions.', res.data.decode())
    
    def test_get_unowned_role(self):
        headers = self.generate_auth_headers(user_id=2)
        
        res = self.client().get(f'{self.role_route}/2', headers=headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn('Role either does not exist or user does not have permissions.', res.data.decode())
    
    def test_delete_role(self):
        """Attempt to retrieve a role that doesn't exist."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().delete(f'{self.role_route}/1', headers=headers)
        self.assertEqual(res.status_code, 200)
    
    def test_delete_missing_role(self):
        """Attempt to retrieve a role that doesn't exist."""
        headers = self.generate_auth_headers()
        
        res = self.client().delete(f'{self.role_route}/10', headers=headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn('Role either does not exist or user does not have permissions.', res.data.decode())
    
    def test_update_role_name(self):
        """Owners should be able to update a role's name."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().put(f'{self.role_route}/1', json={'role_name': 'Updated Role Name'}, headers=headers)
        self.assertEqual(res.status_code, 200)
        role = json.loads(res.data.decode())
        
        self.assertEqual(role.get('role_name'), 'Updated Role Name')
    
    def test_update_unowned_role(self):
        """Users should not be able to update roles they do not own."""
        headers = self.generate_auth_headers(user_id=2)
        
        res = self.client().put(f'{self.role_route}/1', json={'role_name': 'Updated Role Name'}, headers=headers)
        self.assertEqual(res.status_code, 404)
        self.assertIn('Role either does not exist or user does not have permissions.', res.data.decode())
    
    def test_update_owners(self):
        """Owners should be able to update owner list for roles."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().put(f'{self.role_route}/1', json={'owners': [2, 3]}, headers=headers)
        self.assertEqual(res.status_code, 200)
        role = json.loads(res.data.decode())
        
        owner_ids = []
        for member in role.get('members'):
            if member.get('is_owner'):
                owner_ids.append(member.get('user').get('user_id'))
        
        self.assertEqual(owner_ids, [2, 3])
    
    def test_update_multiple_role_properties(self):
        """Owners should be able to update multiple properties at once for roles."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().put(f'{self.role_route}/1', json={'owners': [2, 3, 4], 'role_name': 'Other Role'},
                                headers=headers)
        self.assertEqual(res.status_code, 200)
        role = json.loads(res.data.decode())
        
        self.assertEqual(role.get('role_name'), 'Other Role')
        
        owner_ids = []
        for member in role.get('members'):
            if member.get('is_owner'):
                owner_ids.append(member.get('user').get('user_id'))
        
        self.assertEqual(owner_ids, [2, 3, 4])
    
    def test_update_empty_owners(self):
        """Owners should be able to update owner list for roles."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().put(f'{self.role_route}/1', json={'owners': []}, headers=headers)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Role must have at least one owner.', res.data.decode())
