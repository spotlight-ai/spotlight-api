from db import ma
from models.datasets.base import DatasetModel


class DatasetSchema(ma.ModelSchema):
    class Meta:
        model = DatasetModel