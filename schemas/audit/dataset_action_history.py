from db import ma
from models.audit.dataset_action_history import DatasetActionHistoryModel
from schemas.user import UserSchema
from schemas.datasets.base import DatasetSchema


class DatasetActionHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DatasetActionHistoryModel
        dump_only = ("timestamp",)

    user = ma.Nested(UserSchema)
    dataset = ma.Nested(DatasetSchema)
