from db import ma
from models.roles.role_member import RoleMemberModel
from schemas.user import UserSchema


class RoleMemberSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = RoleMemberModel
        exclude = ['role_member_id', 'role']
        load_only = ['user_id']
    
    user = ma.Nested(UserSchema, exclude=['last_login', 'created_ts'])
