from flask_restful import Resource
from flask import request, abort
from schemas.datasets.base import DatasetSchema
from models.datasets.base import DatasetModel
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from db import db

dataset_schema = DatasetSchema()


class DatasetCollection(Resource):
    def get(self):
        datasets = DatasetModel.query.all()
        return dataset_schema.dump(datasets, many=True)
