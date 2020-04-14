from db import ma
from models.datasets.base import DatasetModel
from schemas.job import JobSchema


class DatasetSchema(ma.ModelSchema):
    class Meta:
        model = DatasetModel
    
    jobs = ma.List(ma.Nested(JobSchema))
