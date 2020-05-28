from db import ma
from models.user import UserModel


class UserSchema(ma.ModelSchema):
    class Meta:
        model = UserModel
        load_only = ('password',)
        exclude = ('role', 'role_member')
