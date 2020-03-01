from db import ma
from models.roles.role_member import RoleMemberModel


class RoleMemberSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = RoleMemberModel

