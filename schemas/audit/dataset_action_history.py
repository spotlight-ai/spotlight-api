from db import ma
from models.audit.dataset_action_history import DatasetActionHistoryModel


class DatasetActionHistorySchema(ma.ModelSchema):
    class Meta:
        model = DatasetActionHistoryModel
        include_fk = True
        dump_only = ("timestamp",)
