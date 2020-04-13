from distutils.util import strtobool

from flask import request
from flask_restful import Resource

from core.decorators import authenticate_token
from db import db
from models.datasets.base import DatasetModel
from schemas.datasets.base import DatasetSchema
from schemas.job import JobSchema

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
        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        return dataset_schema.dump(dataset)


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
        
        for dataset in datasets:
            if not dataset.verified:
                # TODO: Add S3 verification.
                # TODO: Add API call to model API to run job that is created.
                # TODO: Add Kafka messaging queue implementation for job queueing.
                job = job_schema.load({ 'dataset_id': dataset.dataset_id })
                db.session.add(job)
                dataset.verified = True
        
        db.session.commit()
        return
