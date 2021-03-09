from db import ma
from models.workspaces.workspace import WorkspaceModel

class WorkspaceSchema(ma.ModelSchema):
    class Meta:
        model = WorkspaceModel