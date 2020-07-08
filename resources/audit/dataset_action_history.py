from flask import abort
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.decorators import authenticate_token
from db import db
from models.audit.dataset_action_history import DatasetActionHistoryModel
from models.datasets.flat_file import FlatFileDatasetModel
from models.user import UserModel
from schemas.audit.dataset_action_history import DatasetActionHistorySchema
from schemas.datasets.flat_file import FlatFileDatasetSchema

flat_file_dataset_schema = FlatFileDatasetSchema()
dataset_action_history_schema = DatasetActionHistorySchema()


class DatasetActionHistoryCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        try:
            logged_in_user = UserModel.query.filter(
                UserModel.user_id == user_id
            ).first()

            owned_datasets = FlatFileDatasetModel.query.filter(
                FlatFileDatasetModel.owners.contains(logged_in_user),
            ).all()

            owned_dataset_id = [
                dataset.get("dataset_id")
                for dataset in flat_file_dataset_schema.dump(owned_datasets, many=True)
            ]

            if len(owned_dataset_id) == 0:
                return []
            else:
                owned_datasets_history = (
                    DatasetActionHistoryModel.query.filter(
                        DatasetActionHistoryModel.dataset_id.in_(owned_dataset_id)
                    )
                    .order_by(DatasetActionHistoryModel.timestamp.desc())
                    .all()
                )
                return dataset_action_history_schema.dump(
                    owned_datasets_history, many=True
                )

        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
