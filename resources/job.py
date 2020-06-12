from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from core.decorators import authenticate_token
from db import db
from models.associations import DatasetOwner
from models.datasets.base import DatasetModel
from models.job import JobModel
from models.user import UserModel
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
        datasets_owned = [dataset.dataset_id for dataset in
                          DatasetModel.query.join(DatasetOwner).join(UserModel).filter(
                              (UserModel.user_id == user_id)).all()]
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        job_status = request.args.get('status')
        if job_status:
            if user.admin:
                jobs = JobModel.query.filter((JobModel.job_status.upper() == job_status)).order_by(
                    JobModel.job_created_ts).all()
            else:
                jobs = JobModel.query.filter(JobModel.job_status.upper() == job_status) & (
                    JobModel.dataset_id.in_(datasets_owned)).order_by(JobModel.job_created_ts).all()
        else:
            if user.admin:
                jobs = JobModel.query.order_by(JobModel.job_created_ts).all()
            else:
                jobs = JobModel.query.filter((JobModel.dataset_id.in_(datasets_owned))).order_by(
                    JobModel.job_created_ts).all()
        return job_schema.dump(jobs, many=True)
    
    @authenticate_token
    def post(self, user_id):
        """
        Create a new job.
        :return: None
        """
        try:
            data = request.get_json(force=True)
            
            datasets_owned = [dataset.dataset_id for dataset in
                              DatasetModel.query.join(DatasetOwner).join(UserModel).filter(
                                  (UserModel.user_id == user_id)).all()]
            
            job = job_schema.load(data)
            
            dataset = DatasetModel.query.filter_by(dataset_id=job.dataset_id).first()
            
            if not dataset:
                abort(404, 'Dataset does not exist.')
            
            if job.dataset_id not in datasets_owned:
                abort(401, 'Not authorized to create a job for this dataset.')
            
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
        datasets_owned = [dataset.dataset_id for dataset in
                          DatasetModel.query.join(DatasetOwner).join(UserModel).filter(
                              (UserModel.user_id == user_id)).all()]
        
        job = JobModel.query.filter_by(job_id=job_id).first()
        user = UserModel.query.filter_by(user_id=user_id).first()
        
        if not job:
            abort(404, "Job not found.")
        
        if not user.admin and job.dataset_id not in datasets_owned:
            abort(401, "Not authorized to view this job.")
        
        return job_schema.dump(job)
    
    @authenticate_token
    def patch(self, user_id, job_id):
        """
        Edit a job.
        :param user_id: Currently logged in user ID.
        :param job_id: Job ID to be edited.
        :return: None
        """
        datasets_owned = [dataset.dataset_id for dataset in
                          DatasetModel.query.join(DatasetOwner).join(UserModel).filter(
                              (UserModel.user_id == user_id)).all()]

        job = JobModel.query.filter_by(job_id=job_id).first()
        user = UserModel.query.filter_by(user_id=user_id).first()

        if not job:
            abort(404, "Job not found.")

        if user_id != 'MODEL':
            if not user.admin and job.dataset_id not in datasets_owned:
                abort(401, "Not authorized to edit this job.")

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
            
            datasets_owned = [dataset.dataset_id for dataset in
                              DatasetModel.query.join(DatasetOwner).join(UserModel).filter(
                                  (UserModel.user_id == user_id)).all()]
            user = UserModel.query.filter_by(user_id=user_id).first()
            
            if not job:
                abort(404, "Job not found")
            
            if not user.admin and job.dataset_id not in datasets_owned:
                abort(401, "Not authorized to delete this job.")
            
            db.session.delete(job)
            db.session.commit()
            return
        except UnmappedInstanceError as err:
            db.session.rollback()
            abort(404, err)
