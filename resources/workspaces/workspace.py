from flask import request
from flask_restful import Resource

from core.decorators import authenticate_token
from db import db
from models.auth.user import UserModel
from models.workspaces.workspace import WorkspaceModel
from schemas.workspaces.workspace import WorkspaceSchema
from schemas.workspaces.workspace_member import WorkspaceMemberSchema

workspace_schema = WorkspaceSchema()
workspace_member_schema = WorkspaceMemberSchema()

class WorkspaceCollection(Resource):
    def post(self) -> None:
        data: dict = request.get_json(force=True)

        workspace = workspace_schema.load(data)

        db.session.add(workspace)
        db.session.commit()


class WorkspaceUserCollection(Resource):
    @authenticate_token
    def post(self, user_id: int, workspace_id: int) -> None:
        data: dict = request.get_json(force=True)

        data['workspace_id'] = workspace_id

        workspace_member = workspace_member_schema.load(data, session=db.session)

        db.session.add(workspace_member)
        db.session.commit()