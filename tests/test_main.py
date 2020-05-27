import json
import unittest

from dotenv import find_dotenv, load_dotenv

from app import create_app, db

load_dotenv(find_dotenv())


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client
        
        # Define common objects to use in downstream test cases
        self.role_object = {
            'role_name': 'Test Role'
        }
        self.user_object = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@user.com',
            'password': 'testpass'
        }
        
        self.user_route = '/user'
        self.role_route = '/role'
        self.login_route = '/login'
        
        with self.app.app_context():
            # Pre-load database to desired state
            from models.user import UserModel
            from models.roles.role import RoleModel
            from models.roles.role_member import RoleMemberModel
            from models.pii.pii import PIIModel
            
            db.create_all()
            
            self.users = [
                {
                    'first_name': 'Doug',
                    'last_name': 'Developer',
                    'email': 'doug@spotlightai.com',
                    'password': 'testpassword'
                },
                {
                    'first_name': 'Dana',
                    'last_name': 'Developer',
                    'email': 'dana@spotlight.ai',
                    'password': 'pass123'
                },
                {
                    'first_name': 'Mary',
                    'last_name': 'Manager',
                    'email': 'mary@spotlight.ai',
                    'password': 'pass123'
                },
                {
                    'first_name': 'Mark',
                    'last_name': 'Manager',
                    'email': 'mark@spotlight.ai',
                    'password': 'pass123'
                },
                {
                    'first_name': 'Cindy',
                    'last_name': 'Compliance',
                    'email': 'cindy@spotlight.ai',
                    'password': 'pass123'
                },
                {
                    'first_name': 'Craig',
                    'last_name': 'Compliance',
                    'email': 'craig@spotlight.ai',
                    'password': 'pass123'
                },
                {
                    'first_name': 'Oscar',
                    'last_name': 'Outsider',
                    'email': 'oscar@oscartime.com',
                    'password': 'pass123'
                }
            ]
            
            role_1 = RoleModel(creator_id=4, role_name='Financial Developers')
            role_2 = RoleModel(creator_id=4, role_name='Personal Developers')
            role_1_owner_1 = RoleMemberModel(role_id=1, user_id=4, is_owner=True)
            role_1_owner_2 = RoleMemberModel(role_id=1, user_id=3, is_owner=True)
            role_1_user_1 = RoleMemberModel(role_id=1, user_id=1)
            
            role_2_owner_1 = RoleMemberModel(role_id=2, user_id=4, is_owner=True)
            role_2_user_1 = RoleMemberModel(role_id=2, user_id=2)
            
            for user in self.users:
                db.session.add(
                    UserModel(first_name=user.get('first_name'), last_name=user.get('last_name'),
                              email=user.get('email'), password=user.get('password')))
            
            pii_ssn = PIIModel('ssn')
            pii_name = PIIModel('name')
            pii_address = PIIModel('address')
            
            role_1.permissions = [pii_ssn]
            role_2.permissions = [pii_name, pii_address]
            
            db.session.add(role_1)
            db.session.add(role_2)
            db.session.add(role_1_owner_1)
            db.session.add(role_1_owner_2)
            db.session.add(role_1_user_1)
            db.session.add(role_2_owner_1)
            db.session.add(role_2_user_1)
            
            db.session.commit()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def generate_auth_headers(self, user_id=1):
        """Logs in for user and generates authentication token."""
        user = self.users[user_id - 1]
        
        creds = {'email': user.get('email'), 'password': user.get('password')}
        
        login_res = self.client().post(self.login_route, json=creds)
        token = json.loads(login_res.data.decode()).get('token')
        return {'Authorization': f'Bearer {token}'}
