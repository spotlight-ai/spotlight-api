from db import ma
from models.datasets.base import DatasetModel
from schemas.job import JobSchema
from schemas.pii.text_file import TextFilePIISchema
from schemas.user import UserSchema


class DatasetSchema(ma.ModelSchema):
    class Meta:
        model = DatasetModel

    jobs = ma.List(ma.Nested(JobSchema))
    markers = ma.List(ma.Nested(TextFilePIISchema))
    owners = ma.List(ma.Nested(UserSchema, exclude=["owned_datasets"]))
