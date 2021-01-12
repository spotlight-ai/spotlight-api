from db import ma 
from models.pii.marker_file import PIIMarkerFileModel

class PIIMarkerFileSchema(ma.ModelSchema):
    class Meta:
        model = PIIMarkerFileModel
        include_fk = True
