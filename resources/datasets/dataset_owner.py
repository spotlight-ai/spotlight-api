from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from db import db
from models.datasets.dataset_owner import DatasetOwnerModel
from schemas.datasets.dataset_owner import DatasetOwnerSchema

dataset_owner_schema = DatasetOwnerSchema()


class DatasetOwnerCollection(Resource):
    
    def get(self):
        dataset_owner_records = DatasetOwnerModel.query.all()
        return dataset_owner_schema.dump(dataset_owner_records, many=True)
    
    def post(self):
        try:
            data = request.get_json(force=True)
            dataset_id = data['dataset_id']
            owner_id = data['owner_id']
            record = dataset_owner_schema.load(data, session=db.session)
            db.session.add(record)
            db.session.commit()
        
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
