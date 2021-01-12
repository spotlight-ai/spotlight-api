from db import ma
from models.datasets.base import DatasetModel
from schemas.datasets.file import FileSchema
from schemas.job import JobSchema
from schemas.pii.marker_base import PIIMarkerBaseSchema
from schemas.user import UserSchema


class DatasetSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = DatasetModel
        ordered = True
    
    jobs = ma.List(ma.Nested(JobSchema))
    markers = ma.List(ma.Nested(PIIMarkerBaseSchema))
    owners = ma.List(ma.Nested(UserSchema, exclude=["owned_datasets", "dataset_action_history"]))
    files = ma.List(ma.Nested(FileSchema, exclude=["dataset"]))
