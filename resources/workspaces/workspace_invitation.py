from flask_restful import Resource
from core.decorators import authenticate_token


class WorkspaceInvitation(Resource):
    """/workspace/<id>/invite"""
    @authenticate_token
    def post(self, user_id, workspace_id) -> None:
        # member: MemberModel = MemberModel.query.filter(
        #     MemberModel.workspace_id == workspace_id,
        #     MemberModel.user_id == user_id
        # )
        # if not member.is_owner:
        #     abort(400, "User is not owner of workspace.")

        # data: dict = request.get_json(force=True)
        # invite_email_address = data["email_address"]

        # identity = {
        #     "email": invite_email_address,
        #     "workspace_id": workspace_id,
        #     "is_owner": False,
        #     "owner_id": owner_id,
        # }

        # invite_token = create_access_token(
        #     identity=json.dumps(identity), 
        #     expires_delta=datetime.timedelta(hours=24)
        # )

        # workspace_name = WorkspaceModel.query.filter_by(workspace_id=workspace_id).first().name

        # # TODO: confirm if html button clicks a POST or GET -- needs GET
        # html_body: Template = Template(
        #     open("./email_templates/workspace_invitation.html").read()
        # ).safe_substitute(
        #     workspace_name=workspace_name
        #     url=f"{os.environ.get('BASE_WEB_URL')}/workspace/{workspace_name}/invite?token={invite_token}"
        # )
        
        # message: Mail = Mail(
        #     from_email="hellowspotlightai@gmail.com",
        #     to_emails=invite_email_address,
        #     subject="SpotlightAI | Invitation to Join Workspace",
        #     html_content=html_body,
        # )
        
        # send_email(message)
        raise NotImplementedError
