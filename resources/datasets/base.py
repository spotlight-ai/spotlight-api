import os

import requests
from flask import abort, request
from flask_restful import Resource
from sqlalchemy.sql.expression import true

from core.aws import generate_presigned_download_link
from core.decorators import authenticate_token
from db import db
from models.datasets.base import DatasetModel
from models.datasets.flat_file import FlatFileDatasetModel
from models.user import UserModel
from schemas.datasets.base import DatasetSchema
from schemas.datasets.flat_file import FlatFileDatasetSchema
from schemas.job import JobSchema

flat_file_dataset_schema = FlatFileDatasetSchema()
dataset_schema = DatasetSchema()
job_schema = JobSchema()


class DatasetCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        """
        Returns a list of datasets that are owned by and shared with the currently logged in user.

        Note: This will only return datasets that have been verified.

        :param user_id: Currently logged in user ID
        :return: List of datasets
        """
        logged_in_user = UserModel.query.filter_by(user_id=user_id).first()
        owned_datasets = DatasetModel.query.filter(DatasetModel.verified == true(),
                                                   DatasetModel.owners.contains(logged_in_user)).all()
        # TODO: Add shared datasets once the sharing functionality is completed
        return dataset_schema.dump(owned_datasets, many=True)


class Dataset(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        base_dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        if base_dataset.dataset_type == "FLAT_FILE":
            dataset = FlatFileDatasetModel.query.filter_by(dataset_id=dataset_id).first()
            s3_object_key = dataset.location.split('/')[-1]
            dataset.download_link = generate_presigned_download_link('uploaded-datasets', s3_object_key)
            return flat_file_dataset_schema.dump(dataset)
        abort(404, "Dataset not found")


class DatasetVerification(Resource):
    @authenticate_token
    def post(self, user_id):
        """
        Verifies that a dataset has been uploaded. Accepts a list of dataset IDs that are to be verified, and checks
        dataset upload on AWS S3.

        :param user_id: Currently logged in user ID
        :return: None
        """
        request_body = request.get_json(force=True)
        dataset_ids = request_body['dataset_ids']
        
        datasets = DatasetModel.query.filter(DatasetModel.dataset_id.in_(dataset_ids)).all()
        
        job_ids = []
        
        for dataset in datasets:
            if not dataset.verified:
                # TODO: Add S3 verification.
                # TODO: Add API call to model API to run job that is created.
                # TODO: Add Kafka messaging queue implementation for job queueing.
                job = job_schema.load({'dataset_id': dataset.dataset_id})
                db.session.add(job)
                dataset.verified = True
                
                db.session.flush()
                db.session.refresh(job)
                
                db.session.commit()
                
                url = f'http://{os.getenv("MODEL_HOST")}:{os.getenv("MODEL_PORT")}/predict/file'
                payload = {'job_id': job.job_id}
                
                job_ids.append(job.job_id)
                requests.post(url, json=payload)
        
        db.session.commit()
        return {'job_ids': job_ids}
