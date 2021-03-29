from string import Template

from flask import abort, request
from flask_jwt_extended import create_access_token, decode_token
from flask_restful import Resource
from sendgrid.helpers.mail import Mail

from core.decorators import authenticate_token
from core.errors import WorkspaceErrors
from db import db
from models.auth.user import UserModel
from models.workspaces.workspace import WorkspaceModel
from models.workspaces.workspace_member import WorkspaceMemberModel as MemberModel
from schemas.workspaces.workspace import WorkspaceSchema
from schemas.workspaces.workspace_member import WorkspaceMemberSchema
from resources.auth.util import send_email

workspace_schema = WorkspaceSchema()
workspace_member_schema = WorkspaceMemberSchema()

workspace_init_token = "StartSpotlight"

class WorkspaceCollection(Resource):
    def post(self) -> None:

        data: dict = request.get_json(force=True)

        _validate_workspace_create(data)


        workspace = workspace_schema.load(data)
        db.session.add(workspace)
        db.session.commit()

        identity = {
            "workspace_id" ,
            "workspace_name",
            "is_owner": True,
        }
        token = create_access_token(
            identity=json.dumps(identity),
            expires_delta=datetime.timedelta(hours=24)
        )

        return {"token": }

    def _validate_workspace_create(data: dict):

        init_token = data.get("init_token")
        if init_token is None:
            abort(400, WorkspaceErrors.MISSING_INIT_TOKEN)
        if init_token != workspace_init_token:
            abort(403, WorkspaceErrors.INCORRECT_INIT_TOKEN)
        
        workspace_name = data.get("workspace_name")
        workspace_same_name = WorkspaceModel.query.filter_by(workspace_name=workspace_name).first()
        if workspace_same_name: 
            abort(409, WorkspaceErrors.WORKSPACE_NAME_EXISTS)

        return


class WorkspaceInvitation(Resource):
    @authenticate_token
    def post(self, user_id, workspace_id) -> None:
        member: MemberModel = MemberModel.query.filter(
            MemberModel.workspace_id == workspace_id,
            MemberModel.user_id == user_id
        )
        if not member.is_owner:
            abort(400, "User is not owner of workspace.")

        data: dict = request.get_json(force=True)
        invite_email_address = data["email_address"]

        identity = {
            "email": invite_email_address,
            "workspace_id": workspace_id,
            "is_owner": False,
            "owner_id": owner_id,
        }

        invite_token = create_access_token(
            identity=json.dumps(identity), 
            expires_delta=datetime.timedelta(hours=24)
        )

        workspace_name = WorkspaceModel.query.filter_by(workspace_id=workspace_id).first().name

        # TODO: confirm if html button clicks a POST or GET -- needs GET
        html_body: Template = Template(
            open("./email_templates/workspace_invitation.html").read()
        ).safe_substitute(
            workspace_name=workspace_name
            url=f"{os.environ.get('BASE_WEB_URL')}/workspace/{workspace_name}/invite?token={invite_token}"
        )
        
        message: Mail = Mail(
            from_email="hellowspotlightai@gmail.com",
            to_emails=invite_email_address,
            subject="SpotlightAI | Invitation to Join Workspace",
            html_content=html_body,
        )
        
        send_email(message)
        return
        

class WorkspaceUserCollection(Resource):
    """user_id and admin true will be supplied in body to add as admin"""
    """user_id and admin false will need invite code in the body. """
    @authenticate_token
    def post(self, user_id: int) -> None:
        """Users will add themselves to the workspace list of members via invite link."""
        data: dict = request.get_json(force=True)
        token = data["token"]

        identity = json.loads(decode_token(token).get("identity"))
        member = MemberModel.query.filter(
            MemberModel.workspace_name == identity["workspace_id"],
            MemberModel.user_id == user_id
        )
        if member:
            return 200

        if identity["is_owner"]:
            # add owner of workspace
            workspace_member_entry = workspace_member_schema.load({
                "workspace_id": identity["workspace_id"],  # TODO: or is it better to get from database?
                "user_id": user_id,
                "is_owner": True,
            })

        else:
            # verify email of token == user_id
            if identity["email"] != UserModel.query.filter_by(user_id=user_id).first().email:
                abort(400, "Signed in user does not match user in token. ")

            workspace_member_entry = workspace_member_schema.load({
                "workspace_id": identity["workspace_id"],
                "user_id": user_id, 
                "is_owner": False,
            })

        db.session.add(workspace_member_entry)
        db.session.commit()
        return


    @authenticate_token
    def delete(self, user_id, workspace_id, del_user_id) -> None:
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
        return