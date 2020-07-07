from db import ma
from models.pii.snake_case import PIIColumnar


class PIIColumnarSchema(ma.ModelSchema):
    class Meta:
        model = PIIColumnar
        include_fk = True
        dump_only = ("last_updated_ts",)