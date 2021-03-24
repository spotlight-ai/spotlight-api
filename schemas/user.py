from marshmallow import fields
from marshmallow.validate import Length

from db import ma
from models.auth.user import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        exclude = (
            "role",
            "role_member",
            "owned_datasets",
            "api_keys",
        )
        ordered = True
        load_instance = True

    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=Length(min=8))
    first_name = fields.String(required=True, validate=Length(min=1))
    last_name = fields.String(required=True, validate=Length(min=1))
