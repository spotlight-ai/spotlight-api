from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.decorators import authenticate_token
from core.errors import DatasetErrors
from db import db
from models.datasets.base import DatasetModel
from models.pii.file import FilePIIModel
from models.datasets.file import FileModel
from schemas.pii.file import FilePIISchema

file_pii_schema = FilePIISchema()


class FilePIICollection(Resource):
    @authenticate_token
    def post(self, user_id, file_id):
        """
        Associate a PII marker with a file onboarded to the Spotlight platform.

        :user_id: User ID of requesting user.
        :file_id: File identifier.
        :return: None
        """
        try:
            markers: list = request.get_json(force=True)

            for marker in markers:
                marker["file_id"] = file_id

            file_pii = file_pii_schema.load(markers, many=True)

            for pii in file_pii:            
                db.session.add(pii)

            db.session.commit()
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
        return

    @authenticate_token
    def get(self, user_id: int, file_id: int):
        """
        Retrieve all PII associated with a file.

        :user_id: User ID of requesting user.
        :file_id: File identifier
        :return: List of PII markers associated with a file.
        """
        file = FileModel.query.filter_by(file_id=file_id).first()

        if not file:
            abort(404, "File not found.")

        pii = FilePIIModel.query.filter_by(file_id=file_id).all()
        return file_pii_schema.dump(pii, many=True)

class FilePII(Resource):
    @authenticate_token
    def delete(self, user_id, file_id, marker_id):
        """
        Deletes a PII marker from a file.

        :user_id: User ID of requesting user.
        :file_id: File identifier.
        :marker_id: PII marker identifier.
        """
        try:
            file_object = FileModel.query.filter_by(file_id=file_id).first()
            dataset = DatasetModel.query.filter_by(dataset_id=file_object.dataset_id).first()

            owners = [owner.user_id for owner in dataset.owners]
            
            if user_id not in owners:
                abort(400, DatasetErrors.USER_DOES_NOT_OWN)
            else:
                FilePIIModel.query.filter_by(pii_id=marker_id).delete()
                db.session.commit()
                return None, 200
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
        return
    
    @authenticate_token
    def put(self, user_id, file_id, marker_id):
        try:
            data = request.get_json(force=True)
            pii = FilePIIModel.query.filter_by(pii_id=marker_id).first()
            
            file_object = FileModel.query.filter_by(file_id=file_id).first()
            dataset = DatasetModel.query.filter_by(
                dataset_id=file_object.dataset_id
            ).first()
            owners = [owner.user_id for owner in dataset.owners]
            
            if user_id not in owners:
                abort(400, DatasetErrors.USER_DOES_NOT_OWN)
            else:
                pii.pii_type = data.get("pii_type", pii.pii_type)
                pii.start_location = data.get("start_location", pii.start_location)
                pii.end_location = data.get("end_location", pii.end_location)
                pii.confidence = data.get("confidence", pii.confidence)
                
                db.session.commit()
            
            return file_pii_schema.dump(pii)
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
        return
