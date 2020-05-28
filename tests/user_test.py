import json

from tests.test_main import BaseTest


class UserResourceTest(BaseTest):
    def test_valid_user_creation(self):
        res = self.client().post(self.user_route, json=self.user_object)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data.decode(), 'null\n')
    
    def test_extra_field_user_creation(self):
        wrong_user = self.user_object.copy()
        extra_field = 'middle_name'
        extra_value = 'Test'
        wrong_user[extra_field] = extra_value
        
        res = self.client().post(self.user_route, json=wrong_user)
        self.assertEqual(res.status_code, 422)
        self.assertIn('Unknown field.', str(res.data))
    
    def test_missing_field_user_creation(self):
        wrong_user = self.user_object.copy()
        wrong_user.pop("email")
        
        res = self.client().post(self.user_route, json=wrong_user)
        self.assertEqual(res.status_code, 422)
        self.assertIn('Missing data for required field.', res.data.decode())
    
    def test_duplicate_user_creation(self):
        self.client().post(self.user_route, json=self.user_object)
        res = self.client().post(self.user_route, json=self.user_object)
        
        self.assertEqual(res.status_code, 400)
        self.assertIn('User already exists.', res.data.decode())
    
    def test_retrieve_all_users(self):
        headers = self.generate_auth_headers()
        
        res = self.client().get(self.user_route, headers=headers)
        response_body = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), len(self.users))
    
    def test_missing_auth_retrieve_all_users(self):
        res = self.client().get(self.user_route)
        
        self.assertEqual(res.status_code, 400)
        self.assertIn('Missing authorization header', res.data.decode())
    
    def test_incorrect_auth_retrieve_all_users(self):
        incorrect_header = {'authorization': 'Bearer wrong'}
        
        res = self.client().get(self.user_route, headers=incorrect_header)
        
        self.assertEqual(res.status_code, 401)
    
    def test_filter_user_list(self):
        """Filters user list based on query."""
        headers = self.generate_auth_headers()
        
        res = self.client().get(f'{self.user_route}?query=doug',
                                headers=headers)
        response_body = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 1)
        
        res = self.client().get(f'{self.user_route}?query=developer',
                                headers=headers)
        response_body = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 2)
        
        res = self.client().get(f'{self.user_route}?query=doug@spotli', headers=headers)
        response_body = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 1)
