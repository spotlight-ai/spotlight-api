from db import ma
from models.datasets.base import DatasetModel


class DatasetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = DatasetModel
        include_fk = True
        load_instance = True
        exclude = ("dataset_action_history",)

    jobs = ma.List(ma.Nested("JobSchema"))
    markers = ma.List(ma.Nested("PIIMarkerSchema"))
    owners = ma.List(ma.Nested("UserSchema", exclude=["owned_datasets"]))
    files = ma.List(ma.Nested("FileSchema"))
    roles = ma.List(ma.Nested("RoleSchema", exclude=["datasets", "creator"]))
