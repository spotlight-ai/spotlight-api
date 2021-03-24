from db import ma
from models.job import JobModel


class JobSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = JobModel
        include_fk = True
        load_instance = True
        strict = True
