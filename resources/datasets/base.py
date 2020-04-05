from flask_restful import Resource
from flask import request, abort
from schemas.datasets.base import DatasetSchema
from models.datasets.base import DatasetModel
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from db import db
from core.decorators import authenticate_token

dataset_schema = DatasetSchema()


class DatasetCollection(Resource):
    def get(self):
        datasets = DatasetModel.query.all()
        return dataset_schema.dump(datasets, many=True)


class DatasetVerification(Resource):
    @authenticate_token
    def post(self, user_id):
        request_body = request.get_json(force=True)
        dataset_id = request_body['dataset_id']

        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        dataset.verified = True
        db.session.commit()
        return