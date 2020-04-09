from db import ma
from models.datasets.dataset_owner import DatasetOwnerModel


class DatasetOwnerSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = DatasetOwnerModel

