from models.workspaces.workspace_member import WorkspaceMemberModel
from schemas.workspaces.workspace_member import WorkspaceMemberSchema
from flask_restful import Resource
from core.decorators import authenticate_token
from flask import abort, request
import json
from flask_jwt_extended import decode_token
from jwt.exceptions import ExpiredSignatureError
from core.errors import WorkspaceErrors
from models.auth.user import UserModel

workspace_member_schema = WorkspaceMemberSchema()

class WorkspaceMember(Resource):
    """/workspace/<id>/member/<id>"""
    def get(self):
        raise NotImplementedError

    def patch(self):
        raise NotImplementedError

    @authenticate_token
    def delete(self, user_id, workspace_id, member_user_id) -> None:
        # workspace: WorkspaceModel = WorkspaceModel.query.filter_by(workspace_id=workspace_id).first()

        # if not workspace:
        #     abort(404, workspace_id)

        # member: WorkspaceMemberModel = WorkspaceMemberModel.query.filter(
        #     WorkspaceMemberModel.workspace_id == workspace_id,
        #     WorkspaceMemberModel.user_id == user_id
        # ).first()

        # if not member.is_owner:
        #     abort(401, "User does not own workspace. ")

        # all_members: [WorkspaceMemberModel] = WorkspaceMemberModel.query.filter_by(workspace_id=workspace_id).all()

        # for member in all_members:
        #     member.delete(synchronize_session=False)

        # workspace.delete(synchronize_session=False)  # TODO look up synchronize session
        # db.session.commit()
        # return
        raise NotImplementedError
class WorkspaceMemberCollection(Resource):
    """/workspace/<id>/member"""

    @authenticate_token
    def post(self, user_id: int, workspace_id) -> None:
        # """Users will add themselves to the workspace list of members via invite link."""
        # data: dict = request.get_json(force=True)
        # try:
        #     identity = decode_token(data["token"]).get("sub")
        # except ExpiredSignatureError:
        #     abort(401, WorkspaceErrors.ADD_MEMBER_TOKEN_EXPIRED)
        
        # # Validate Token Identity
        # email = identity["email"]
        # workspace_id = identity["workspace_id"]
        # is_owner = identity["is_owner"]

        # if email != UserModel.query.filter_by(user_id=user_id).first().email:
        #     abort(400, "Signed in user does not match user in token. ")
        
        # member = WorkspaceMemberModel.query.filter(
        #     WorkspaceMemberModel.workspace_id == workspace_id,
        #     WorkspaceMemberModel.user_id == user_id
        # ).all()
        # if member:
        #     abort(409, WorkspaceErrors.ADD_MEMBER_EXISTS_IN_WORKSPACE.format(identity["email"]))
        
        # workspace_member_data = {
        #     "workspace_id": workspace_id,
        #     "user_id": user_id,
        #     "is_owner": is_owner,
        # }

        # # Add Member to Workspace
        # workspace_member_entry = workspace_member_schema.load(workspace_member_data)

        # db.session.add(workspace_member_entry)
        # db.session.commit()
        # return
        raise NotImplementedError

    def get(self): 
        raise NotImplementedError
