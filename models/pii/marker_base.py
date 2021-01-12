from datetime import datetime

from db import db


class PIIMarkerBaseModel(db.Model):
    __tablename__ = "pii_marker_base"

    pii_id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("file.file_id", ondelete="cascade"))
    pii_type = db.Column(db.String, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    marker_type = db.Column(db.String, nullable=False)
    last_updated_ts = db.Column(db.DateTime, nullable=False)

    __mapperargs__ = {
        "polymorphic_identity" : "pii_marker_base",
        "polymorphic_on": marker_type
    }

    def __init__(self, file_id, pii_type, confidence, marker_type):
        self.file_id = file_id
        self.pii_type = pii_type
        self.confidence = confidence
        self.marker_type = marker_type
        self.last_updated_ts = datetime.utcnow()

    def __repr__(self):
        return f"PIIMarkerBaseModel(file_id={self.file_id}, pii_type={self.pii_type}, self.confidence={self.confidence})"





