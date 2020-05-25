from db import ma
from models.roles.role_member import RoleMemberModel
from schemas.user import UserSchema


class RoleMemberSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = RoleMemberModel
    
    user = ma.Nested(UserSchema, exclude=['last_login', 'created_ts'])
