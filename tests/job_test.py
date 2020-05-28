import json
import os
import unittest

from tests.test_main import BaseTest

from dotenv import find_dotenv, load_dotenv

from app import create_app, db

load_dotenv(find_dotenv())


class JobResourceTest(BaseTest):
    def setUp(self):
        self.app = create_app('config.TestingConfig')
        self.client = self.app.test_client
        self.flatfile = {
            'dataset_name': 'NAME',
            'location': "California"
        }
        self.job = {
            'dataset_id': self.flatfile.get('dataset_id')
        }

        self.collection_endpoint1 = '/job'
        self.collection_endpoint2 = '/job/<int:job_id>'
        self.headers = {'Authorization': f'Bearer {os.environ.get("MODEL_KEY")}'}

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_valid_job_creation(self):
        print(self.job)
        res = self.client().post(self.collection_endpoint1, json=self.job)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data.decode(), 'null\n')

    def test_extra_field_job_creation(self):
        wrong_job = self.job.copy()
        extra_field = 'id'
        extra_value = "Hello"
        wrong_job[extra_field] = extra_value

        res = self.client().post(self.collection_endpoint1, json=wrong_job)
        self.assertEqual(res.status_code, 422)
        self.assertIn('Unknown field.', str(res.data))

    def test_missing_field_job_creation(self):
        wrong_job = self.job.copy()
        wrong_job.pop("dataset_id")

        res = self.client().post(self.collection_endpoint1, json=wrong_job)
        self.assertEqual(res.status_code, 422)
        self.assertIn('Missing data for required field.', res.data.decode())

    def test_retrieve_all_jobs(self):
        self.client().post(self.collection_endpoint1, json=self.job)

        res = self.client().get(self.collection_endpoint1, headers=self.headers)
        response_body = json.loads(res.data.decode())

        self.assertEqual(res.status_code, 200)

        print(response_body)
        #???
        #self.assertEqual(len(response_body), 1)

    def test_missing_auth_retrieve_all_jobs(self):
        res = self.client().get(self.collection_endpoint1)

        self.assertEqual(res.status_code, 400)
        self.assertIn('Missing authorization header', res.data.decode())

    def test_incorrect_auth_retrieve_all_users(self):
        incorrect_header = {'authorization': 'Bearer wrong'}

        res = self.client().get(self.collection_endpoint1, headers=incorrect_header)

        self.assertEqual(res.status_code, 401)
