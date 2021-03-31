import datetime
import json

import pytest

from models.auth.user import UserModel
from models.workspaces.workspace_member import WorkspaceMemberModel
from tests.conftest import generate_access_token, generate_auth_headers

workspace_id = 1
existing_owner = 1
existing_member = 2
new_owner = 3
new_member = 4


def _delete_member(client, auth_user_id, delete_user_id):
    headers = generate_auth_headers(client, user_id=auth_user_id)
    res = client.delete(
        f"/workspace/{workspace_id}/member/{delete_user_id}", headers=headers)
    return res


def _add_member(client, auth_user_id, is_owner=False, token_user_id=None, email=None, expires_delta=datetime.timedelta(hours=24)):
    if not token_user_id:
        token_user_id = auth_user_id
    if not email:
        email = UserModel.query.filter_by(user_id=token_user_id).first().email

    identity = {
        "email": email,
        "workspace_id": workspace_id,
        "is_owner": is_owner,
    }

    body = {"token": generate_access_token(identity, expires_delta)}
    headers = generate_auth_headers(client, user_id=auth_user_id)
    return body, headers


def _assert_member_does_not_exist(user_id):
    assert len(WorkspaceMemberModel.query.filter(
        WorkspaceMemberModel.workspace_id == workspace_id,
        WorkspaceMemberModel.user_id == user_id,
    ).all()) == 0


def _assert_member_exists_once(user_id):
    assert len(WorkspaceMemberModel.query.filter(
        WorkspaceMemberModel.workspace_id == workspace_id,
        WorkspaceMemberModel.user_id == user_id,
    ).all()) == 1


# TestDeleteMemberFromCollection
def test_delete_member_success(client, db_session):
    user_to_delete = existing_member
    user_id = existing_owner

    _assert_member_exists_once(user_to_delete)

    res = _delete_member(client, user_id, user_to_delete)

    assert res.status_code == 204
    _assert_member_does_not_exist(user_to_delete)


def test_delete_member_does_not_exist(client, db_session):
    user_to_delete = new_member  # does not exist in test database for WorkspaceMemberModel
    user_id = existing_owner

    _assert_member_does_not_exist(user_to_delete)

    res = _delete_member(client, user_id, user_to_delete)

    assert res.status_code == 204
    _assert_member_does_not_exist(user_to_delete)


def test_delete_member_unauthorized(client, db_session):
    user_to_delete = existing_owner
    unauthorized_user = existing_member

    _assert_member_exists_once(user_to_delete)

    res = _delete_member(client, unauthorized_user, user_to_delete)

    assert res.status_code == 403
    _assert_member_exists_once(user_to_delete)


# TestAddMemberToCollection
def test_add_owner_success(client, db_session):
    user_to_add = new_owner
    _assert_member_does_not_exist(user_to_add)

    body, headers = _add_member(client, user_to_add)
    res = client.post(f"/workspace/{workspace_id}/member", json=body, headers=headers)

    assert res.status_code == 201
    assert json.loads(res.data.decode()) is None
    _assert_member_exists_once(user_to_add)


def test_add_member_success(client, db_session):
    user_to_add = new_member
    _assert_member_does_not_exist(user_to_add)

    body, headers = _add_member(client, user_to_add)
    res = client.post(f"/workspace/{workspace_id}/member", json=body, headers=headers)

    assert res.status_code == 201
    assert json.loads(res.data.decode()) is None
    _assert_member_exists_once(user_to_add)


def test_user_in_request_and_token_do_not_match(client, db_session):
    user_to_add = new_member
    token_user_id = new_owner
    _assert_member_does_not_exist(user_to_add)

    body, headers = _add_member(client, user_to_add, token_user_id=token_user_id)
    res = client.post(f"/workspace/{workspace_id}/member", json=body, headers=headers)

    assert res.status_code == 400
    message = json.loads(res.data.decode())["message"].lower()
    assert "not match" in message
    _assert_member_does_not_exist(user_to_add)


def test_token_expired(client, db_session):
    user_to_add = new_member
    _assert_member_does_not_exist(user_to_add)

    body, headers = _add_member(
        client, user_to_add, expires_delta=datetime.timedelta(-1, 86392, 895000))
    res = client.post(f"/workspace/{workspace_id}/member", json=body, headers=headers)

    assert res.status_code == 401
    message = json.loads(res.data.decode())["message"].lower()
    assert "invitation token" in message
    assert "expired" in message
    _assert_member_does_not_exist(user_to_add)


def test_user_in_token_exists_in_workspace(client, db_session):
    user_to_add = existing_member

    _assert_member_exists_once(user_to_add)

    body, headers = _add_member(client, user_to_add)
    res = client.post(f"/workspace/{workspace_id}/member", json=body, headers=headers)

    assert res.status_code == 409
    message = json.loads(res.data.decode())["message"]
    assert "email" in message
    assert "exists" in message

    _assert_member_exists_once(user_to_add)


# Not Yet Implemented
@pytest.mark.skip
def test_update_member_one_field_success():
    pass


@pytest.mark.skip
def test_update_member_multi_field_success():
    pass


@pytest.mark.skip
def test_update_member_unauthorized():
    pass


@pytest.mark.skip
def test_update_member_field_not_updatable():
    pass


@pytest.mark.skip
def test_get_member_success():
    pass


@pytest.mark.skip
def test_get_member_unauthorized():
    pass


@pytest.mark.skip
def test_get_member_collection_success():
    pass


@pytest.mark.skip
def test_get_member_collection_unauthorized():
    pass
