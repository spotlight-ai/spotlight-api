import os
from distutils.util import strtobool

import requests
from flask import abort, request
from flask_restful import Resource

from core.decorators import authenticate_token
from db import db
from models.datasets.base import DatasetModel
from models.datasets.flat_file import FlatFileDatasetModel
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
        Returns a list of datasets. There are two optional boolean query parameters: owned and shared. If 'owned' is
        True, a list of datasets owned by the requesting user will be returned. 'Shared' will return a list of
        datasets that have been shared with the requesting user. The parameters can be used together. If neither is
        true, a list of all datasets will be returned.

        Note: This will only return datasets that have been verified.

        :param user_id: Currently logged in user ID
        :return: List of datasets
        """
        args = request.args
        owned = args.get('owned')
        shared = args.get('shared')
        if owned:
            # TODO: Add correct querying for owned dataset once table is complete.
            owned = strtobool(owned)
        else:
            owned = False
        if shared:
            # TODO: Add correct querying for datasets shared with this user once the table is complete.
            shared = strtobool(shared)
        else:
            shared = False
        
        datasets = DatasetModel.query.filter_by(verified=True).all()
        return dataset_schema.dump(datasets, many=True)


class Dataset(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        base_dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        if base_dataset.dataset_type == "FLAT_FILE":
            dataset = FlatFileDatasetModel.query.filter_by(dataset_id=dataset_id).first()
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
                
                url = f'http://{os.getenv("MODEL_HOST")}:{os.getenv("MODEL_PORT")}/predict/file'
                payload = {'job_id': job.job_id}
                job_ids.append(job.job_id)
                requests.post(url, json=payload)
        
        db.session.commit()
        return {'job_ids': job_ids}
