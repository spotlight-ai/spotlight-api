from tests.conftest import workspace_route
from tests.conftest import decode_access_token
from models.workspaces.workspace import WorkspaceModel

import pytest
import json

new_workspace_name = "New_Workspace"
access_code = "StartSpotlight"
email = "test@email.com"

# TestWorkspaceCollectionAdd
def test_add_workspace_success(client, db_session):
    workspace_name = new_workspace_name
    assert WorkspaceModel.query.filter_by(workspace_name=workspace_name).first() == None

    body = {
        "token": "StartSpotlight",
        "email": email,
        "workspace_name": workspace_name,
    }
    res = client.post("/workspace", json=body)
    assert res.status_code == 201
    assert len(WorkspaceModel.query.filter_by(workspace_name=workspace_name).all()) == 1
    res_json = json.loads(res.data.decode())
    assert "token" in res_json
    identity = decode_access_token(res_json["token"])

    assert "email" in identity
    assert "workspace_id" in identity
    assert "is_owner" in identity
    assert identity["email"] == email
    assert identity["workspace_id"] == WorkspaceModel.query.filter_by(workspace_name=workspace_name).first().workspace_id
    assert identity["is_owner"] == True

def test_add_workspace_name_conflict(client, db_session):
    existing_workspace_name = WorkspaceModel.query.filter_by(workspace_id=1).first().workspace_name
    workspace_name = existing_workspace_name
    assert len(WorkspaceModel.query.filter_by(workspace_name=workspace_name).all()) == 1

    body = {
        "token": access_code,
        "email": email,
        "workspace_name": workspace_name,
    }
    res = client.post("/workspace", json=body)
    assert res.status_code == 409
    assert len(WorkspaceModel.query.filter_by(workspace_name=workspace_name).all()) == 1
    message = json.loads(res.data.decode()).get("message")
    assert workspace_name in message
    assert "exists" in message
    
def test_add_workspace_unauthorized(client, db_session):
    workspace_name = new_workspace_name
    assert WorkspaceModel.query.filter_by(workspace_name=workspace_name).first() == None

    body = {
        "token": "Incorrect Access Code",
        "email": email,
        "workspace_name": workspace_name,
    }
    res = client.post("/workspace", json=body)
    assert res.status_code == 401
    assert WorkspaceModel.query.filter_by(workspace_name=workspace_name).first() == None
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
