from db import ma
from models.user import UserModel


class UserSchema(ma.ModelSchema):
    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'roles', 'datasets_owned', 'email', 'created_ts', 'last_login')
        load_only = ('password',)
