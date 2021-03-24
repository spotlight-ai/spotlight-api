from db import ma
from models.workspaces.workspace_member import WorkspaceMemberModel

class WorkspaceMemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkspaceMemberModel
        include_fk = True