from flask_restful import Resource
from flask import request, abort
from schemas.datasets.flat_file import FlatFileDatasetSchema
from models.datasets.flat_file import FlatFileDatasetModel
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from db import db
from core.decorators import authenticate_token

flat_file_schema = FlatFileDatasetSchema()


class FlatFileCollection(Resource):
    def get(self):
        datasets = FlatFileDatasetModel.query.all()
        return flat_file_schema.dump(datasets, many=True)

    @authenticate_token
    def post(self, user_id):
        try:
            request_body = request.get_json(force=True)
            request_body['uploader'] = user_id

            dataset = flat_file_schema.load(request_body)
            db.session.add(dataset)
            db.session.commit()
            return
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)