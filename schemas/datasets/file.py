from db import ma
from models.datasets.file import FileModel
from schemas.pii.text_file import TextFilePIISchema


class FileSchema(ma.ModelSchema):
    class Meta:
        model = FileModel
    
    markers = ma.List(ma.Nested(TextFilePIISchema, exclude=["file_id", "pii_id", "file"]))
