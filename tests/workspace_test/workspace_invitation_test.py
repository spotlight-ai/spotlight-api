import pytest

from models.auth.user import UserModel
from models.workspaces.workspace import WorkspaceModel
from resources.workspaces.workspace_invitation import WorkspaceInvitation
from tests.conftest import generate_auth_headers

existing_owner = 1
existing_member = 2
new_owner_email = "new_owner@email.com"
new_member_email = "new_member@email.com"
workspace_id = 1


@pytest.fixture
def mocked_send_email(mocker):
    return mocker.patch("resources.workspaces.workspace_invitation.send_email")


def test_invitation_for_owner_success(client, db_session, mocked_send_email):
    invite_email = new_owner_email
    user_id = existing_owner

    body = {
        "is_owner": True,
        "email": invite_email,
        "workspace_id": workspace_id,
    }
    headers = generate_auth_headers(client, user_id)
    res = client.post(f"/workspace/{workspace_id}/invite", json=body, headers=headers)

    assert res.status_code == 200
    mocked_send_email.assert_called_once()


def test_invitation_for_member_success(client, db_session, mocked_send_email):
    invite_email = new_member_email
    user_id = existing_owner

    body = {
        "is_owner": False,
        "email": invite_email,
        "workspace_id": workspace_id,
    }
    headers = generate_auth_headers(client, user_id)
    res = client.post(f"/workspace/{workspace_id}/invite", json=body, headers=headers)

    assert res.status_code == 200
    mocked_send_email.assert_called_once()


def test_non_owner_sends_invitation(client, db_session):
    invite_email = new_member_email
    user_id = existing_member

    body = {
        "is_owner": False,
        "email": invite_email,
        "workspace_id": workspace_id,
    }

    headers = generate_auth_headers(client, user_id)
    res = client.post(f"/workspace/{workspace_id}/invite", json=body, headers=headers)

    assert res.status_code == 401

# def test_workspace_invitation_malformed_request_is_owner_value(client, db_session):
#     headers = generate_auth_headers(client, existing_owner)

#     invite_email = new_member_email
#     workspace_name = WorkspaceModel.query.filter_by(workspace_id=1).first().workspace_name

#     body = {
#         "is_owner": None,
#         "workspace_name": workspace_name,
#         "email": email,
#     }
#     res = client.post(f"/workspace/{workspace_id}/invite", json=body, headers=headers)
#     assert res.status_code == 400

#     body = {
#         "is_owner": False,
#         "email": email,
#     }
#     res = client.post(f"/workspace/{workspace_id}/invite", json=body, headers=headers)
#     assert res.status_code == 400

#     body = {
#         "is_owner": False,
#         "workspace_name": workspace_name,
#     }

#     body = {
#         "is_owner": False,
#         "workspace_name": None,
#         "email": None,
#     }
#     res = client.post(f"/workspace/{workspace_id}/invite", json=body, headers=headers)
#     assert res.status_code == 400

#     body = {
#         "is_owner": False,
#         "workspace_name": workspace_name,
#         "email": None,
#     }
#     res = client.post(f"/workspace/{workspace_id}/invite", json=body, headers=headers)
#     assert res.status_code == 400


def test_workspace_invitation_email_exists_in_workspace(client, db_session):
    invite_email = UserModel.query.filter_by(user_id=existing_member).first().email
    user_id = existing_owner

    body = {
        "is_owner": False,
        "email": invite_email,
        "workspace_id": workspace_id,
    }

    headers = generate_auth_headers(client, user_id)
    res = client.post(f"/workspace/{workspace_id}/invite", json=body, headers=headers)

    assert res.status_code == 409


"""
Invite a new person to the workspace
Invite an existing member to the workspace
Invite non-spotlight user should be success
invitation malformed request

Accept from person with spotlight account
accept from person without spotlight account
no spotlight account attempting login
spotlight account attempting signup
accepting token with different email address
accepting token with different workspace name
accepting expired token
(no way to track accepting used token for now?)





"""

@pytest.fixture
def mocked_email_template(mocker):
    return mocker.patch("resources.workspaces.workspace_invitation.Template")


@pytest.fixture
def mocked_mail(mocker):
    return mocker.patch("resources.workspaces.workspace_invitation.Mail")


@pytest.fixture
def mocked_send_mail(mocker):
    return mocker.patch("resources.workspaces.workspace_invitation.send_email")

@pytest.fixture
def mock_send_invitation(mocker):
    return mocker.patch.object(WorkspaceInvitation, "send_invitation", wraps=WorkspaceInvitation.send_invitation)

@pytest.fixture
def mock_create_access_token(mocker):
    return mocker.patch("resources.workspaces.workspace_invitation.create_access_token")


def _invite_assertions(client, workspace_name, invite_email, owner_status):
    workspace_owner = 1

    headers = generate_auth_headers(client, workspace_owner)
    body = {
        "email": invite_email,
        "owner": owner_status,
    }
    test_invitation_token = f"test_invitation_token_{workspace_name}_{invite_email}_{owner_status}"
    mock_create_access_token.return_value = test_invitation_token
    response = client.post(f"/workspace/{workspace_name}/invite", json=body, headers=headers)

    assert response.status_code == 200
    args, _ = mock_send_invitation.call_args
    assert workspace_name in args
    assert test_invitation_token in args
    assert invite_email in args

    _, kwargs = mocked_email_template.return_value.safe_substitute.call_args
    assert kwargs["workspace_name"] == workspace_name
    assert workspace_name in kwargs["url"]
    assert test_invitation_token in kwargs["url"]

    _, kwargs = mocked_mail.call_args
    assert kwargs["to_emails"] == invite_email

    mocked_send_mail.assert_called()


def test_invitation_to_new_person(client, db_session, mock_send_invitation, mock_create_access_token, mocked_email_template, mocked_mail, mocked_send_mail):
    """As the owner of a workspace, With email of user to invite and status of ownership, send email link to user containing workspace name and invite token"""

    invite_email = "new_person@email.com"
    owner_status = False

    _invite_assertions(client, "Existing_Workspace", invite_email, owner_status)


def test_invitation_to_existing_spotlight_user(client, db_session, mock_send_invitation, mock_create_access_token, mocked_email_template, mocked_mail, mocked_send_mail):
    invite_email = "mary@spotlight.ai"
    owner_status = False

    _invite_assertions(client,"Existing_Workspace", invite_email, owner_status)

def test_invitation_non_existing_workspace():
    # 404 workspace not found
    pass

def test_invitation_existing_member():
    # 409 member in workspace
    pass

def test_invitation_malformed_request():
    # 400 bad request
    pass

def test_invitation_as_non_owner():
    # 403 user is forbidden from making changes
    pass


def test_accept_as_non_spotlight_user():
    pass

def test_accept_as_spotlight_user():
    pass

def test_accept_as_existing_member():
    pass

def test_accept_unmatching_emails():
    pass

def test_accept_expired_token():
    pass

@pytest.mark.xfail
def test_accept_already_used_token():
    raise NotImplementedError