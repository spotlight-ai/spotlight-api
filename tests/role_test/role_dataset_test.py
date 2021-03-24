import json
from unittest.mock import patch
from tests.conftest import generate_auth_headers
from tests.conftest import dataset_route, role_route, dataset_list
import pytest

def test_get_role_datasets(client, db_session):
    """Role owner should be able to retrieve datasets assigned to a given role."""
    headers = generate_auth_headers(client, user_id=4)

    res = client.get(f"{role_route}/1/dataset", headers=headers)

    assert 200 == res.status_code
    datasets = json.loads(res.data.decode())

    dataset_1_name = dataset_list[0].dataset_name

    assert 1 == len(datasets)
    assert dataset_1_name == datasets[0].get("dataset_name")

def test_get_role_datasets_unowned_role(client, db_session):
    """User of an unowned role should not be able to see dataset details."""
    headers = generate_auth_headers(client, user_id=2)

    res = client.get(f"{role_route}/1/dataset", headers=headers)

    assert res.status_code == 401

@pytest.fixture
def mock_notif(mocker):
    return mocker.patch("resources.roles.role_dataset.send_notifications")


def test_add_new_role_dataset(client, db_session, mock_notif):
    """Tests that a role owner can add an individual dataset to a role."""
    headers = generate_auth_headers(client, user_id=3)

    res = client.post(
        f"{role_route}/1/dataset", headers=headers, json={"datasets": [2]}
    )

    assert res.status_code == 201

    res = client.get(f"{role_route}/1/dataset", headers=headers)
    datasets = json.loads(res.data.decode())

    assert res.status_code == 200
    assert len(datasets) == 2


def test_add_multiple_datasets(client, db_session, mock_notif):
    """Verify that owners can add multiple datasets at once to a role."""
    # Note: Must be owner of all datasets to add to the role. 
    headers_3 = generate_auth_headers(client, user_id=3)
    headers_4 = generate_auth_headers(client, user_id=4)

    # Role Owner cannot add datasets they are not owners of
    res = client.post(
        f"{role_route}/1/dataset", headers=headers_3, json={"datasets": [2, 4]}
    )
    assert res.status_code == 401

    # Update dataset with new owner
    res = client.put(
        f"{dataset_route}/4/owner", headers=headers_4, json={"owners": [3, 4]}
    )

    # Role owner adds datasets to role
    res = client.post(
        f"{role_route}/1/dataset", headers=headers_3, json={"datasets": [2, 4]}
    )
    res = client.get(f"{role_route}/1/dataset", headers=headers_3)
    permissions = json.loads(res.data.decode())

    assert res.status_code == 200
    assert 3 == len(permissions)


def test_add_same_dataset(client, db_session):
    """Owners should not be able to add the same dataset to a role."""
    headers = generate_auth_headers(client, user_id=3)

    res = client.post(
        f"{role_route}/1/dataset", headers=headers, json={"datasets": [1, 2]}
    )

    assert res.status_code == 400

def test_add_unowned_dataset(client, db_session):
    """Users should not be able to add a dataset they do not own to a role."""
    headers = generate_auth_headers(client, user_id=3)

    res = client.post(
        f"{role_route}/1/dataset", headers=headers, json={"datasets": [4]}
    )

    assert res.status_code == 401


def test_update_role_datasets(client, db_session, mock_notif):
    """Owners should be able to overwrite role datasets."""
    headers = generate_auth_headers(client, user_id=3)

    res = client.put(
        f"{role_route}/1/dataset", json={"datasets": [1, 2]}, headers=headers
    )

    assert res.status_code == 200
    datasets = json.loads(res.data.decode()).get("datasets")

    assert 2 == len(datasets)

def test_remove_role_dataset(client, db_session):
    """Owners should be able to remove role datasets."""
    headers = generate_auth_headers(client, user_id=3)

    res = client.delete(
        f"{role_route}/1/dataset", json={"datasets": [1]}, headers=headers
    )

    assert res.status_code == 200
    permissions = json.loads(res.data.decode()).get("datasets")

    assert len(permissions) == 0

def test_remove_missing_dataset(client, db_session):
    """Validate that owner cannot remove a dataset that is not in the role."""
    headers = generate_auth_headers(client, user_id=3)

    res = client.delete(
        f"{role_route}/1/dataset", json={"datasets": [1, 2]}, headers=headers
    )

    assert res.status_code == 400
    assert "not present" in res.data.decode()
