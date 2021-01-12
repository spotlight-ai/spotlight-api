from db import ma 
from models.pii.marker_base import PIIMarkerBaseModel

class PIIMarkerBaseSchema(ma.ModelSchema):
    class Meta:
        model = PIIMarkerBaseModel
        include_fk = True
        dump_only = ("last_updated_ts",)