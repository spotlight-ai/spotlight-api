from urllib.parse import urlparse

from flask import abort, request
from flask_restful import Resource
from loguru import logger
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.aws import generate_presigned_download_link, generate_presigned_link
from core.constants import AuditConstants
from core.decorators import authenticate_token
from core.errors import FileErrors
from db import db
from models.audit.dataset_action_history import DatasetActionHistoryModel
from models.auth.user import UserModel
from models.datasets.base import DatasetModel
from models.datasets.file import FileModel
from models.pii.file import FilePIIModel
from schemas.datasets.base import DatasetSchema
from schemas.datasets.file import FileSchema
from schemas.pii.file import FilePIISchema

file_schema = FileSchema()
dataset_schema = DatasetSchema()
file_pii_schema = FilePIISchema()


class FlatFileCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        datasets = FileModel.query.all()
        return file_schema.dump(datasets, many=True)
    
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
            
            # Upload Format: s3://{bucket}/{user_id}_{dataset}/{object_name}
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
            
            for location in locations:
                object_name: str = f"{user_id}_{dataset_name}/{location.get('name')}"
                
                flat_file_body: dict = {
                    "dataset_id": dataset.dataset_id,
                    "location": object_name
                }
                
                flat_file_dataset = file_schema.load(
                    flat_file_body, session=db.session)
                
                db.session.add(flat_file_dataset)
                
                response = generate_presigned_link(
                    bucket_name="uploaded-datasets", object_name=object_name)
                response["dataset_id"] = dataset.dataset_id
                
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
    @authenticate_token
    def get(self, user_id: int, dataset_id: int, file_id: int) -> dict:
        """
        Retrieves file object and generates pre-signed link if user requesting has access.
        :param user_id: User ID requesting the file object
        :param dataset_id: Dataset ID that the file belongs to
        :param file_id: Unique file identifier
        :return: File object
        """
        file: FileModel = FileModel.query.filter_by(file_id=file_id, dataset_id=dataset_id).first()
        
        if not file:
            abort(404, FileErrors.FILE_NOT_FOUND)
        
        # Determine if the user requesting is an owner
        dataset: DatasetModel = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        is_owner: bool = user_id in {user.user_id for user in dataset.owners}
        
        if is_owner:
            # TODO: Need to add permissions for users who are shared the file.
            markers = FilePIIModel.query.filter_by(file_id=file_id).all()
            
            filepath: str = urlparse(file.location).path[1:]
            file.location, file.markers = generate_presigned_download_link(filepath=filepath, markers=markers,
                                                                           permissions=[])
            
            return file_schema.dump(file)
        
        # Throw an error if the user is not an owner of the dataset, or has not had this dataset shared
        abort(401, FileErrors.DOES_NOT_HAVE_PERMISSION)
