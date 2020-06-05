import datetime

from db import db
from models.associations import DatasetOwner, RoleDataset
from models.job import JobModel
from models.pii.text_file import TextFilePIIModel
from models.roles.role import RoleModel


class DatasetModel(db.Model):
    __tablename__ = "dataset"
    
    dataset_id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String, nullable=False)
    dataset_type = db.Column(db.String, nullable=False)
    uploader = db.Column(db.Integer, foreign_key='user.user_id')
    created_ts = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    verified = db.Column(db.Boolean, default=False, nullable=True)
    
    jobs = db.relationship(JobModel, backref='dataset', lazy=True)
    markers = db.relationship(TextFilePIIModel, backref='dataset', lazy=True, cascade="save-update, merge, delete")
    roles = db.relationship(RoleModel, secondary=RoleDataset, back_populates='datasets')
    owners = db.relationship("UserModel", secondary=DatasetOwner, back_populates='owned_datasets',
                             cascade="save-update, merge, delete")
    
    __mapper_args__ = {
        'polymorphic_identity': 'dataset',
        'polymorphic_on': dataset_type
    }
    
    def __init__(self, dataset_name, dataset_type, uploader):
        self.dataset_name = dataset_name
        self.dataset_type = dataset_type
        self.uploader = uploader
        self.created_ts = datetime.datetime.now()
        self.verified = False
    
    def __repr__(self):
        return f"<Dataset {self.dataset_name}>"
