from db import db
from models.pii.marker_base import PIIMarkerBaseModel


class FileModel(db.Model):
    __tablename__ = "file"
    
    file_id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset.dataset_id", ondelete="cascade"),
    )
    location = db.Column(db.String, unique=True)
    
    markers = db.relationship(
        PIIMarkerBaseModel,
        backref="file",
        lazy=True,
        cascade="save-update, merge, delete",
    )
    
    def __init__(self, dataset_id, location):
        self.dataset_id = dataset_id
        self.location = f"s3://temp-test-datasets.s3.amazonaws.com/{location}"
    
    def __repr__(self):
        return f"<File(id={self.dataset_id},location={self.location}>"
