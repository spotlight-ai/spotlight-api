import json
import unittest

from app import create_app, db


class RoleResourceTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client
        self.user = {
            'first_name': 'Doug',
            'last_name': 'Developer',
            'email': 'test@email.com',
            'password': 'testpassword'
        }
        
        self.role = {
            'role_name': 'Developers'
        }
        
        self.user_route = '/user'
        self.role_route = '/role'
        self.login_route = '/login'
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def generate_auth_headers(self):
        self.client().post(self.user_route, json=self.user)
        
        creds = {'email': self.user.get('email'), 'password': self.user.get('password')}
        
        login_res = self.client().post(self.login_route, json=creds)
        token = json.loads(login_res.data.decode()).get('token')
        return {'Authorization': f'Bearer {token}'}
    
    def test_create_role(self):
        headers = self.generate_auth_headers()
        
        res = self.client().post(self.role_route, json=self.role, headers=headers)
        
        self.assertEqual(201, res.status_code)
        self.assertIn(self.role.get('role_name'), res.data.decode())
        
        res = self.client().get(self.role_route, headers=headers)
        members = json.loads(res.data.decode())[0].get('members')
        
        self.assertEqual(len(members), 1)
        self.assertTrue(members[0].get('is_owner'))
    
    def test_create_role_multiple_owners(self):
        headers = self.generate_auth_headers()
        new_user = self.user.copy()
        new_user['email'] = 'another@gmail.com'
        
        self.client().post(self.user_route, json=new_user)
        
        new_role = self.role.copy()
        new_role['owners'] = [1, 2]
        
        res = self.client().post(self.role_route, json=new_role, headers=headers)
        self.assertEqual(res.status_code, 201)
        
        res = self.client().get(self.role_route, headers=headers)
        members = json.loads(res.data.decode())[0].get('members')
        
        self.assertEqual(len(members), 2)
        self.assertTrue(members[0].get('is_owner'))
        self.assertTrue(members[1].get('is_owner'))
