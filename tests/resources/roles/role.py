import os
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
        
        self.user_route = '/user'
        self.role_route = '/role'
        self.login_route = '/login'
        self.headers = {'Authorization': f'Bearer {os.environ.get("MODEL_KEY")}'}
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_create_role(self):
        self.client().post(self.user_route, json=self.user)
        # another thing
        pass
