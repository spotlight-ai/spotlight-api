import os
from urllib.parse import urlparse

import requests
from flask import abort, request
from flask_restful import Resource
from sqlalchemy.sql.expression import true

from core.aws import dataset_cleanup, generate_presigned_download_link
from core.constants import AuditConstants
from core.decorators import authenticate_token
from core.errors import DatasetErrors, UserErrors
from db import db
from models.associations import RoleDataset, RolePermission, UserDatasetPermission
from models.audit.dataset_action_history import DatasetActionHistoryModel
from models.auth.user import UserModel
from models.datasets.base import DatasetModel
from models.datasets.file import FileModel
from models.datasets.shared_user import SharedDatasetUserModel
from models.job import JobModel
from models.pii.pii import PIIModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel
from schemas.datasets.base import DatasetSchema
from schemas.datasets.file import FileSchema
from schemas.job import JobSchema

flat_file_dataset_schema = FileSchema()
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
        owned_datasets = DatasetModel.query.filter(
            DatasetModel.verified == true(),
            DatasetModel.owners.contains(logged_in_user),
        ).all()
        
        owned_datasets_json = dataset_schema.dump(owned_datasets, many=True)
        owned_dataset_ids = [
            dataset.get("dataset_id") for dataset in owned_datasets_json
        ]
        for dataset in owned_datasets_json:
            dataset["permission"] = "owned"
        all_datasets.extend(owned_datasets_json)
        
        # Retrieve datasets the user may access via role permissions
        shared_by_role = (
            DatasetModel.query.join(RoleDataset)
                .join(RoleModel)
                .join(RoleMemberModel)
                .filter(RoleMemberModel.user_id == user_id)
        )
        
        # Retrieve datasets the user may access via individual permissions/sharing
        shared_by_user = DatasetModel.query.join(SharedDatasetUserModel).filter(
            SharedDatasetUserModel.user_id == user_id
        )
        
        shared = shared_by_role.union(shared_by_user).distinct()
        
        shared_json = dataset_schema.dump(shared, many=True)
        for dataset in shared_json:
            if dataset.get("dataset_id") not in owned_dataset_ids:
                dataset["permission"] = "shared"
                all_datasets.append(dataset)
        
        return all_datasets


