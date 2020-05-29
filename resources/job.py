from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from core.decorators import authenticate_token
from db import db
from models.job import JobModel
from schemas.job import JobSchema

job_schema = JobSchema()


class JobCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        """
        Get all jobs (optionally by status code).
        :param user_id: Currently logged in user.
        :return: List of jobs.
        """
        job_status = request.args.get('status')
        if job_status:
            jobs = JobModel.query.filter_by(job_status=job_status.upper()).order_by(JobModel.job_created_ts).all()
        else:
            jobs = JobModel.query.order_by(JobModel.job_created_ts).all()
        return job_schema.dump(jobs, many=True)
    
    @authenticate_token
    def post(self, user_id):
        """
        Create a new job.
        :return: None
        """
        try:
            data = request.get_json(force=True)
            job = job_schema.load(data)
            
            db.session.add(job)
            db.session.commit()
            return None, 201
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)


class Job(Resource):
    loadable_fields = ['job_status', 'job_completed_ts']
    
    @authenticate_token
    def get(self, user_id, job_id):
        """
        Retrieves a single job.
        :param user_id: Currently logged in user ID.
        :param job_id: Job ID to be retrieved.
        :return: Job object.
        """
        job = JobModel.query.filter_by(job_id=job_id).first()
        return job_schema.dump(job)
    
    @authenticate_token
    def patch(self, user_id, job_id):
        """
        Edit a job.
        :param user_id: Currently logged in user ID.
        :param job_id: Job ID to be edited.
        :return: None
        """
        job = JobModel.query.filter_by(job_id=job_id).first()
        
        if not job:
            abort(404, "Job not found.")
        
        data = request.get_json(force=True)
        for k, v in data.items():
            if k in self.loadable_fields:
                job.__setattr__(k, v)
        db.session.commit()
        return
    
    @authenticate_token
    def delete(self, user_id, job_id):
        """
        Deletes a job.
        :param user_id: Currently logged in user ID.
        :param job_id: Job ID to be deleted.
        :return: None
        """
        try:
            job = job_schema.load(request.get_json(force=True))
            
            if not job:
                abort(404, "Job not found")
            
            db.session.delete(job)
            db.session.commit()
            return
        except UnmappedInstanceError as err:
            db.session.rollback()
            abort(404, err)
