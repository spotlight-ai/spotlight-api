from db import ma 
from models.pii.marker_image import PIIMarkerImageModel

class PIIMarkerImageSchema(ma.ModelSchema):
    class Meta:
        model = PIIMarkerImageModel
        include_fk = True
