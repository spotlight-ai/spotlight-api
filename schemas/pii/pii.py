from db import ma

from models.pii.pii import PIIModel


class PIISchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PIIModel
        ordered = True
        exclude = ("roles", "pii_id")
