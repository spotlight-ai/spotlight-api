import os
from loguru import logger

from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse

from core.constants import SupportedFiles
from core.decorators import authenticate_token
from core.errors import DatasetErrors
from db import db
from models.datasets.base import DatasetModel
from models.pii.marker_character import PIIMarkerCharacterModel
from models.pii.marker_image import PIIMarkerImageModel
from models.datasets.file import FileModel
from schemas.pii.marker_character import PIIMarkerCharacterSchema
from schemas.pii.marker_image import PIIMarkerImageSchema

pii_marker_character_schema = PIIMarkerCharacterSchema()
pii_marker_image_schema = PIIMarkerImageSchema()



class FilePIICollection(Resource):
    @authenticate_token
    def post(self, user_id, file_id):
        """
        Associate a PII marker with a file onboarded to the Spotlight platform.

        :user_id: User ID of requesting user.
        :file_id: File identifier.
        :return: None
        """
        file = FileModel.query.filter_by(file_id=file_id).first()
        if not file:
            abort(404, "File not found.")

        markers: list = request.get_json(force=True)

        for marker in markers:
            marker["file_id"] = file_id

        filepath = urlparse(file.location).path[1:]
        _, ext = os.path.splitext(filepath)

        if ext in SupportedFiles.CHARACTER_BASED:
            logger.info(f"The markers we're trying to load: {markers}")
            file_pii = pii_marker_character_schema.load(markers, many=True)
        elif ext in SupportedFiles.IMAGE_BASED:
            file_pii = pii_marker_image_schema.load(markers, many=True)
        else:
            abort(400, "File extension not supported.")

        try:
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

        filepath = urlparse(file.location).path[1:]
        _, ext = os.path.splitext(filepath)

        def get_pii(model, schema):
            markers = model.query.filter_by(file_id=file_id).all()
            return schema.dump(markers, many=True)

        if ext in SupportedFiles.CHARACTER_BASED:
            pii = get_pii(model=PIIMarkerCharacterModel, schema=pii_marker_character_schema)
        elif ext in SupportedFiles.IMAGE_BASED:
            pii = get_pii(model=PIIMarkerImageModel, schema=pii_marker_image_schema)
        else:
            abort(400, "File extension not supported.")

        return pii

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
                _, ext = os.path.splitext(urlparse(file_object.location).path[1:])
                if ext in SupportedFiles.CHARACTER_BASED:
                    PIIMarkerCharacterModel.query.filter_by(pii_id=marker_id).delete()
                elif ext in SupportedFiles.IMAGE_BASED:
                    PIIMarkerImageModel.query.filter_by(pii_id=marker_id).delete()
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
            file_object = FileModel.query.filter_by(file_id=file_id).first()
            _, ext = os.path.splitext(urlparse(file_object.location).path[1:])
            if ext in SupportedFiles.CHARACTER_BASED:
                pii = PIIMarkerCharacterModel.query.filter_by(pii_id=marker_id).first()
            elif ext in SupportedFiles.IMAGE_BASED:
                pii = PIIMarkerImageModel.query.filter_by(pii_id=marker_id).first()
            
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
