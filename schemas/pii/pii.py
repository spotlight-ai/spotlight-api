from marshmallow import Schema

from models.pii.pii import PIIModel


class PIISchema(Schema):
    class Meta:
        model = PIIModel
        fields = ('description',)
