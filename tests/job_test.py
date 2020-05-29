import json

from tests.test_main import BaseTest


class JobResourceTest(BaseTest):
    def test_valid_job_creation(self):
        """Ensures successful job creation by Dataset owner."""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().post(self.job_route, headers=headers, json={'dataset_id': 1})

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data.decode(), 'null\n')

    def test_extra_field_job_creation(self):
        """Ensures failure upon job creation with extra field"""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().post(self.job_route, headers=headers, json={
            'dataset_id': 1,
            'name': 'John'
        })

        self.assertEqual(res.status_code, 422)
        self.assertIn('Unknown field.', str(res.data))

    def test_missing_field_job_creation(self):
        """Ensures failure upon job creation with missing field"""
        headers = self.generate_auth_headers(user_id=3)

        job_object = {
            'dataset_id': 1
        }

        wrong_job = job_object.copy()
        wrong_job.pop('dataset_id')

        res = self.client().post(self.job_route, headers=headers, json={})

        self.assertEqual(res.status_code, 422)
        self.assertIn('Missing data for required field.', res.data.decode())

    def test_retrieve_all_jobs(self):
        """Ensures that the owner of the Dataset is able to see all active jobs for that Dataset"""
        headers = self.generate_auth_headers(user_id=3)

        self.client().post(self.job_route, headers=headers, json={'dataset_id': 1})

        res = self.client().get(self.job_route, headers=headers)
        response_body = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(response_body), 1)

    def test_missing_auth_retrieve_all_jobs(self):
        """Ensures that if the owner of the Dataset is not logged in,
        they won't be able to see all of the jobs"""
        res = self.client().get(self.job_route)

        self.assertEqual(res.status_code, 400)
        self.assertIn('Missing authorization header', res.data.decode())

    def test_incorrect_auth_retrieve_all_jobs(self):
        """Ensures that if the individual trying to retrieve all jobs associated with the Dataset is
        not the owner of the Dataset, they will not be able to see the jobs"""
        incorrect_header = {'authorization': 'Bearer wrong'}

        res = self.client().get(self.job_route, headers=incorrect_header)

        self.assertEqual(res.status_code, 401)

    def test_incorrect_user_create_job(self):
        """Ensures that if the individual trying to create a job is not the owner of the Dataset,
        they will not be able to create a job"""
        headers = self.generate_auth_headers(user_id=1)

        res = self.client().post(self.job_route, headers=headers, json={'dataset_id': 1})

        self.assertEqual(res.status_code, 401)

    def test_nonexistent_dataset_job_creation(self):
        """Ensures that if an individual attempts to create a job for a Dataset that doesn't exist,
        they will not be permitted to do so"""
        headers = self.generate_auth_headers(user_id=3)

        res = self.client().post(self.job_route, headers=headers, json={'dataset_id': 9})

        self.assertEqual(res.status_code, 404)

    def test_access_all_active_jobs_all_datasets_user(self):
        """Ensures that if a user attempts to access all jobs for all Datasets (they own no Datasets)
        they will be refused"""
        header_user1 = self.generate_auth_headers(user_id=1)
        header_user3 = self.generate_auth_headers(user_id=3)
        header_user4 = self.generate_auth_headers(user_id=4)

        # User 3 posts a job for each Dataset they own
        self.client().post(self.job_route, headers=header_user3, json={'dataset_id': 1})
        self.client().post(self.job_route, headers=header_user3, json={'dataset_id': 2})
        self.client().post(self.job_route, headers=header_user3, json={'dataset_id': 3})

        # User 4 posts a job the Dataset they own
        self.client().post(self.job_route, headers=header_user4, json={'dataset_id': 4})

        # User 1 attempts to access jobs from all of these Datasets, none of which they own
        res1 = self.client().get(f'{self.job_route}/1', headers=header_user1)
        res2 = self.client().get(f'{self.job_route}/2', headers=header_user1)
        res3 = self.client().get(f'{self.job_route}/3', headers=header_user1)
        res4 = self.client().get(f'{self.job_route}/4', headers=header_user1)

        self.assertEqual(res1.status_code, 401)
        self.assertEqual(res2.status_code, 401)
        self.assertEqual(res3.status_code, 401)
        self.assertEqual(res4.status_code, 401)

    def test_access_all_active_jobs_all_datasets_owner(self):
        """Ensures that if a user attempts to access all jobs for all Datasets (including Datasets
        that they don't own) they will be refused"""
        header_user3 = self.generate_auth_headers(user_id=3)
        header_user4 = self.generate_auth_headers(user_id=4)

        # User 3 posts a job for each Dataset they own
        self.client().post(self.job_route, headers=header_user3, json={'dataset_id': 1})
        self.client().post(self.job_route, headers=header_user3, json={'dataset_id': 2})
        self.client().post(self.job_route, headers=header_user3, json={'dataset_id': 3})

        # User 4 posts a job for the Dataset they own
        self.client().post(self.job_route, headers=header_user4, json={'dataset_id': 4})

        # User 3 attempts to access all of the jobs pertaining to their Dataset as well
        # as a job that doesn't belong to their Dataset
        res1 = self.client().get(f'{self.job_route}/1', headers=header_user3)
        res2 = self.client().get(f'{self.job_route}/2', headers=header_user3)
        res3 = self.client().get(f'{self.job_route}/3', headers=header_user3)
        res4 = self.client().get(f'{self.job_route}/4', headers=header_user3)

        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res4.status_code, 401)

    def test_access_all_active_jobs_all_datasets_admin(self):
        """Ensures that if an administrator attempts to access all jobs for all Datasets
        (including Datasets that they don't own) they will be granted permission"""
        header_user5 = self.generate_auth_headers(user_id=5)
        header_user3 = self.generate_auth_headers(user_id=3)
        header_user4 = self.generate_auth_headers(user_id=4)

        # User 3 posts a job for each Dataset they own
        self.client().post(self.job_route, headers=header_user3, json={'dataset_id': 1})
        self.client().post(self.job_route, headers=header_user3, json={'dataset_id': 2})
        self.client().post(self.job_route, headers=header_user3, json={'dataset_id': 3})

        # User 4 posts a job the Dataset they own
        self.client().post(self.job_route, headers=header_user4, json={'dataset_id': 4})

        # Admin attempts to see all jobs associated with all Datasets
        res1 = self.client().get(f'{self.job_route}/1', headers=header_user5)
        res2 = self.client().get(f'{self.job_route}/2', headers=header_user5)
        res3 = self.client().get(f'{self.job_route}/3', headers=header_user5)
        res4 = self.client().get(f'{self.job_route}/4', headers=header_user5)

        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res4.status_code, 200)
