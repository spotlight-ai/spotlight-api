from marshmallow import Schema, fields


class LoginSchema(Schema):
    class Meta:
        strict = True

    email = fields.Str(required=True)
    password = fields.Str(required=True)
