from flask_restful import Resource
from flask import request, abort
from schemas.datasets.base import DatasetSchema
from models.datasets.base import DatasetModel
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from distutils.util import strtobool

from db import db
from core.decorators import authenticate_token

dataset_schema = DatasetSchema()


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
            # TODO: Add S3 verification.
            dataset.verified = True

        db.session.commit()
        return
