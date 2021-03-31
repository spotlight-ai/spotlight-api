import pytest

from models.auth.user import UserModel
from models.workspaces.workspace import WorkspaceModel
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
