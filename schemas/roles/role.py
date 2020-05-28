from db import ma
from models.roles.role import RoleModel
from schemas.datasets.flat_file import FlatFileDatasetSchema
from schemas.pii.pii import PIISchema
from schemas.roles.role_member import RoleMemberSchema
from schemas.user import UserSchema


class RoleSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = RoleModel
        load_only = ('creator_id', 'user_id')
    
    members = ma.List(
        ma.Nested(RoleMemberSchema, exclude=['role_id', 'role', 'role_member_id', 'user_id']))
    creator = ma.Nested(UserSchema, exclude=['created_ts', 'last_login', 'owned_datasets'])
    permissions = ma.List(ma.Nested(PIISchema))
    datasets = ma.List(ma.Nested(FlatFileDatasetSchema))
