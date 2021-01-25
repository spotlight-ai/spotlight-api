import datetime

from db import db
from models.associations import DatasetOwner, RoleDataset
from models.datasets.file import FileModel
from models.job import JobModel
from models.roles.role import RoleModel


class DatasetModel(db.Model):
    __tablename__ = "dataset"
    
    dataset_id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String, nullable=False)
    dataset_type = db.Column(db.String, nullable=False)
    uploader = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="cascade"))
    created_ts = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow()
    )
    verified = db.Column(db.Boolean, default=False, nullable=True)
    
    files = db.relationship(FileModel, backref="dataset", lazy=True)
    jobs = db.relationship(JobModel, backref="dataset", lazy=True)
    
    roles = db.relationship(RoleModel, secondary=RoleDataset, back_populates="datasets")
    owners = db.relationship(
        "UserModel",
        secondary=DatasetOwner,
        back_populates="owned_datasets",
        cascade="save-update, merge, delete",
    )
    
    def __init__(self, dataset_name, dataset_type, uploader, verified):
        self.dataset_name = dataset_name
        self.dataset_type = dataset_type
        self.uploader = uploader
        self.created_ts = datetime.datetime.now()
        self.verified = verified
    
    def __repr__(self):
        return f"<datadataset {self.dataset_name}>"
