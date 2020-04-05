from db import ma
from models.datasets.flat_file import FlatFileDatasetModel


class FlatFileDatasetSchema(ma.ModelSchema):
    class Meta:
        model = FlatFileDatasetModel
        fields = ('dataset_name', 'uploader', 'created_ts', 'dataset_id', 'location')
        dump_only = ('created_ts', 'dataset_id')
