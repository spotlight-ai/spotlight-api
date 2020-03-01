from flask_restful import Resource
from flask import request, abort
from schemas.datasets.flat_file import FlatFileDatasetSchema
from models.datasets.flat_file import FlatFileDatasetModel
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from db import db

flat_file_schema = FlatFileDatasetSchema()


class FlatFileCollection(Resource):
    def get(self):
        datasets = FlatFileDatasetModel.query.all()
        return flat_file_schema.dump(datasets, many=True)

    def post(self):
        try:
            data = flat_file_schema.load(request.get_json(force=True))
            db.session.add(data)
            db.session.commit()
            return
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
