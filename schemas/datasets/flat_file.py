from db import ma
from models.datasets.flat_file import FlatFileDatasetModel
from schemas.job import JobSchema
from schemas.pii.text_file import TextFilePIISchema
from schemas.user import UserSchema

class FlatFileDatasetSchema(ma.ModelSchema):
    class Meta:
        model = FlatFileDatasetModel
        fields = (
            "dataset_id",
            "location",
        )
        ordered = True
