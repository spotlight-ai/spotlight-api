import json

from tests.test_main import BaseTest


class JobResourceTest(BaseTest):
    def test_valid_job_creation(self):
        headers = self.generate_auth_headers(user_id=3)
        res = self.client().get(self.flatfile_route, headers=headers)
        datasets = json.loads(res.data.decode())
        
        res = self.client().post(self.job_route, headers=headers, json={'dataset_id': 1})
        
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data.decode(), 'null\n')
    
    def test_extra_field_job_creation(self):
        headers = self.generate_auth_headers(user_id=3)
        res = self.client().get(self.flatfile_route, headers=headers)
        datasets = json.loads(res.data.decode())
        
        res = self.client().post(self.job_route, headers=headers, json={
            'dataset_id': datasets[0].get('dataset_id'),
            'name': 'John'
        })
        
        self.assertEqual(res.status_code, 422)
        self.assertIn('Unknown field.', str(res.data))
    
    def test_missing_field_job_creation(self):
        headers = self.generate_auth_headers(user_id=3)
        res = self.client().get(self.flatfile_route, headers=headers)
        datasets = json.loads(res.data.decode())
        
        job_object = {
            'dataset_id': datasets[0].get('dataset_id')
        }
        
        wrong_job = job_object.copy()
        wrong_job.pop('dataset_id')
        
        res = self.client().post(self.job_route, headers=headers, json={})
        
        self.assertEqual(res.status_code, 422)
        self.assertIn('Missing data for required field.', res.data.decode())
    
    def test_retrieve_all_jobs(self):
        headers = self.generate_auth_headers(user_id=3)
        res = self.client().get(self.flatfile_route, headers=headers)
        datasets = json.loads(res.data.decode())
        
        self.client().post(self.job_route, headers=headers, json={'dataset_id': datasets[0].get('dataset_id')})
        
        res = self.client().get(self.job_route, headers=headers)
        response_body = json.loads(res.data.decode())
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 1)
    
    def test_missing_auth_retrieve_all_jobs(self):
        res = self.client().get(self.job_route)
        
        self.assertEqual(res.status_code, 400)
        self.assertIn('Missing authorization header', res.data.decode())
    
    def test_incorrect_auth_retrieve_all_users(self):
        incorrect_header = {'authorization': 'Bearer wrong'}
        
        res = self.client().get(self.job_route, headers=incorrect_header)
        
        self.assertEqual(res.status_code, 401)
