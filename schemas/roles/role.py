from db import ma
from models.roles.role import RoleModel
from schemas.roles.role_member import RoleMemberSchema
from schemas.user import UserSchema


class RoleSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = RoleModel
        exclude = ('creator_id',)
    
    members = ma.List(ma.Nested(RoleMemberSchema))
    creator = ma.Nested(UserSchema, exclude=['created_ts', 'last_login', 'datasets_owned'])
