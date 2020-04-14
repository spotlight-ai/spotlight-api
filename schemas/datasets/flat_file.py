from db import ma
from models.datasets.flat_file import FlatFileDatasetModel
from schemas.job import JobSchema


class FlatFileDatasetSchema(ma.ModelSchema):
    class Meta:
        model = FlatFileDatasetModel
        fields = ('dataset_name', 'uploader', 'created_ts', 'dataset_id', 'location', 'jobs')
        dump_only = ('created_ts', 'dataset_id', 'jobs')
    
    jobs = ma.List(ma.Nested(JobSchema))
