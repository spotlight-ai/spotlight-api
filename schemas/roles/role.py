from db import ma
from models.roles.role import RoleModel


class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        include_fk = True
        model = RoleModel
        load_only = ("creator_id", "user_id")
        load_instance = True
    
    members = ma.List(
        ma.Nested(
            "RoleMemberSchema", exclude=["role_id", "role_member_id", "user_id"]
        )
    )
    creator = ma.Nested(
        "UserSchema", exclude=["created_ts", "last_login", "owned_datasets"]
    )
    permissions = ma.List(ma.Nested("PIISchema"))
    datasets = ma.List(ma.Nested("DatasetSchema", exclude=["roles"]))
