import datetime
import json
import os
from string import Template

from flask import abort, request
from flask_jwt_extended import create_access_token, decode_token
from jwt.exceptions import ExpiredSignatureError
from flask_restful import Resource
from sendgrid.helpers.mail import Mail
from marshmallow import Schema, fields

from core.decorators import authenticate_token
from core.errors import WorkspaceErrors
from models.auth.user import UserModel
from models.workspaces.workspace_member import WorkspaceMemberModel
from resources.auth.util import send_email
from resources.auth.login import Login
from resources.workspaces.workspace import Workspace
from resources.workspaces.workspace_member import WorkspaceMember, WorkspaceMemberCollection
from resources.user import UserCollection

IdentitySchema = Schema.from_dict(
    {
        "email": fields.Email(),
        "workspace_id": fields.Int(),
        "is_owner": fields.Bool(),
    }
)

def verify_user_not_in_workspace(workspace_name, invite_email):
    invite_user = UserModel.query.filter_by(email=invite_email).first()
    if invite_user:
        member = WorkspaceMemberModel.query.filter(
            WorkspaceMemberModel.workspace_name == workspace_name,
            WorkspaceMemberModel.user_id == invite_user.user_id,
        ).all()
        if member:
            abort(409, "User already exists in workspace.")



class WorkspaceInvitation(Resource):
    """/workspace/<workspace_name>/invite"""

    @staticmethod
    def send_invitation(workspace_name, invite_token, invite_email):
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


    @staticmethod
    def create_invite_token(email, workspace_id, is_owner):
        identity = {
            "email": email,
            "workspace_id": workspace_id,
            "is_owner": is_owner,
        }
        invite_token = create_access_token(
            identity=json.dumps(identity),
            expires_delta=datetime.timedelta(hours=24)
        )
        return invite_token


    @staticmethod
    @authenticate_token
    def post(user_id, workspace_name) -> None:

        workspace = Workspace.get_workspace(workspace_name)
        member = WorkspaceMember.get_workspace_member(workspace.workspace_id, user_id)
        if not member.is_owner:
            abort(401, "User is not authorized to invite users to workspace.")

        data: dict = request.get_json(force=True)
        try:
            invite_email = data["email"]
            invite_is_owner = data["owner"]
        except KeyError:
            abort(400, "Malformed Request")

        verify_user_not_in_workspace(workspace_name, invite_email)
        invite_token = WorkspaceInvitation.create_invite_token(
            invite_email,
            workspace.workspace_id,
            invite_is_owner
        )

        WorkspaceInvitation.send_invitation(workspace_name, invite_token, invite_email)

        return 204



class WorkspaceInvitationAccept(Resource):
    """/workspace/<workspace_name>/invite/accept"""
    @staticmethod
    def decode_invite_token(token):
        try:
            data = decode_token(token).get("sub")
            identity = IdentitySchema.load(data)
        except ExpiredSignatureError:
            abort(401, WorkspaceErrors.ADD_MEMBER_TOKEN_EXPIRED)
        return identity

    @staticmethod
    def post(workspace_name, action):
        data = request.get_json(force=True)
        invite_token = data["token"]
        user_data = data["user_data"]
        action = data["action"]
        
        if action.lower() not in ["login, signup"]:
            abort(400, "Invalid workspace invite accept action.")

        identity = WorkspaceInvitationAccept.decode_invite_token(invite_token)

        workspace = Workspace.get_workspace(workspace_name)

        if identity.email != user_data["email"] and identity.workspace_id != workspace.workspace_id:
            abort(400, "Signed in user does not match user in token. ")

        if action == "login":
            _, user = Login.login_user(user_data)

        elif action == "signup":
            user = UserCollection.create_new_user(user_data)

        workspace_member_data = {
            "workspace_id": workspace.workspace_id,
            "user_id": user.user_id,
            "is_owner": identity.is_owner,
        }

        WorkspaceMemberCollection.create_workspace_member(workspace_member_data)
        
        return 201
