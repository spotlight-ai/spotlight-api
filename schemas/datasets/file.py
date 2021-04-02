from db import ma
from models.datasets.file import FileModel
# from schemas.pii.file import FilePIISchema


class FileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = FileModel
    
    markers = ma.List(ma.Nested("FilePIISchema", exclude=["file_id"]))
