import json
from unittest.mock import patch
from tests.conftest import generate_auth_headers
from tests.conftest import dataset_route

def test_get_dataset_shared_users(client, db_session):
    """Verify that owners are able to retrieve a list of users that have access to a dataset that they own."""
    headers = generate_auth_headers(client, user_id=3)
    res = client.get(f"{dataset_route}/1/user", headers=headers)

    assert res.status_code == 200
    shared_users = json.loads(res.data.decode())

    assert len(shared_users) == 2

def test_get_unowned_dataset_shared_users(client, db_session):
    """Users should not be able to view access for datasets they do not own."""
    headers = generate_auth_headers(client, user_id=1)
    res = client.get(f"{dataset_route}/1/user", headers=headers)

    assert res.status_code == 401

@patch("resources.datasets.shared_user.NotificationModel.send_notification_email")
def test_add_dataset_shared_user(self, mock_send_notif):
    """Owners should be able to add individual users to access their dataset."""
    headers = generate_auth_headers(client, user_id=3)
    res = client.post(
        f"{dataset_route}/1/user", headers=headers, json=[{"user_id": 5}]
    )

    assert res.status_code == 201

    res = client.get(f"{dataset_route}/1/user", headers=headers)

    assert res.status_code == 200
    shared_users = json.loads(res.data.decode())

    assert len(shared_users) == 3

def test_add_dataset_shared_user_already_owner(client, db_session):
    headers = generate_auth_headers(client, user_id=3)

    res = client.post(
        f"{dataset_route}/2/user", headers=headers, json=[{"user_id": 4}]
    )

    assert res.status_code == 400
    assert "cannot be shared with owner" == res.data.decode()

def test_add_dataset_shared_user_already_shared(client, db_session):
    headers = generate_auth_headers(client, user_id=3)

    res = client.post(
        f"{dataset_route}/1/user",
        headers=headers,
        json=[{"user_id": 1}, {"user_id": 2}],
    )

    assert res.status_code == 400
    assert "already shared" == res.data.decode()

def test_remove_dataset_shared_users(client, db_session):
    headers = generate_auth_headers(client, user_id=3)

    res = client.delete(
        f"{dataset_route}/1/user",
        headers=headers,
        json=[{"user_id": 1}, {"user_id": 2}],
    )

    assert res.status_code == 204

    res = client.get(f"{dataset_route}/1/user", headers=headers)
    shared_users = json.loads(res.data.decode())

    assert res.status_code == 200
    assert len(shared_users) == 0

@patch("resources.datasets.shared_user.NotificationModel.send_notification_email")
def test_add_dataset_shared_user_with_permissions(self, mock_send_notif):
    headers = generate_auth_headers(client, user_id=3)

    res = client.post(
        f"{dataset_route}/1/user",
        headers=headers,
        json=[
            {"user_id": 5, "permissions": ["ssn", "name"]},
            {"user_id": 4, "permissions": ["ssn"]},
        ],
    )

    assert res.status_code == 201

    res = client.get(f"{dataset_route}/1/user", headers=headers)

    assert res.status_code == 200
    shared_users = json.loads(res.data.decode())

    assert len(shared_users) == 4
    self.assertEqual(
        shared_users[2].get("permissions"),
        [
            {
                "description": "ssn",
                "long_description": "Social Security Number",
                "category": "Identity",
            },
            {
                "description": "name",
                "long_description": "Name",
                "category": "Identity",
            },
        ],
    )
    self.assertEqual(
        shared_users[3].get("permissions"),
        [
            {
                "description": "ssn",
                "long_description": "Social Security Number",
                "category": "Identity",
            }
        ],
    )
