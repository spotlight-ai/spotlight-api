from db import db
from models.datasets.base import DatasetModel


class FlatFileDatasetModel(DatasetModel):
    __tablename__ = "flat_file_dataset"
    
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.dataset_id'), primary_key=True)
    location = db.Column(db.String, unique=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'FLAT_FILE'
    }
    
    def __init__(self, dataset_name, uploader, location):
        super().__init__(dataset_name=dataset_name, dataset_type='FLAT_FILE', uploader=uploader)
        self.location = f's3://uploaded-datasets.s3.amazonaws.com/{location}'
    
    def __repr__(self):
        return f"<FlatFileDataset {self.location}>"
