from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.decorators import authenticate_token
from db import db
from models.pii.text_file import TextFilePIIModel
from schemas.pii.text_file import TextFilePIISchema

text_file_pii_schema = TextFilePIISchema()


class TextFilePIICollection(Resource):
    @authenticate_token
    def post(self, user_id):
        try:
            data = request.get_json(force=True)
            text_file_pii = text_file_pii_schema.load(data)

            db.session.add(text_file_pii)
            db.session.commit()
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
        return


class TextFilePII(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        pii = TextFilePIIModel.query.filter_by(dataset_id=dataset_id).all()
        return text_file_pii_schema.dump(pii, many=True)
