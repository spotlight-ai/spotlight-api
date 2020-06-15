from marshmallow import fields
from marshmallow.validate import Length

from db import ma
from models.user import UserModel


class UserSchema(ma.ModelSchema):
    class Meta:
        model = UserModel
        exclude = ("role", "role_member", "owned_datasets", "shared_datasets")
        ordered = True

    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=Length(min=8))
    first_name = fields.String(required=True, validate=Length(min=1))
    last_name = fields.String(required=True, validate=Length(min=1))
