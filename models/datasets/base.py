from db import db
import datetime


class DatasetModel(db.Model):
    __tablename__ = "dataset"

    dataset_id = db.Column(db.Integer, primary_key=True)
    dataset_name = db.Column(db.String, nullable=False)
    dataset_type = db.Column(db.String, nullable=False)
    uploader = db.Column(db.Integer, foreign_key='user.user_id')
    created_ts = db.Column(db.DateTime)

    __mapper_args__ = {
        'polymorphic_identity': 'dataset',
        'polymorphic_on': dataset_type
    }

    def __init__(self, dataset_name, dataset_type, uploader):
        self.dataset_name = dataset_name
        self.dataset_type = dataset_type
        self.uploader = uploader
        self.created_ts = datetime.datetime.now()

    def __repr__(self):
        return f"<Dataset {self.dataset_name}>"
