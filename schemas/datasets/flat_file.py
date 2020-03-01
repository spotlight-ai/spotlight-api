from db import ma
from models.datasets.flat_file import FlatFileDatasetModel


class FlatFileDatasetSchema(ma.ModelSchema):
    class Meta:
        model = FlatFileDatasetModel
        fields = ('dataset_name', 'location', 'uploader', 'created_ts', 'dataset_id')
        dump_only = ('created_ts', 'dataset_id')