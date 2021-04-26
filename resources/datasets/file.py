import typing
from urllib.parse import urlparse
import os

from flask import abort, request
from flask_restful import Resource
from loguru import logger
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.aws import generate_presigned_download_link, generate_presigned_link, generate_upload_filepath
from core.constants import AuditConstants
from core.decorators import authenticate_token
from core.errors import FileErrors
from db import db
from models.audit.dataset_action_history import DatasetActionHistoryModel
from models.auth.user import UserModel
from models.datasets.base import DatasetModel
from models.datasets.file import FileModel
from resources.datasets import util as dataset_util
from models.pii.marker_character import PIIMarkerCharacterModel
from models.pii.marker_image import PIIMarkerImageModel
from schemas.datasets.base import DatasetSchema
from schemas.datasets.file import FileSchema
from schemas.pii.marker_image import PIIMarkerImageSchema
from schemas.pii.marker_character import PIIMarkerCharacterSchema
from core.constants import SupportedFiles

file_schema = FileSchema()
dataset_schema = DatasetSchema()


class FlatFileCollection(Resource):
    @authenticate_token
    def post(self, user_id) -> None:
        """
        Generates a request to upload a new flat file. Returns a pre-signed S3 link for upload that is valid for
        a pre-determined amount of time.

        Note: This upload needs to be verified using the /dataset/verification endpoint.
        :param user_id: Currently logged in user ID
        :return: AWS S3 pre-signed upload link
        """
        try:
            request_body: dict = request.get_json(force=True)
            
            dataset_name: str = request_body.get("dataset_name")
            location_body = request_body.get("locations")
            
            locations: list = location_body if type(location_body) == list else [
                {"name": location_body}]
            
            # Create dataset object to store in database
            dataset_body: dict = {
                "dataset_name": dataset_name,
                "dataset_type": "FLAT_FILE",
                "uploader": user_id,
                "verified": False
            }
            
            logger.info(f"Dataset Name: {dataset_name}")
            logger.info(f"Locations: {locations}")
            
            dataset = dataset_schema.load(dataset_body)
            owner: UserModel = UserModel.query.get(user_id)
            
            dataset.owners.append(owner)
            db.session.add(dataset)
            db.session.commit()
            
            # Generate a series of presigned links for each location
            response_urls: list = []
            dataset_id = dataset.dataset_id

            for location in locations:
                object_name = location.get('name')
                
                flat_file_body: dict = {
                    "dataset_id": dataset_id,
                    "location": generate_upload_filepath(dataset_id, object_name)
                }
                flat_file_dataset = file_schema.load(
                    flat_file_body, session=db.session)
                
                db.session.add(flat_file_dataset)
                
                response = generate_presigned_link(dataset_id, object_name=object_name)
                response["dataset_id"] = dataset_id
                response_urls.append(response)
                
                db.session.add(DatasetActionHistoryModel(
                    user_id=user_id, dataset_id=dataset.dataset_id, action=AuditConstants.DATASET_CREATED))
            
            db.session.commit()
            
            logger.info(f"Response: {response_urls}")
            
            return response_urls
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)


class File(Resource):
    """
    Resource for manipulating a single File resource.
    """
    @authenticate_token
    def get(self, user_id: int, dataset_id: int, file_id: int) -> dict:
        """
        Retrieves file object and generates pre-signed link if user requesting has access.
        :param user_id: User ID requesting the file object
        :param dataset_id: Dataset ID that the file belongs to
        :param file_id: Unique file identifier
        :return: File object
        """
        file: typing.Optional[FileModel] = None
        dataset: typing.Optional[DatasetModel] = None

        try:
            file: FileModel = dataset_util.retrieve_file(file_id, dataset_id)
            dataset: DatasetModel = dataset_util.retrieve_dataset(dataset_id)
        except ValueError as e:
            logger.error(e.args)
            abort(404, e.args[0])
        
        # Determine if the user requesting is an owner
        is_owner: bool = dataset_util.check_dataset_ownership(dataset, user_id)

        markers: list = file.markers
        filepath: str = urlparse(file.location).path[1:]
        _, ext = os.path.splitext(filepath)
        
        if is_owner:
            permissions: list = [marker.pii_type for marker in markers]
        else:
            is_shared, roles = dataset_util.check_dataset_role_permissions(dataset_id, user_id)

            if not is_shared:
                abort(401, FileErrors.DOES_NOT_HAVE_PERMISSION)

            perm_list: list = []
            for role in roles:
                perm_list.extend(role.permissions)

            permissions: list = [{x.description for x in perm_list}]

        if ext in SupportedFiles.CHARACTER_BASED:
            markers = PIIMarkerCharacterModel.query.filter_by(file_id=file_id).all()
        elif ext in SupportedFiles.IMAGE_BASED:
            markers = PIIMarkerImageModel.query.filter_by(file_id=file_id).all()
        else:
            abort(400, "File extension not supported.")

        logger.debug(markers)
        logger.debug(permissions)

        file.location, file.markers = generate_presigned_download_link(filepath=filepath, markers=markers,
                                                                       permissions=permissions)

        logger.debug(file.markers)

        return file_schema.dump(file)

