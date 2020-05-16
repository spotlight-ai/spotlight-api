from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.aws import generate_presigned_link
from core.decorators import authenticate_token
from db import db
from models.datasets.flat_file import FlatFileDatasetModel
from models.user import UserModel
from schemas.datasets.flat_file import FlatFileDatasetSchema

flat_file_schema = FlatFileDatasetSchema()


class FlatFileCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        datasets = FlatFileDatasetModel.query.all()
        return flat_file_schema.dump(datasets, many=True)
    
    @authenticate_token
    def post(self, user_id):
        """
        Generates a request to upload a new flat file. Returns a pre-signed S3 link for upload that is valid for
        a pre-determined amount of time.

        Note: This upload needs to be verified using the /dataset/verification endpoint.
        :param user_id: Currently logged in user ID
        :return: AWS S3 pre-signed upload link
        """
        try:
            request_body = request.get_json(force=True)
            
            # Upload Format: s3://{bucket}/{user_id}_{dataset}/{object_name}
            dataset_name = request_body['dataset_name']
            key = request_body['location']
            object_name = f'{user_id}_{dataset_name}/{key}'
            
            request_body['uploader'] = user_id
            request_body['location'] = object_name
            
            dataset = flat_file_schema.load(request_body)
            owner = UserModel.query.get(user_id)
            
            dataset.owners.append(owner)
            db.session.add(dataset)
            
            db.session.commit()
            
            response = generate_presigned_link(bucket_name='uploaded-datasets',
                                               object_name=object_name)
            response['dataset_id'] = dataset.dataset_id
            return response
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
