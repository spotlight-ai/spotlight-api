from flask_restful import Resource
from flask import request, abort
from schemas.datasets.flat_file import FlatFileDatasetSchema
from schemas.datasets.dataset_owner import DatasetOwnerSchema
from models.datasets.flat_file import FlatFileDatasetModel
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from db import db
from core.decorators import authenticate_token
from core.aws import generate_presigned_link

flat_file_schema = FlatFileDatasetSchema()
dataset_owner_schema = DatasetOwnerSchema()



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
            request_body['uploader'] = user_id

            dataset = flat_file_schema.load(request_body)
            db.session.add(dataset)
            db.session.flush()
            db.session.refresh(dataset)

            # Create a record in the DatasetOwner table
            dataset_id_data = {'dataset_id': dataset.dataset_id, 'owner_id': user_id}
            dataset_owner = dataset_owner_schema.load(dataset_id_data, session=db.session)
            db.session.add(dataset_owner)

            db.session.commit()

            response = generate_presigned_link(bucket_name='uploaded-datasets',
                                                     object_name=request_body['location'])
            response['dataset_id'] = dataset.dataset_id
            return response
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
