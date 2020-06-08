from datetime import datetime

from db import db


class JobModel(db.Model):
    __tablename__ = "job"
    
    job_id = db.Column(db.Integer, primary_key=True)
    job_created_ts = db.Column(db.DateTime, nullable=False)
    job_completed_ts = db.Column(db.DateTime)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.dataset_id'))
    job_status = db.Column(db.String, nullable=False, default="PENDING")
    
    def __init__(self, dataset_id):
        self.job_created_ts = datetime.utcnow()
        self.job_status = "PENDING"
        self.dataset_id = dataset_id
    
    def __repr__(self):
        return f"<Job {self.job_id} created at {self.job_created_ts} - {self.job_status}>"
