from db import ma 
from marshmallow import fields
from models.pii.marker_character import PIIMarkerCharacterModel

class PIIMarkerCharacterSchema(ma.SQLAlchemyAutoSchema):
    marker_type = fields.Str(missing="character")
    class Meta:
        model = PIIMarkerCharacterModel
        include_fk = True
        dump_only = ("last_updated_ts", "pii_id")
        load_instance = True
