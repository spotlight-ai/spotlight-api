import os
from urllib.parse import urlparse

import requests
from flask import abort, request
from flask_restful import Resource
from sqlalchemy.sql.expression import true

from core.aws import generate_presigned_download_link
from core.decorators import authenticate_token
from db import db
from models.associations import RoleDataset, RolePermission, UserDatasetPermission
from models.datasets.base import DatasetModel
from models.datasets.flat_file import FlatFileDatasetModel
from models.datasets.shared_user import SharedDatasetUserModel
from models.pii.pii import PIIModel
from models.pii.text_file import TextFilePIIModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel
from models.user import UserModel
from schemas.datasets.base import DatasetSchema
from schemas.datasets.flat_file import FlatFileDatasetSchema
from schemas.job import JobSchema

flat_file_dataset_schema = FlatFileDatasetSchema()
dataset_schema = DatasetSchema()
job_schema = JobSchema()


class DatasetCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        """
        Returns a list of datasets that are owned by and shared with the currently logged in user.

        Note: This will only return datasets that have been verified.

        :param user_id: Currently logged in user ID
        :return: List of datasets
        """
        logged_in_user = UserModel.query.filter_by(user_id=user_id).first()
        
        all_datasets = []
        
        # Retrieve all datasets that the user owns
        owned_datasets = DatasetModel.query.filter(DatasetModel.verified == true(),
                                                   DatasetModel.owners.contains(logged_in_user)).all()
        
        owned_datasets_json = dataset_schema.dump(owned_datasets, many=True)
        for dataset in owned_datasets_json:
            dataset['permission'] = 'owned'
        all_datasets.extend(owned_datasets_json)
        
        # Retrieve datasets the user may access via role permissions
        shared_by_role = DatasetModel.query.join(RoleDataset).join(RoleModel).join(RoleMemberModel).filter(
            RoleMemberModel.user_id == user_id)
        
        # Retrieve datasets the user may access via individual permissions/sharing
        shared_by_user = DatasetModel.query.join(SharedDatasetUserModel).filter(
            SharedDatasetUserModel.user_id == user_id)
        
        shared = shared_by_role.union(shared_by_user).all()
        
        shared_json = dataset_schema.dump(shared, many=True)
        for dataset in shared_json:
            dataset['permission'] = 'shared'
        all_datasets.extend(shared_json)
        
        return all_datasets


class Dataset(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        base_dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        if not base_dataset:
            abort(404, "Dataset not found")
        
        owned = user in base_dataset.owners
        shared = True if SharedDatasetUserModel.query.filter_by(dataset_id=dataset_id,
                                                                user_id=user_id).first() else False
        role_ids = []
        
        if not shared:  # Check for role sharing if it hasn't been shared individually
            for role in base_dataset.roles:
                for member in role.members:
                    if member.user_id == user_id:
                        shared = True
                        role_ids.append(role.role_id)
                        break
        
        if not shared and not owned:
            abort(401, "This user is not authorized to view this dataset")
        
        individual_permissions = PIIModel.query.join(UserDatasetPermission).join(SharedDatasetUserModel).filter_by(
            dataset_id=dataset_id,
            user_id=user_id)
        
        role_permissions = PIIModel.query.join(RolePermission).join(RoleModel).filter(RoleModel.role_id.in_(role_ids))
        permissions = individual_permissions.union(role_permissions).all()
        
        markers = TextFilePIIModel.query.filter_by(dataset_id=dataset_id).all()
        
        if base_dataset.dataset_type == "FLAT_FILE":
            dataset = FlatFileDatasetModel.query.filter_by(dataset_id=dataset_id).first()
            parsed_path = urlparse(dataset.location)
            s3_object_key = parsed_path.path[1:]
            if owned:
                dataset.download_link = generate_presigned_download_link('uploaded-datasets', s3_object_key)
            elif shared:
                dataset.download_link = generate_presigned_download_link('spotlightai-redacted-copies', s3_object_key,
                                                                         permissions=permissions, markers=markers)
            return flat_file_dataset_schema.dump(dataset)
        
        return


class DatasetVerification(Resource):
    @authenticate_token
    def post(self, user_id):
        """
        Verifies that a dataset has been uploaded. Accepts a list of dataset IDs that are to be verified, and checks
        dataset upload on AWS S3.

        :param user_id: Currently logged in user ID
        :return: None
        """
        request_body = request.get_json(force=True)
        dataset_ids = request_body['dataset_ids']
        
        datasets = DatasetModel.query.filter(DatasetModel.dataset_id.in_(dataset_ids)).all()
        
        job_ids = []
        
        for dataset in datasets:
            if not dataset.verified:
                # TODO: Add S3 verification.
                # TODO: Add API call to model API to run job that is created.
                # TODO: Add Kafka messaging queue implementation for job queueing.
                job = job_schema.load({'dataset_id': dataset.dataset_id})
                db.session.add(job)
                dataset.verified = True
                
                db.session.flush()
                db.session.refresh(job)
                
                db.session.commit()
                
                url = f'http://{os.getenv("MODEL_HOST")}:{os.getenv("MODEL_PORT")}/predict/file'
                payload = {'job_id': job.job_id}
                
                job_ids.append(job.job_id)
                requests.post(url, json=payload)
        
        db.session.commit()
        return {'job_ids': job_ids}
