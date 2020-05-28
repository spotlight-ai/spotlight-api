from flask import abort, request
from flask_restful import Resource

from core.decorators import authenticate_token
from db import db
from models.datasets.flat_file import FlatFileDatasetModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel
from models.user import UserModel
from schemas.datasets.flat_file import FlatFileDatasetSchema
from schemas.roles.role import RoleSchema

flat_file_schema = FlatFileDatasetSchema()
role_schema = RoleSchema()


class RoleDatasetCollection(Resource):
    @authenticate_token
    def get(self, user_id, role_id):
        role = RoleModel.query.filter((RoleModel.role_id == role_id) & (RoleMemberModel.user_id == user_id) & (
                RoleMemberModel.is_owner == True)).first()
        
        if not role:
            abort(401, "Role either does not exist or user does not have permissions")
        
        return flat_file_schema.dump(role.datasets, many=True)
    
    @authenticate_token
    def post(self, user_id, role_id):
        role = RoleModel.query.filter((RoleModel.role_id == role_id) & (RoleMemberModel.user_id == user_id) & (
                RoleMemberModel.is_owner == True)).first()
        
        if not role:
            abort(401, "Role either does not exist or user does not have permissions")
        
        data = request.get_json(force=True)
        
        dataset_ids = data.get('datasets', [])
        datasets = FlatFileDatasetModel.query.filter((FlatFileDatasetModel.dataset_id.in_(dataset_ids))).all()
        
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        for dataset in datasets:
            if dataset in role.datasets:
                abort(400, f'Dataset {dataset} already present in role.')
            
            if user not in dataset.owners:
                abort(401, "User does not own one or more of these datasets.")
            
            role.datasets.append(dataset)
        
        db.session.commit()
        return None, 201
    
    @authenticate_token
    def put(self, user_id, role_id):
        role = RoleModel.query.filter((RoleModel.role_id == role_id) & (RoleMemberModel.user_id == user_id) & (
                RoleMemberModel.is_owner == True)).first()
        
        if not role:
            abort(401, "Role either does not exist or user does not have permissions")
        
        data = request.get_json(force=True)
        dataset_ids = data.get('datasets', [])
        datasets = FlatFileDatasetModel.query.filter((FlatFileDatasetModel.dataset_id.in_(dataset_ids))).all()
        
        user = UserModel.query.filter_by(user_id=user_id).first()
        for dataset in datasets:
            if user not in dataset.owners:
                abort(401, "User does not own one or more of these datasets.")
        
        role.datasets = datasets
        
        return role_schema.dump(role)
    
    @authenticate_token
    def delete(self, user_id, role_id):
        role = RoleModel.query.filter((RoleModel.role_id == role_id) & (RoleMemberModel.user_id == user_id) & (
                RoleMemberModel.is_owner == True)).first()
        
        if not role:
            abort(401, "Role either does not exist or user does not have permissions")
        
        data = request.get_json(force=True)
        dataset_ids = data.get('datasets', [])
        datasets = FlatFileDatasetModel.query.filter((FlatFileDatasetModel.dataset_id.in_(dataset_ids))).all()
        
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        for dataset in datasets:
            if user not in dataset.owners:
                abort(401, "User does not own one or more of these datasets.")
            if dataset not in role.datasets:
                abort(400, f"Dataset {dataset} not present in the role.")
            role.datasets.remove(dataset)
        
        return role_schema.dump(role)
