from flask import abort, request
from flask_restful import Resource

from core.decorators import authenticate_token
from db import db
from models.datasets.base import DatasetModel
from models.datasets.shared_user import SharedDatasetUserModel
from models.user import UserModel
from schemas.datasets.shared_user import SharedDatasetUserSchema

shared_dataset_user_schema = SharedDatasetUserSchema()


class DatasetSharedUserCollection(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        if user not in dataset.owners:
            abort(401, 'User does not have permission to view users shared with this dataset.')
        
        shared_users = SharedDatasetUserModel.query.filter((SharedDatasetUserModel.dataset_id == dataset_id)).all()
        
        return shared_dataset_user_schema.dump(shared_users, many=True)
    
    @authenticate_token
    def post(self, user_id, dataset_id):
        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        if user not in dataset.owners:
            abort(401, 'User does not have permission to view users shared with this dataset.')
        
        data = request.get_json(force=True)
        
        shared_user_ids = data.get('users', [])
        
        shared_users = UserModel.query.filter(UserModel.user_id.in_(shared_user_ids)).all()
        currently_shared = [shared.user_id for shared in
                            SharedDatasetUserModel.query.filter(SharedDatasetUserModel.dataset_id == dataset_id).all()]
        
        for user in shared_users:
            if user in dataset.owners:
                abort(400, 'Dataset cannot be shared with owner.')
            if user.user_id in currently_shared:
                abort(400, f'Dataset is already shared with user {user.email}')
            
            db.session.add(SharedDatasetUserModel(user_id=user.user_id, dataset_id=dataset.dataset_id))
        
        db.session.commit()
        
        return None, 201
