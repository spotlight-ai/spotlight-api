from db import ma
from models.datasets.file import FileModel
from schemas.pii.marker_base import PIIMarkerSchema


class FileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = FileModel
        load_instance = True
    
    markers = ma.List(ma.Nested("PIIMarkerSchema", exclude=["file_id", "pii_id"]))
