from flask import abort, request
from flask_restful import Resource

from core.decorators import authenticate_token
from core.errors import DatasetErrors, RoleErrors
from db import db
from models.user import UserModel
from resources.datasets.util import retrieve_datasets
from resources.roles.util import retrieve_role
from schemas.datasets.flat_file import FlatFileDatasetSchema
from schemas.roles.role import RoleSchema

flat_file_schema = FlatFileDatasetSchema()
role_schema = RoleSchema()


class RoleDatasetCollection(Resource):
    @authenticate_token
    def get(self, user_id, role_id):
        """
        Retrieves all datasets that a Role has access to (as long as the requester owns the Role.
        :param user_id: Currently logged in user ID.
        :param role_id: Role being requested.
        :return: List of datasets.
        """
        role = retrieve_role(user_id=user_id, role_id=role_id)
        return flat_file_schema.dump(role.datasets, many=True)
    
    @authenticate_token
    def post(self, user_id, role_id):
        """
        Adds datasets to a Role and allows Role Members to access those datasets.
        :param user_id: Currently logged in user ID.
        :param role_id: Role to be updated,
        :return: None
        """
        role = retrieve_role(user_id=user_id, role_id=role_id)
        
        data = request.get_json(force=True)
        datasets = retrieve_datasets(data.get('datasets', []))
        
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        for dataset in datasets:
            if dataset in role.datasets:
                abort(400, f'{dataset.dataset_id}: {RoleErrors.DATASET_ALREADY_PRESENT}')
            
            if user not in dataset.owners:
                abort(401, f'{dataset.dataset_id}: {DatasetErrors.USER_DOES_NOT_OWN}')
        
        role.datasets.extend(datasets)
        
        db.session.commit()
        return None, 201
    
    @authenticate_token
    def put(self, user_id, role_id):
        """
        Replaces the datasets that a Role may access.
        :param user_id: Currently logged in user ID.
        :param role_id: Role to be updated.
        :return: Role object
        """
        role = retrieve_role(role_id=role_id, user_id=user_id)
        
        data = request.get_json(force=True)
        datasets = retrieve_datasets(data.get('datasets', []))
        
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        for dataset in datasets:
            if user not in dataset.owners:
                abort(401, f'{dataset.dataset_id}: {DatasetErrors.USER_DOES_NOT_OWN}')
        
        role.datasets = datasets
        
        return role_schema.dump(role)
    
    @authenticate_token
    def delete(self, user_id, role_id):
        """
        Removes datasets from a Role.
        :param user_id: Currently logged in user ID.
        :param role_id: Role to be updated.
        :return: Role object
        """
        role = retrieve_role(user_id=user_id, role_id=role_id)
        
        data = request.get_json(force=True)
        datasets = retrieve_datasets(data.get('datasets', []))
        
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        for dataset in datasets:
            if user not in dataset.owners:
                abort(401, f'{dataset.dataset_id}: {DatasetErrors.USER_DOES_NOT_OWN}')
            if dataset not in role.datasets:
                abort(400, f'{dataset.dataset_id}: {RoleErrors.DATASET_NOT_PRESENT}')
            role.datasets.remove(dataset)
        
        return role_schema.dump(role)
