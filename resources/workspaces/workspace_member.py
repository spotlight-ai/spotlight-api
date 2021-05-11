from flask import abort, request
from flask_restful import Resource
from core.decorators import authenticate_token
from core.errors import WorkspaceErrors
from db import db
from models.auth.user import UserModel
from models.workspaces.workspace_member import WorkspaceMemberModel
from schemas.workspaces.workspace_member import WorkspaceMemberSchema
from resources.user import UserCollection
workspace_member_schema = WorkspaceMemberSchema()


class WorkspaceMember(Resource):
    """/workspace/<id>/member/<id>"""
    
    @staticmethod
    def get_workspace_member(workspace_id, user_id):
        member: WorkspaceMemberModel = WorkspaceMemberModel.query.filter(
            WorkspaceMemberModel.workspace_id == workspace_id,
            WorkspaceMemberModel.user_id == user_id
        ).first()
        return member

    def get(self):
        raise NotImplementedError
    
    def patch(self):
        raise NotImplementedError
    
    @authenticate_token
    def delete(self, user_id, workspace_id, member_user_id) -> tuple:
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
    

    @staticmethod
    def create_workspace_member(workspace_member_data):

        workspace_member_entry = workspace_member_schema.load(workspace_member_data, session=db.session)
        
        db.session.add(workspace_member_entry)
        db.session.commit()
        return workspace_member_entry


    @authenticate_token
    def post(self) -> tuple:
        """Users will add themselves to the workspace list of members via invite link."""
        data: dict = request.get_json(force=True)
        member = WorkspaceMember.get_workspace_member(data["workspace_id"], data["user_id"])
        if member:
            abort(409, WorkspaceErrors.ADD_MEMBER_EXISTS_IN_WORKSPACE.format(data["user_id"]))
        
        WorkspaceMemberCollection.create_workspace_member(data)

        return None, 201
    
    def get(self):
        raise NotImplementedError
