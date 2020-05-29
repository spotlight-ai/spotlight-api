from marshmallow import fields
from db import ma
from models.job import JobModel


class JobSchema(ma.ModelSchema):
    class Meta:
        model = JobModel
        include_fk = True
        strict = True

    dataset_id = fields.Int(required=True)
