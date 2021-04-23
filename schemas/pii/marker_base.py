import typing

from db import ma 
from marshmallow import ValidationError
from models.pii.marker_base import PIIMarkerBaseModel
from schemas.pii.marker_character import PIIMarkerCharacterSchema
from schemas.pii.marker_image import PIIMarkerImageSchema

class PIIMarkerSchema(ma.SQLAlchemyAutoSchema):
    type_map = {
        "image": PIIMarkerImageSchema,
        "character": PIIMarkerCharacterSchema,
    }
    class Meta:
        model = PIIMarkerBaseModel
        include_fk = True
        load_instance = True
        dump_only = ("last_updated_ts",)

    def dump(self, obj: typing.Any, *, many: bool = None):
        result = []
        errors = {}
        many = self.many if many is None else bool(many)

        if not many:
            return self._dump(obj)

        for idx, value in enumerate(obj):
            try:
                res = self._dump(value)
                result.append(res)

            except ValidationError as error:
                errors[idx] = error.normalized_messages()
                result.append(error.valid_data)

        if errors:
            raise ValidationError(errors, data=obj, valid_data=result)

        return result

    def _dump(self, obj: typing.Any):
        marker_type = getattr(obj, "marker_type")
        inner_schema = PIIMarkerSchema.type_map.get(marker_type)

        if inner_schema is None:
            raise ValidationError(f"Missing schema for '{marker_type}'")

        return inner_schema().dump(obj)