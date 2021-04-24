import datetime
import json
import os
from string import Template

from flask import abort, request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from sendgrid.helpers.mail import Mail

from core.decorators import authenticate_token
from models.auth.user import UserModel
from models.workspaces.workspace import WorkspaceModel
from models.workspaces.workspace_member import WorkspaceMemberModel
from resources.auth.util import send_email


class WorkspaceInvitation(Resource):
    """/workspace/<name>/invite"""
    @authenticate_token
    def post(self, user_id, workspace_id) -> None:
        member: WorkspaceMemberModel = WorkspaceMemberModel.query.filter(
            WorkspaceMemberModel.workspace_id == workspace_id,
            WorkspaceMemberModel.user_id == user_id
        ).first()
        if not member.is_owner:
            abort(401, "User is not owner of workspace.")

        data: dict = request.get_json(force=True)
        try:
            invite_email = data["email"]
            invite_workspace_id = data["workspace_id"]
            invite_is_owner = data["is_owner"]
        except KeyError:
            abort(400, "Malformed Request")

        invite_user = UserModel.query.filter_by(email=invite_email).first()
        if invite_user:
            member = WorkspaceMemberModel.query.filter(
                WorkspaceMemberModel.workspace_id == workspace_id,
                WorkspaceMemberModel.user_id == invite_user.user_id,
            ).all()
            if member:
                abort(409, "User already exists in workspace.")

        identity = {
            "email": invite_email,
            "workspace_id": workspace_id,
            "is_owner": False,
        }

        invite_token = create_access_token(
            identity=json.dumps(identity),
            expires_delta=datetime.timedelta(hours=24)
        )

        workspace_name = WorkspaceModel.query.filter_by(
            workspace_id=workspace_id).first().workspace_name

        # TODO: confirm if html button clicks a POST or GET -- needs GET
        html_body: Template = Template(
            open("./email_templates/workspace_invitation.html").read()
        ).safe_substitute(
            workspace_name=workspace_name,
            url=f"{os.environ.get('BASE_WEB_URL')}/workspace/{workspace_name}/invite?token={invite_token}"
        )

        message: Mail = Mail(
            from_email="hellospotlightai@gmail.com",
            to_emails=invite_email,
            subject="SpotlightAI | Invitation to Join Workspace",
            html_content=html_body,
        )

        send_email(message)
        return 204
