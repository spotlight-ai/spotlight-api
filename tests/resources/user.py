import json
import os
import unittest

from dotenv import find_dotenv, load_dotenv

from app import create_app, db

load_dotenv(find_dotenv())


class UserResourceTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client
        self.user = {
            'first_name': 'Doug',
            'last_name': 'Developer',
            'email': 'test@email.com',
            'password': 'testpassword'
        }
        
        self.collection_endpoint = '/user'
        self.headers = {'Authorization': f'Bearer {os.environ.get("MODEL_KEY")}'}
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_valid_user_creation(self):
        res = self.client().post(self.collection_endpoint, json=self.user)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data.decode(), 'null\n')
    
    def test_extra_field_user_creation(self):
        wrong_user = self.user.copy()
        extra_field = 'middle_name'
        extra_value = 'Test'
        wrong_user[extra_field] = extra_value
        
        res = self.client().post(self.collection_endpoint, json=wrong_user)
        self.assertEqual(res.status_code, 422)
        self.assertIn('Unknown field.', str(res.data))
    
    def test_missing_field_user_creation(self):
        wrong_user = self.user.copy()
        wrong_user.pop("email")
        
        res = self.client().post(self.collection_endpoint, json=wrong_user)
        self.assertEqual(res.status_code, 422)
        self.assertIn('Missing data for required field.', res.data.decode())
    
    def test_duplicate_user_creation(self):
        self.client().post(self.collection_endpoint, json=self.user)
        res = self.client().post(self.collection_endpoint, json=self.user)
        
        self.assertEqual(res.status_code, 400)
        self.assertIn('User already exists.', res.data.decode())
    
    def test_retrieve_all_users(self):
        self.client().post(self.collection_endpoint, json=self.user)
        
        res = self.client().get(self.collection_endpoint, headers=self.headers)
        response_body = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 1)
    
    def test_missing_auth_retrieve_all_users(self):
        res = self.client().get(self.collection_endpoint)
        
        self.assertEqual(res.status_code, 400)
        self.assertIn('Missing authorization header', res.data.decode())
    
    def test_incorrect_auth_retrieve_all_users(self):
        incorrect_header = {'authorization': 'Bearer wrong'}
        
        res = self.client().get(self.collection_endpoint, headers=incorrect_header)
        
        self.assertEqual(res.status_code, 401)
    
    def test_filter_user_list(self):
        second_user = self.user.copy()
        second_user['first_name'] = 'John'
        second_user['email'] = 'test123@gmail.com'
        self.client().post(self.collection_endpoint, json=self.user)
        self.client().post(self.collection_endpoint, json=second_user)
        
        res = self.client().get(f'{self.collection_endpoint}?query={self.user.get("first_name")[:3]}',
                                headers=self.headers)
        response_body = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 1)
        
        res = self.client().get(f'{self.collection_endpoint}?query={self.user.get("last_name")[:4]}',
                                headers=self.headers)
        response_body = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 2)
        
        res = self.client().get(f'{self.collection_endpoint}?query={self.user.get("email")[:6]}', headers=self.headers)
        response_body = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 1)
