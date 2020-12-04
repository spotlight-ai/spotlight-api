from db import db
from models.datasets.base import DatasetModel


class FlatFileDatasetModel(db.Model):
    __tablename__ = "flat_file_dataset"

    id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset.dataset_id", ondelete="cascade"),
    )
    location = db.Column(db.String, unique=True)

    dataset = db.relationship(DatasetModel, backref="dataset")

    # __mapper_args__ = {"polymorphic_identity": "FLAT_FILE"}

    def __init__(self, dataset_id, location):
        self.dataset_id = dataset_id
        self.location = f"s3://uploaded-datasets.s3.amazonaws.com/{location}"

    def __repr__(self):
        return f"<FlatFileDataset(id={self.dataset_id},location={self.location}>"
