import datetime
import json
from string import Template

from flask import abort, request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from sendgrid.helpers.mail import Mail

from core.decorators import authenticate_token
from core.errors import WorkspaceErrors
from db import db
from models.auth.user import UserModel
from models.workspaces.workspace import WorkspaceModel
from resources.auth.util import send_email
from schemas.workspaces.workspace import WorkspaceSchema

workspace_schema = WorkspaceSchema()

workspace_init_token = "StartSpotlight"


class WorkspaceCollection(Resource):
    """/workspace"""

    def post(self) -> None:

        data: dict = request.get_json(force=True)

        self._validate_workspace_create(data)
        workspace_data = {
            "workspace_name": data.get("workspace_name")
        }

        workspace = workspace_schema.load(workspace_data)
        db.session.add(workspace)
        db.session.commit()

        workspace = WorkspaceModel.query.filter_by(
            workspace_name=data.get("workspace_name")).first()
        identity = {
            "workspace_id": workspace.workspace_id,
            "email": data.get("email"),
            "is_owner": True,
        }
        token = create_access_token(
            json.dumps(identity),
            expires_delta=datetime.timedelta(hours=24)
        )

        return {"token": token}, 201

    def _validate_workspace_create(self, data: dict):

        init_token = data.get("token")
        if init_token is None:
            abort(400, WorkspaceErrors.MISSING_INIT_TOKEN)
        if init_token != workspace_init_token:
            abort(401, WorkspaceErrors.INCORRECT_INIT_TOKEN)

        workspace_name = data.get("workspace_name")
        workspace_same_name = WorkspaceModel.query.filter_by(
            workspace_name=workspace_name).first()
        if workspace_same_name:
            abort(409, WorkspaceErrors.WORKSPACE_NAME_EXISTS.format(workspace_name))

        return

    def get(self):
        return NotImplemented


class Workspace(Resource):
    """/workspace/<id>"""

    def get(self):
        return NotImplemented

    def patch(self):
        return NotImplemented

    def delete(self):
        return NotImplemented
