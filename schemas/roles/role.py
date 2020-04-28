from db import ma
from models.roles.role import RoleModel
from schemas.roles.role_member import RoleMemberSchema


class RoleSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = RoleModel

    members = ma.List(ma.Nested(RoleMemberSchema))
