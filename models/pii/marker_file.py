from datetime import datetime
from models.pii.marker_base import PIIMarkerBaseModel

from db import db


class PIIMarkerFileModel(PIIMarkerBaseModel):
    __tablename__ = "pii_marker_file"
    pii_id = db.Column(db.ForeignKey("pii_marker_base.pii_id", ondelete="cascade"), primary_key=True)
    start_location = db.Column(db.Integer, nullable=False)
    end_location = db.Column(db.Integer, nullable=False)

    __mapperargs__ = {
        "polymorphic_identity": "CHARACTER_FILE"
    }

    def __init__(self, start_location, end_location):
        self.start_location = start_location
        self.end_location = end_location

    def __repr__(self):
        return f"PIIMarkerFileModel(start_location={self.start_location}, end_location={self.end_location})"