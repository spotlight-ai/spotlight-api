from datetime import datetime

from db import db


class TextFilePIIModel(db.Model):
    __tablename__ = "pii_text_file"
    __tableargs__ = db.UniqueConstraint(
        "pii_id", "dataset_id", "start_location", "end_location"
    )
    
    pii_id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(
        db.Integer, db.ForeignKey("dataset.dataset_id", ondelete="cascade")
    )
    pii_type = db.Column(db.String, nullable=False)
    start_location = db.Column(db.Integer, nullable=False)
    end_location = db.Column(db.Integer, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    page_number = db.Column(db.Integer, nullable=False, server_default="1")
    last_updated_ts = db.Column(db.DateTime, nullable=False)
    
    def __init__(self, dataset_id, pii_type, start_location, end_location, confidence, page_number=1):
        self.dataset_id = dataset_id
        self.pii_type = pii_type
        self.start_location = start_location
        self.end_location = end_location
        self.confidence = confidence
        self.page_number = page_number
        self.last_updated_ts = datetime.utcnow()
    
    def __repr__(self):
        return f"<TextFilePII {self.pii_type}: {self.start_location} - {self.end_location} ({self.confidence}%)"
