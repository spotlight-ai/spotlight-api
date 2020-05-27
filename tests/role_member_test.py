import json
import unittest

from app import create_app, db


class RoleMemberResourceTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client
        
        self.role = {
            'role_name': 'Developers'
        }
        
        self.user_route = '/user'
        self.role_route = '/role'
        
        with self.app.app_context():
            from models.user import UserModel
            from models.roles.role import RoleModel
            from models.roles.role_member import RoleMemberModel
            
            db.create_all()
            
            user_1 = UserModel(first_name='Doug', last_name='Developer', email='test@email.com',
                               password='testpassword')
            user_2 = UserModel(first_name='Dana', last_name='Developer', email='test_2@email.com',
                               password='testpassword')
            
            role = RoleModel(creator_id=2, role_name='Developers')
            role_member = RoleMemberModel(role_id=1, user_id=2, is_owner=True)
            
            db.session.add(user_1)
            db.session.add(user_2)
            db.session.add(role)
            db.session.add(role_member)
            db.session.commit()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def generate_auth_headers(self):
        """Logs in for user #1 and generates authentication token."""
        creds = {'email': 'test@email.com', 'password': 'testpassword'}
        login_route = '/login'
        
        login_res = self.client().post(login_route, json=creds)
        token = json.loads(login_res.data.decode()).get('token')
        return {'Authorization': f'Bearer {token}'}
    
    def test_get_role_members(self):
        headers = self.generate_auth_headers()
        
        res = self.client().get(f'{self.role_route}/1/member', headers=headers)
        
        members = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(members), 1)
    
    def test_get_role_members_missing_role(self):
        headers = self.generate_auth_headers()
        
        res = self.client().get(f'{self.role_route}/10/member', headers=headers)
        
        self.assertEqual(res.status_code, 404)
        self.assertIn('Role not found', res.data.decode())
