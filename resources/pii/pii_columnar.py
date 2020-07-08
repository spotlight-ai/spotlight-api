from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.decorators import authenticate_token
from db import db
from models.pii.pii_columnar import ColumnarPIIModel
from schemas.pii.pii_columnar import ColumnarPIISchema

columnar_file_pii_schema = ColumnarPIISchema()

class ColumnarPII(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        pii = ColumnarPIIModel.query.filter_by(dataset_id=dataset_id).all()
        return columnar_file_pii_schema.dump(pii, many=True)

class ColumnarPIICollection(Resource):
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
            