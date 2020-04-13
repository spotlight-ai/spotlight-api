from flask_restful import Resource
from flask import request, abort
from schemas.job import JobSchema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from models.job import JobModel
from core.decorators import authenticate_token
from db import db

job_schema = JobSchema()


class JobCollection(Resource):
    def get(self):
        job_status = request.args.get('status')
        if job_status:
            jobs = JobModel.query.filter_by(job_status=job_status.upper()).order_by(JobModel.job_created_ts).all()
        else:
            jobs = JobModel.query.order_by(JobModel.job_created_ts).all()
        return job_schema.dump(jobs, many=True)

    @authenticate_token
    def post(self):
        try:
            data = job_schema.load(request.get_json(force=True))
            db.session.add(data)
            db.session.commit()
            return
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)


class Job(Resource):
    loadable_fields = ['job_status', 'job_completed_ts']

    def get(self, job_id):
        job = JobModel.query.filter_by(job_id=job_id).first()
        return job_schema.dump(job)

    def patch(self, job_id):
        job = JobModel.query.filter_by(job_id=job_id).first()
        data = request.get_json(force=True)
        for k, v in data.items():
            if k in self.loadable_fields:
                job.__setattr__(k, v)
        db.session.commit()
        return job_schema.dump(job)
