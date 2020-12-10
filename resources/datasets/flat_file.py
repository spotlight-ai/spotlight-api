from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.aws import generate_presigned_link
from core.constants import AuditConstants
from core.decorators import authenticate_token
from db import db
from models.audit.dataset_action_history import DatasetActionHistoryModel
from models.auth.user import UserModel
from models.datasets.flat_file import FlatFileDatasetModel
from schemas.datasets.flat_file import FlatFileDatasetSchema
from schemas.datasets.base import DatasetSchema

from loguru import logger

flat_file_schema = FlatFileDatasetSchema()
dataset_schema = DatasetSchema()


class FlatFileCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        datasets = FlatFileDatasetModel.query.all()
        return flat_file_schema.dump(datasets, many=True)

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
            location_body = request_body.get("location")

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

                flat_file_dataset = flat_file_schema.load(
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
