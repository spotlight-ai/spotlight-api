from models.workspaces.workspace_member import WorkspaceMemberModel
from models.workspaces.workspace import WorkspaceModel
from schemas.workspaces.workspace_member import WorkspaceMemberSchema
from flask_restful import Resource
from core.decorators import authenticate_token
from flask import abort, request
import json
from flask_jwt_extended import decode_token
from jwt.exceptions import ExpiredSignatureError
from core.errors import WorkspaceErrors
from models.auth.user import UserModel
from db import db
workspace_member_schema = WorkspaceMemberSchema()

class WorkspaceMember(Resource):
    """/workspace/<id>/member/<id>"""
    def get(self):
        raise NotImplementedError

    def patch(self):
        raise NotImplementedError

    @authenticate_token
    def delete(self, user_id, workspace_id, member_user_id) -> None:
        owner = WorkspaceMemberModel.query.filter(
            WorkspaceMemberModel.workspace_id == workspace_id,
            WorkspaceMemberModel.user_id == user_id,
        ).first().is_owner
        if not owner:
            abort(403, "Not authorized to delete members in workspace.")

        member = WorkspaceMemberModel.query.filter(
            WorkspaceMemberModel.workspace_id == workspace_id,
            WorkspaceMemberModel.user_id == member_user_id,
        )

        if member.first():
            member.delete()
            db.session.commit()

        return None, 204


class WorkspaceMemberCollection(Resource):
    """/workspace/<id>/member"""

    @authenticate_token
    def post(self, user_id: int, workspace_id) -> None:
        """Users will add themselves to the workspace list of members via invite link."""
        data: dict = request.get_json(force=True)
        try:
            identity = decode_token(data["token"]).get("sub")
        except ExpiredSignatureError:
            abort(401, WorkspaceErrors.ADD_MEMBER_TOKEN_EXPIRED)
        
        # Validate Token Identity
        email = identity["email"]
        workspace_id = identity["workspace_id"]
        is_owner = identity["is_owner"]

        if email != UserModel.query.filter_by(user_id=user_id).first().email:
            abort(400, "Signed in user does not match user in token. ")
        
        member = WorkspaceMemberModel.query.filter(
            WorkspaceMemberModel.workspace_id == workspace_id,
            WorkspaceMemberModel.user_id == user_id
        ).all()
        if member:
            abort(409, WorkspaceErrors.ADD_MEMBER_EXISTS_IN_WORKSPACE.format(identity["email"]))
        
        workspace_member_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "is_owner": is_owner,
        }

        # Add Member to Workspace
        workspace_member_entry = workspace_member_schema.load(workspace_member_data)

        db.session.add(workspace_member_entry)
        db.session.commit()
        return

    def get(self): 
        raise NotImplementedError
