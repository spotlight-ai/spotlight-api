import json

import pytest

from models.workspaces.workspace import WorkspaceModel
from tests.conftest import WORKSPACE_ROUTE, decode_access_token

NEW_WORKSPACE_NAME = "New_Workspace"
ACCESS_CODE = "StartSpotlight"
TEST_EMAIL = "test@email.com"


# TestWorkspaceCollectionAdd
def test_add_workspace_success(client, db_session):
    workspace_name = NEW_WORKSPACE_NAME
    assert WorkspaceModel.query.filter_by(workspace_name=workspace_name).first() is None

    body = {
        "token": "StartSpotlight",
        "email": TEST_EMAIL,
        "workspace_name": workspace_name,
    }
    res = client.post(WORKSPACE_ROUTE, json=body)
    assert res.status_code == 201
    assert len(WorkspaceModel.query.filter_by(workspace_name=workspace_name).all()) == 1
    res_json = json.loads(res.data.decode())
    assert "token" in res_json
    identity = decode_access_token(res_json["token"])

    assert "email" in identity
    assert "workspace_id" in identity
    assert "is_owner" in identity
    assert identity["email"] == TEST_EMAIL
    assert identity["workspace_id"] == WorkspaceModel.query.filter_by(
        workspace_name=workspace_name).first().workspace_id
    assert identity["is_owner"] is True


def test_add_workspace_name_conflict(client, db_session):
    existing_workspace_name = WorkspaceModel.query.filter_by(
        workspace_id=1).first().workspace_name
    workspace_name = existing_workspace_name
    assert len(WorkspaceModel.query.filter_by(workspace_name=workspace_name).all()) == 1

    body = {
        "token": ACCESS_CODE,
        "email": TEST_EMAIL,
        "workspace_name": workspace_name,
    }
    res = client.post(WORKSPACE_ROUTE, json=body)
    assert res.status_code == 409
    assert len(WorkspaceModel.query.filter_by(workspace_name=workspace_name).all()) == 1
    message = json.loads(res.data.decode()).get("message")
    assert workspace_name in message
    assert "exists" in message


def test_add_workspace_unauthorized(client, db_session):
    workspace_name = NEW_WORKSPACE_NAME
    assert WorkspaceModel.query.filter_by(workspace_name=workspace_name).first() is None

    body = {
        "token": "Incorrect Access Code",
        "email": TEST_EMAIL,
        "workspace_name": workspace_name,
    }
    res = client.post(WORKSPACE_ROUTE, json=body)
    assert res.status_code == 401
    assert WorkspaceModel.query.filter_by(workspace_name=workspace_name).first() is None
    assert "incorrect" in json.loads(res.data.decode()).get("message").lower()


# Not Yet Implemented
@pytest.mark.skip
def test_get_workspace_collection_success():
    pass


@pytest.mark.skip
def test_get_workspace_success():
    pass


@pytest.mark.skip
def test_update_workspace_success():
    pass


@pytest.mark.skip
def test_delete_workspace_success():
    pass
