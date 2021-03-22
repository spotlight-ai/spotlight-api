from db import ma
from models.workspaces.workspace import WorkspaceModel

class WorkspaceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkspaceModel