from db import db
from models.pii.marker_base import PIIMarkerBaseModel

class PIIMarkerImageModel(PIIMarkerBaseModel):
    __tablename__ = "pii_marker_image"
    pii_id = db.Column(db.ForeignKey("pii_marker_base.pii_id", ondelete="cascade"), primary_key=True)
    x1 = db.Column(db.Integer, nullable=False)
    y1 = db.Column(db.Integer, nullable=False)
    x2 = db.Column(db.Integer, nullable=False)
    y2 = db.Column(db.Integer, nullable=False)

    __mapperargs__ = {
        "polymorphic_identity": "IMAGE_FILE"
    }

    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __repr__(self):
        return f"PIIMarkerImageModel(x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2})"

    def __str__(self):
        return f"PIIMarkerImageModel({self.x1, self.y1}), ({self.x2}, {self.y2})"