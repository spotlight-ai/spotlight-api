from datetime import datetime
from models.pii.marker_base import PIIMarkerBaseModel

from db import db


class PIIMarkerCharacterModel(PIIMarkerBaseModel):
    __tablename__ = "pii_marker_character"
    pii_id = db.Column(db.ForeignKey("pii_marker_base.pii_id", ondelete="cascade"), primary_key=True)
    start_location = db.Column(db.Integer, nullable=False)
    end_location = db.Column(db.Integer, nullable=False)

    __mapperargs__ = {
        "polymorphic_identity": "CHARACTER_FILE"
    }

    def __init__(
        self, file_id, pii_type, confidence, start_location, end_location, marker_type="character"
        ):
        super().__init__(file_id, pii_type, confidence, marker_type)

        self.start_location = start_location
        self.end_location = end_location

    def __repr__(self):
        return f"PIIMarkerCharacterModel(start_location={self.start_location}, end_location={self.end_location})"