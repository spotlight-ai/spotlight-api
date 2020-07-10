from flask import abort, request
from flask_restful import Resource

from core.constants import NotificationConstants
from core.decorators import authenticate_token
from db import db
from models.datasets.base import DatasetModel
from models.datasets.shared_user import SharedDatasetUserModel
from models.notifications.notification import NotificationModel
from models.pii.pii import PIIModel
from models.user import UserModel
from schemas.datasets.shared_user import SharedDatasetUserSchema

shared_dataset_user_schema = SharedDatasetUserSchema()


class DatasetSharedUserCollection(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        user = UserModel.query.filter_by(user_id=user_id).first()

        if user not in dataset.owners:
            abort(
                401,
                "User does not have permission to view users shared with this dataset.",
            )

        shared_users = SharedDatasetUserModel.query.filter(
            (SharedDatasetUserModel.dataset_id == dataset_id)
        ).all()

        return shared_dataset_user_schema.dump(shared_users, many=True)

    @authenticate_token
    def post(self, user_id, dataset_id):
        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        user = UserModel.query.filter_by(user_id=user_id).first()

        if user not in dataset.owners:
            abort(
                401,
                "User does not have permission to view users shared with this dataset.",
            )

        dataset_owner_ids = [user.user_id for user in dataset.owners]
        currently_shared_ids = [
            shared.user_id
            for shared in SharedDatasetUserModel.query.filter(
                SharedDatasetUserModel.dataset_id == dataset_id
            ).all()
        ]

        data = request.get_json(force=True)

        for user_object in data:
            if user_object.get("user_id") in dataset_owner_ids:
                abort(400, "Dataset cannot be shared with owner.")
            if user_object.get("user_id") in currently_shared_ids:
                abort(400, f"Dataset is already shared with user {user.email}")
            shared_user_object = SharedDatasetUserModel(
                user_id=user_object.get("user_id"), dataset_id=dataset.dataset_id
            )
            permission_objects = PIIModel.query.filter(
                (PIIModel.description.in_(user_object.get("permissions", [])))
            ).all()

            shared_user_object.permissions = permission_objects
            permission_long_descriptions = [
                perm.long_description for perm in permission_objects
            ]

            db.session.add(shared_user_object)

            # Add notification for shared user
            notification = NotificationModel(
                user_id=shared_user_object.user_id,
                title=NotificationConstants.DATASET_SHARED_TITLE,
                detail=f"{NotificationConstants.DATASET_SHARED_DETAIL} {dataset.dataset_name}",
            )
            notification.send_notification_email(permission_long_descriptions)

            db.session.add(notification)

        db.session.commit()

        return None, 201

    @authenticate_token
    def put(self, user_id, dataset_id):
        pass

    @authenticate_token
    def delete(self, user_id, dataset_id):
        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()
        user = UserModel.query.filter_by(user_id=user_id).first()

        if user not in dataset.owners:
            abort(
                401,
                "User does not have permission to view users shared with this dataset.",
            )

        data = request.get_json(force=True)

        currently_shared_ids = [
            shared.user_id
            for shared in SharedDatasetUserModel.query.filter(
                SharedDatasetUserModel.dataset_id == dataset_id
            ).all()
        ]

        for user_object in data:
            deleted_user_id = user_object.get("user_id")
            if deleted_user_id not in currently_shared_ids:
                abort(
                    400, f"User {deleted_user_id} does not have access to the dataset."
                )

            SharedDatasetUserModel.query.filter(
                (SharedDatasetUserModel.dataset_id == dataset.dataset_id)
                & (SharedDatasetUserModel.user_id == deleted_user_id)
            ).delete()

        db.session.commit()

        return None, 204
