from db import ma
from models.datasets.flat_file import FlatFileDatasetModel
from schemas.job import JobSchema
from schemas.pii.text_file import TextFilePIISchema


class FlatFileDatasetSchema(ma.ModelSchema):
    class Meta:
        model = FlatFileDatasetModel
        fields = (
            "dataset_name",
            "uploader",
            "created_ts",
            "dataset_id",
            "location",
            "jobs",
            "owners",
            "markers",
            "download_link",
        )
        dump_only = ("created_ts", "dataset_id", "jobs", "owners")

    jobs = ma.List(ma.Nested(JobSchema))
    markers = ma.List(ma.Nested(TextFilePIISchema))
