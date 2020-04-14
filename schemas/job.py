from db import ma
from models.job import JobModel


class JobSchema(ma.ModelSchema):
    class Meta:
        model = JobModel
        dump_only = ('job_status', 'job_created_ts', 'job_id', 'job_completed_ts')
