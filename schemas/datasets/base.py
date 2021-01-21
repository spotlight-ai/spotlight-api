from db import ma
from models.datasets.base import DatasetModel
from schemas.datasets.file import FileSchema
from schemas.job import JobSchema
from schemas.pii.file import FilePIISchema
from schemas.roles.role import RoleSchema
from schemas.user import UserSchema


class DatasetSchema(ma.ModelSchema):
    class Meta:
        model = DatasetModel
        include_fk = True
        exclude = ("dataset_action_history",)

    jobs = ma.List(ma.Nested(JobSchema))
    markers = ma.List(ma.Nested(FilePIISchema))
    owners = ma.List(ma.Nested(UserSchema, exclude=["owned_datasets", "dataset_action_history"]))
    files = ma.List(ma.Nested(FileSchema, exclude=["dataset"]))
    roles = ma.List(ma.Nested(RoleSchema, exclude=["datasets", "creator"]))
