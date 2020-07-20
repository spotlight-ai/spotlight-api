from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.constants import AuditConstants
from core.decorators import authenticate_token
from core.errors import DatasetErrors
from db import db
from models.audit.dataset_action_history import DatasetActionHistoryModel
from models.auth.user import UserModel
from models.datasets.flat_file import FlatFileDatasetModel
from schemas.datasets.flat_file import FlatFileDatasetSchema
from schemas.user import UserSchema

flat_file_schema = FlatFileDatasetSchema()
user_schema = UserSchema()


class DatasetOwners(Resource):
    @authenticate_token
    def get(self, user_id, dataset_id):
        dataset = FlatFileDatasetModel.query.filter(
            FlatFileDatasetModel.dataset_id == dataset_id
        ).first()
        if not dataset:
            abort(400, DatasetErrors.DOES_NOT_EXIST)

        owners = [owner.user_id for owner in dataset.owners]

        if user_id not in owners:
            abort(400, DatasetErrors.USER_DOES_NOT_OWN)

        return user_schema.dump(dataset.owners, many=True)

    @authenticate_token
    def post(self, user_id, dataset_id):
        try:
            dataset = FlatFileDatasetModel.query.filter(
                FlatFileDatasetModel.dataset_id == dataset_id
            ).first()

            if not dataset:
                abort(400, DatasetErrors.DOES_NOT_EXIST)

            existing_owners = [owner.user_id for owner in dataset.owners]

            if user_id not in existing_owners:
                abort(400, DatasetErrors.USER_DOES_NOT_OWN)

            new_owners_id = [
                user
                for user in request.get_json(force=True).get("owners", [])
                if user not in existing_owners
            ]

            if len(new_owners_id) > 0:
                new_owners = UserModel.query.filter(
                    UserModel.user_id.in_(new_owners_id)
                ).all()
                dataset.owners.extend(new_owners)

                db.session.commit()
            else:
                abort(400, DatasetErrors.NO_NEW_OWNERS)

            db.session.add(
                DatasetActionHistoryModel(
                    user_id=user_id,
                    dataset_id=dataset.dataset_id,
                    action=AuditConstants.DATASET_OWNERS_MODIFIED,
                    notes=f"Users with id {', '.join([str(id) for id in new_owners_id])} added as owners to the dataset.",
                )
            )
            db.session.commit()

            return flat_file_schema.dump(dataset)
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)

    @authenticate_token
    def put(self, user_id, dataset_id):
        try:
            dataset = FlatFileDatasetModel.query.filter(
                FlatFileDatasetModel.dataset_id == dataset_id
            ).first()

            if not dataset:
                abort(400, DatasetErrors.DOES_NOT_EXIST)

            existing_owners = [owner.user_id for owner in dataset.owners]

            if user_id not in existing_owners:
                abort(400, DatasetErrors.USER_DOES_NOT_OWN)

            new_owners_id = [
                user for user in request.get_json(force=True).get("owners", [])
            ]

            if len(new_owners_id) > 0:
                new_owners = UserModel.query.filter(
                    UserModel.user_id.in_(new_owners_id)
                ).all()
                dataset.owners = new_owners

                db.session.commit()
            else:
                abort(400, DatasetErrors.MUST_HAVE_OWNER)

            db.session.add(
                DatasetActionHistoryModel(
                    user_id=user_id,
                    dataset_id=dataset.dataset_id,
                    action=AuditConstants.DATASET_OWNERS_MODIFIED,
                    notes=f"Users with id {', '.join([str(id) for id in new_owners_id])} made owners of the dataset.",
                )
            )
            db.session.commit()

            return flat_file_schema.dump(dataset)
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)

    @authenticate_token
    def delete(self, user_id, dataset_id):
        try:
            dataset = FlatFileDatasetModel.query.filter(
                FlatFileDatasetModel.dataset_id == dataset_id
            ).first()

            if not dataset:
                abort(400, DatasetErrors.DOES_NOT_EXIST)

            existing_owners = [owner.user_id for owner in dataset.owners]

            if user_id not in existing_owners:
                abort(400, DatasetErrors.USER_DOES_NOT_OWN)

            owners_to_be_removed = request.get_json(force=True).get("owners", [])

            not_an_existing_owner = [
                user for user in owners_to_be_removed if user not in existing_owners
            ]

            if len(not_an_existing_owner) > 0:
                abort(
                    400,
                    (DatasetErrors.GIVEN_USERS_DO_NOT_OWN).format(
                        not_an_owner=", ".join(
                            [str(id) for id in not_an_existing_owner]
                        )
                    ),
                )

            dataset.owners = [
                owner
                for owner in dataset.owners
                if owner.user_id not in owners_to_be_removed
            ]

            db.session.commit()

            db.session.add(
                DatasetActionHistoryModel(
                    user_id=user_id,
                    dataset_id=dataset.dataset_id,
                    action=AuditConstants.DATASET_OWNERS_MODIFIED,
                    notes=f"Users with id {', '.join([str(id) for id in owners_to_be_removed])} removed as owners of the dataset.",
                )
            )
            db.session.commit()

            return flat_file_schema.dump(dataset)
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
