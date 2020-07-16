from db import ma

from models.pii.pii import PIIModel


class PIISchema(ma.ModelSchema):
    class Meta:
        model = PIIModel
        ordered = True
        exclude = ("shared_datasets", "roles", "pii_id")
