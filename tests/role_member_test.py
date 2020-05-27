import json

from tests.test_main import BaseTest


class RoleMemberResourceTest(BaseTest):
    def test_get_role_members(self):
        """Retrieves all members for a given role."""
        headers = self.generate_auth_headers()
        
        res = self.client().get(f'{self.role_route}/1/member', headers=headers)
        
        members = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(members), 3)
    
    def test_get_role_members_missing_role(self):
        """Verifies that an error is thrown when requested role does not exist."""
        headers = self.generate_auth_headers()
        
        res = self.client().get(f'{self.role_route}/10/member', headers=headers)
        
        self.assertEqual(res.status_code, 404)
        self.assertIn('Role not found', res.data.decode())
    
    def test_add_owner_to_unowned_role(self):
        """Verifies that an error is thrown if a user tries to add an owner to a role they don't own."""
        headers = self.generate_auth_headers()
        
        res = self.client().post(f'{self.role_route}/2/member', json={'owners': [2], 'users': [3]}, headers=headers)
        
        self.assertEqual(res.status_code, 401)
        self.assertIn('Not allowed to add permissions to this role', res.data.decode())
    
    def test_add_owner(self):
        """Adds an owner to a role."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().post(f'{self.role_route}/1/member', json={'owners': [2], 'users': []}, headers=headers)
        
        self.assertEqual(res.status_code, 201)
        
        res = self.client().get(f'{self.role_route}/1/member', headers=headers)
        members = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(members), 4)
    
    def test_add_members(self):
        """Adds multiple members to a role."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().post(f'{self.role_route}/1/member', json={'owners': [], 'users': [5, 6]}, headers=headers)
        
        self.assertEqual(res.status_code, 201)
        
        res = self.client().get(f'{self.role_route}/1/member', headers=headers)
        members = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(members), 5)
        
        owner_count = 0
        
        for member in members:
            if member.get('is_owner'):
                owner_count += 1
        
        self.assertEqual(owner_count, 2)
    
    def test_add_combo(self):
        """Adds a combination of users and owners."""
        headers = self.generate_auth_headers(user_id=4)
        
        res = self.client().post(f'{self.role_route}/1/member', json={'owners': [5], 'users': [2]}, headers=headers)
        
        self.assertEqual(res.status_code, 201)
        
        res = self.client().get(f'{self.role_route}/1/member', headers=headers)
        members = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(members), 5)
        
        owner_count = 0
        
        for member in members:
            if member.get('is_owner'):
                owner_count += 1
        
        self.assertEqual(owner_count, 3)
    
    def test_wrong_key(self):
        """Validates that an error is thrown when the wrong key is placed in the request body."""
        headers = self.generate_auth_headers()
        
        res = self.client().post(f'{self.role_route}/1/member', json={'owners': [2], 'members': [3]}, headers=headers)
        
        self.assertEqual(res.status_code, 422)
        self.assertIn("Unknown key", res.data.decode())
