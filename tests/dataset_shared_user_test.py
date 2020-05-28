import json

from tests.test_main import BaseTest


class DatasetSharedUserResourceTest(BaseTest):
    def test_get_dataset_shared_users(self):
        headers = self.generate_auth_headers(user_id=3)
        res = self.client().get(f'{self.dataset_route}/1/user', headers=headers)
        
        self.assertEqual(res.status_code, 200)
        shared_users = json.loads(res.data.decode())
        
        self.assertEqual(len(shared_users), 2)
        
        for user in shared_users:
            self.assertEqual(user.get('permissions'), [])
    
    def test_get_unowned_dataset_shared_users(self):
        headers = self.generate_auth_headers(user_id=1)
        res = self.client().get(f'{self.dataset_route}/1/user', headers=headers)
        
        self.assertEqual(res.status_code, 401)
    
    def test_add_dataset_shared_user(self):
        headers = self.generate_auth_headers(user_id=3)
        
        res = self.client().post(f'{self.dataset_route}/1/user', headers=headers, json=[{'user_id': 5}])
        
        self.assertEqual(res.status_code, 201)
        
        res = self.client().get(f'{self.dataset_route}/1/user', headers=headers)
        
        self.assertEqual(res.status_code, 200)
        shared_users = json.loads(res.data.decode())
        
        self.assertEqual(len(shared_users), 3)
        
        for user in shared_users:
            self.assertEqual(user.get('permissions'), [])
    
    def test_add_dataset_shared_user_already_owner(self):
        headers = self.generate_auth_headers(user_id=3)
        
        res = self.client().post(f'{self.dataset_route}/2/user', headers=headers, json=[{'user_id': 4}])
        
        self.assertEqual(res.status_code, 400)
        self.assertIn('cannot be shared with owner', res.data.decode())
    
    def test_add_dataset_shared_user_already_shared(self):
        headers = self.generate_auth_headers(user_id=3)
        
        res = self.client().post(f'{self.dataset_route}/1/user', headers=headers, json=[
            {
                'user_id': 1
            },
            {
                'user_id': 2
            }
        ])
        
        self.assertEqual(res.status_code, 400)
        self.assertIn('already shared', res.data.decode())
    
    def test_remove_dataset_shared_users(self):
        headers = self.generate_auth_headers(user_id=3)
        
        res = self.client().delete(f'{self.dataset_route}/1/user', headers=headers, json=[
            {
                'user_id': 1
            },
            {
                'user_id': 2
            }
        ])
        
        self.assertEqual(res.status_code, 204)
        
        res = self.client().get(f'{self.dataset_route}/1/user', headers=headers)
        shared_users = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(shared_users), 0)
    
    def test_add_dataset_shared_user_with_permissions(self):
        headers = self.generate_auth_headers(user_id=3)
        
        res = self.client().post(f'{self.dataset_route}/1/user', headers=headers, json=[
            {
                'user_id': 5,
                'permissions': ['ssn', 'name']
            },
            {
                'user_id': 4,
                'permissions': ['ssn']
            }
        ])
        
        self.assertEqual(res.status_code, 201)
        
        res = self.client().get(f'{self.dataset_route}/1/user', headers=headers)
        
        self.assertEqual(res.status_code, 200)
        shared_users = json.loads(res.data.decode())
        
        self.assertEqual(len(shared_users), 4)
        self.assertEqual(shared_users[2].get('permissions'), [{'description': 'ssn'}, {'description': 'name'}])
        self.assertEqual(shared_users[3].get('permissions'), [{'description': 'ssn'}])
