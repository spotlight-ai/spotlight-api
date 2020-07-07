from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.decorators import authenticate_token
from db import db
from models.pii.snake_case import PIIColumnar
from schemas.pii.snake_case import PIIColumnarSchema

columnar_file_pii_schema = PIIColumnarSchema()

class SnakeCasePII(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        pii = PIIColumnar.query.filter_by(dataset_id=dataset_id).all()
        return columnar_file_pii_schema.dump(pii, many=True)

class SnakeCasePIICollection(Resource):
    @authenticate_token
    def post(self, user_id):
        try:
            data = request.get_json(force=True)
            columnar_file_pii = columnar_file_pii_schema.load(data)

            db.session.add(columnar_file_pii)
            db.session.commit()
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
        return        