class Dataset(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        
        if not dataset:
            abort(404, "Dataset not found")
        
        # TODO: Add code to check for role permissions
        is_owner = user_id in {owner.user_id for owner in dataset.owners}
        
        if is_owner or user_id == "MODEL":
            return dataset_schema.dump(dataset)
        else:
            abort(401, "This user is not authorized to view this dataset")
        
        ## Below is deprecated
        
        # args = request.args
        # masked = f'{args.get("masked", "false")}'
        # if masked.lower() == "true":
        #     masked = True
        # else:
        #     masked = False
        
        # if user_id != "MODEL":  # User is requesting
            
        #     # Check if any job related to this dataset is PENDING or Failed in which case we can't reveal the dataset.
        #     jobs = JobModel.query.filter(JobModel.dataset_id == dataset_id).all()
        #     jobs_json = job_schema.dump(jobs, many=True)
            
        #     for job in jobs_json:
        #         if job.get("job_status", "").lower() in ["pending", "failed"]:
        #             if base_dataset.dataset_type == "FLAT_FILE":
        #                 dataset = FileModel.query.filter_by(
        #                     dataset_id=dataset_id
        #                 ).first()
        #                 dataset.download_link, dataset.dataset.markers = None, []
        #             return flat_file_dataset_schema.dump(dataset)
            
        #     user = UserModel.query.filter_by(user_id=user_id).first()
            
        #     if not base_dataset:
        #         abort(404, "Dataset not found")
            
        #     owned = user in base_dataset.owners
        #     shared = (
        #         True
        #         if SharedDatasetUserModel.query.filter_by(
        #             dataset_id=dataset_id, user_id=user_id
        #         ).first()
        #         else False
        #     )
        #     role_ids = []
            
        #     if (
        #             not shared
        #     ):  # Check for role sharing if it hasn't been shared individually
        #         for role in base_dataset.roles:
        #             for member in role.members:
        #                 if member.user_id == user_id:
        #                     shared = True
        #                     role_ids.append(role.role_id)
        #                     break
            
        #     if not shared and not owned:
        #         abort(401, "This user is not authorized to view this dataset")
            
        #     individual_permissions = (
        #         PIIModel.query.join(UserDatasetPermission)
        #             .join(SharedDatasetUserModel)
        #             .filter_by(dataset_id=dataset_id, user_id=user_id)
        #     )
            
        #     role_permissions = (
        #         PIIModel.query.join(RolePermission)
        #             .join(RoleModel)
        #             .filter(RoleModel.role_id.in_(role_ids))
        #     )
        #     permissions = individual_permissions.union(role_permissions).all()
            
        #     markers = FilePIIModel.query.filter_by(dataset_id=dataset_id).all()
        # else:  # Model is requesting
        #     owned = True
        #     shared = False
        #     permissions = []
        #     markers = []
        
        if base_dataset.dataset_type == "FLAT_FILE":
            flat_files = FileModel.query.filter_by(dataset_id=dataset_id).all()
            
            for file in flat_files:
                parsed_path = urlparse(file.location)
                s3_object_key = parsed_path.path[1:]
                
                if owned:
                    file.download_link, _ = generate_presigned_download_link("uploaded-datasets", s3_object_key)
                elif shared:
                    file.download_link, modified_markers = generate_presigned_download_link(
                        "spotlightai-redacted-copies", s3_object_key, permissions=permissions, markers=markers,
                        mask=masked)
                    
                    new_markers = []
                    permission_descriptions = set([perm.description for perm in permissions])
                    
                    if modified_markers:
                        for marker in modified_markers:
                            if marker.pii_type in permission_descriptions:
                                new_markers.append(marker)
                    else:
                        for marker in file.dataset.markers:
                            if marker.pii_type in permission_descriptions:
                                new_markers.append(marker)
                    
                    file.markers = new_markers
                
                return flat_file_dataset_schema.dump(file, many=True)
        return
    
    @authenticate_token
    def put(self, user_id, dataset_id):
        data = request.get_json(force=True)
        owner_ids = data.get("owners", [])
        
        if len(owner_ids) == 0:
            abort(400, DatasetErrors.MUST_HAVE_OWNER)
        
        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        if user not in dataset.owners:
            abort(400, DatasetErrors.USER_DOES_NOT_OWN)
        
        owners = UserModel.query.filter(UserModel.user_id.in_(owner_ids)).all()
        
        if len(owners) == 0:
            abort(400, UserErrors.USER_NOT_FOUND)
        
        dataset.owners = owners
        db.session.commit()
        
        return flat_file_dataset_schema.dump(dataset)
    
    @authenticate_token
    def delete(self, user_id, dataset_id):
        """
        Deletes a dataset from the system.
        :param user_id: Currently logged in user ID.
        :param dataset_id: Dataset unique identifier to delete
        :return: None
        """
        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        
        if not dataset:
            abort(404, DatasetErrors.DOES_NOT_EXIST)
        
        owner_ids = [o.user_id for o in dataset.owners]
        
        if user_id not in owner_ids:
            abort(401, DatasetErrors.USER_DOES_NOT_OWN)
        
        flat_files = FileModel.query.filter_by(dataset_id=dataset_id).all()
        
        for file in flat_files:
            dataset_cleanup(file.location)
        
        DatasetModel.query.filter_by(dataset_id=dataset_id).delete()
        
        db.session.commit()
        return None, 202


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
        dataset_ids = request_body["dataset_ids"]
        
        datasets = DatasetModel.query.filter(
            DatasetModel.dataset_id.in_(dataset_ids)
        ).all()
        
        job_ids = []
        
        for dataset in datasets:
            if not dataset.verified:
                # TODO: Add S3 verification.
                # TODO: Add API call to model API to run job that is created.
                # TODO: Add Kafka messaging queue implementation for job queueing.
                job = job_schema.load({"dataset_id": dataset.dataset_id})
                db.session.add(job)
                dataset.verified = True
                
                db.session.flush()
                db.session.refresh(job)
                
                db.session.commit()
                
                url = f'http://{os.getenv("MODEL_HOST")}:{os.getenv("MODEL_PORT")}/predict/file'
                payload = {"job_id": job.job_id}
                
                job_ids.append(job.job_id)
                requests.post(url, json=payload)
                db.session.add(
                    DatasetActionHistoryModel(
                        user_id=user_id,
                        dataset_id=dataset.dataset_id,
                        action=AuditConstants.DATASET_VERIFIED,
                    )
                )
        
        db.session.commit()
        return {"job_ids": job_ids}
