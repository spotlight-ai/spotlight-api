from db import ma
from marshmallow import fields
from models.pii.marker_image import PIIMarkerImageModel

class PIIMarkerImageSchema(ma.SQLAlchemyAutoSchema):
    marker_type = fields.Str(missing="image")
    class Meta:
        model = PIIMarkerImageModel
        include_fk = True
        load_instance = True
        dump_only = ("last_updated_ts", "pii_id")
