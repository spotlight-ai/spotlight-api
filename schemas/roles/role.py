from db import ma
from models.roles.role import RoleModel


class RoleSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = RoleModel
