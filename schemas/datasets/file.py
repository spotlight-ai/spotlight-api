from db import ma
from models.datasets.file import FileModel
from schemas.pii.marker_base import PIIMarkerBaseSchema


class FileSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = FileModel
    
    markers = ma.List(ma.Nested(PIIMarkerBaseSchema, exclude=["file_id", "pii_id", "file"]))
