from tests.conftest import generate_auth_headers, generate_access_token
import pytest
from models.workspaces.workspace import WorkspaceModel
from models.auth.user import UserModel

existing_owner = 1
existing_member = 2
new_owner = 3
new_member = 4
workspace_id = 1


def test_invitation_for_owner_success(client, db_session):

    res = _invite_member(
        client, 
        user_id=existing_owner, 
        invite_user_id=None, 
        email="new_owner@email.com", 
        is_owner=True
    )

    assert res.status_code == 200


def test_invitation_for_member_success(client, db_session):

    res = _invite_member(
        client, 
        user_id=existing_owner, 
        invite_user_id=None, 
        email="new_member@email.com",
    )
    assert res.status_code == 200

def test_non_owner_sends_invitation(client, db_session):

    res = _invite_member(
        client, 
        user_id=existing_member, 
        invite_user_id=new_member, 
    )

    assert res.status_code == 401

def test_workspace_invitation_malformed_request(client, db_session):
    user_to_invite = new_member
    workspace = WorkspaceModel.query.filter_by(workspace_id=1).first()
    email = UserModel.query.filter_by(user_id=user_to_invite).first().email
    body = {
        "is_owner": True,
        "workspace_name": workspace.workspace_name,
        "email": email,
    }
    keys = body.keys()
    for key in keys:
        temp_key = key
        temp_val = body[key]
        del body[key]

        res = _invite_member(
            client, 
            user_id=existing_owner, 
            invite_user_id=user_to_invite,
            body=body,
        )

        assert res.status_code == 400
        body[temp_key] = temp_val

def test_workspace_invitation_email_exists_in_workspace(client, db_session):

    res = _invite_member(
        client, 
        user_id=existing_owner, 
        invite_user_id=existing_member,
    )

    assert res.status_code == 409

def _invite_member(client, user_id, invite_user_id, email=None, body=None, is_owner=False):
    workspace = WorkspaceModel.query.filter_by(workspace_id=1).first()
    if user_id and not email:
        email = UserModel.query.filter_by(user_id=invite_user_id).first().email

    if not body:
        body = {
            "is_owner": is_owner,
            "email": email,
            "workspace_name": workspace.workspace_name,
        }
    headers = generate_auth_headers(client, user_id)
    res = client.post(f"/workspace/{workspace.workspace_id}/invite", json=body, headers=headers)
    return res
