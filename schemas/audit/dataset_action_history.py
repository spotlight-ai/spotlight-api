from db import ma
from models.audit.dataset_action_history import DatasetActionHistoryModel


class DatasetActionHistorySchema(ma.Schema):
    class Meta:
        model = DatasetActionHistoryModel
