import json
from unittest.mock import patch

from tests.conftest import generate_auth_headers, role_route


def test_get_role_members(client, db_session):
    """Retrieves all members for a given role."""
    headers = generate_auth_headers(client, user_id=3)
    
    res = client.get(f"{role_route}/1/member", headers=headers)
    
    members = json.loads(res.data.decode())
    
    assert res.status_code == 200
    assert len(members) == 3


def test_get_role_members_missing_role(client, db_session):
    """Verifies that an error is thrown when requested role does not exist."""
    headers = generate_auth_headers(client)
    
    res = client.get(f"{role_route}/10/member", headers=headers)
    
    assert res.status_code == 401
    assert "Role either does not exist or user does not have permissions." in res.data.decode()


def test_add_owner_to_unowned_role(client, db_session):
    """Verifies that an error is thrown if a user tries to add an owner to a role they don't own."""
    headers = generate_auth_headers(client)
    
    res = client.post(
        f"{role_route}/2/member",
        json={"owners": [2], "users": [3]},
        headers=headers,
    )
    
    assert res.status_code == 401
    assert "Role either does not exist or user does not have permissions." in res.data.decode()


def test_add_owner(client, db_session):
    """Adds an owner to a role."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.post(
        f"{role_route}/1/member",
        json={"owners": [2], "users": []},
        headers=headers,
    )
    
    assert res.status_code == 201
    
    res = client.get(f"{role_route}/1/member", headers=headers)
    members = json.loads(res.data.decode())
    
    assert res.status_code == 200
    assert len(members) == 4


@patch("resources.roles.role_member.send_notifications")
def test_add_members(self, mock_notif):
    """Adds multiple members to a role."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.post(
        f"{role_route}/1/member",
        json={"owners": [], "users": [5, 6]},
        headers=headers,
    )
    
    assert res.status_code == 201
    
    res = client.get(f"{role_route}/1/member", headers=headers)
    members = json.loads(res.data.decode())
    
    assert res.status_code == 200
    assert len(members) == 5
    
    owner_count = 0
    
    for member in members:
        if member.get("is_owner"):
            owner_count += 1
    
    assert owner_count == 2


@patch("resources.roles.role_member.send_notifications")
def test_add_combo(self, mock_notif):
    """Adds a combination of users and owners."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.get(f"{role_route}/1/member", headers=headers)
    members = json.loads(res.data.decode())
    res = client.post(
        f"{role_route}/1/member",
        json={"owners": [5], "users": [2]},
        headers=headers,
    )
    
    assert res.status_code == 201
    
    res = client.get(f"{role_route}/1/member", headers=headers)
    members = json.loads(res.data.decode())
    
    assert res.status_code == 200
    assert len(members) == 5
    
    owner_count = 0
    
    for member in members:
        if member.get("is_owner"):
            owner_count += 1
    
    assert owner_count == 3


@patch("resources.roles.role_member.send_notifications")
def test_replace_combo(self, mock_notif):
    """Replaces role members and owners with new sets."""
    headers = generate_auth_headers(client, user_id=3)
    member_path = f"{role_route}/1/member"
    
    res = client.put(
        member_path,
        json={"owners": [2, 3], "users": [4]},
        headers=headers,
    )
    
    assert 200 == res.status_code
    
    res = client.get(member_path, headers=headers)
    members = json.loads(res.data.decode())
    
    assert 200 == res.status_code
    assert 3 == len(members)
    
    owner_count = 0
    
    for member in members:
        if member.get("is_owner"):
            owner_count += 1
    
    assert owner_count == 2


def test_add_existing_combo(client, db_session):
    """Should not be able to add owners or members that already exist."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.post(
        f"{role_route}/1/member",
        json={"owners": [4], "users": [2]},
        headers=headers,
    )
    
    assert res.status_code == 400
    assert "Role member already exists." in res.data.decode()


def test_wrong_key(client, db_session):
    """Validates that an error is thrown when the wrong key is placed in the request body."""
    headers = generate_auth_headers(client)
    
    res = client.post(
        f"{role_route}/1/member",
        json={"owners": [2], "members": [3]},
        headers=headers,
    )
    
    assert res.status_code == 422
    assert "Body must have only the accepted keys: ['owners', 'users']" in res.data.decode()


def test_delete_all_owners(client, db_session):
    """Validates that an error is thrown when all owners are deleted."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.delete(
        f"{role_route}/1/member",
        json={"owners": [3, 4], "members": []},
        headers=headers,
    )
    
    assert res.status_code == 400
    assert "Role must have at least one owner." in res.data.decode()


def test_delete_owner(client, db_session):
    """Validates that an owner may be deleted by another owner."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.delete(
        f"{role_route}/1/member",
        json={"owners": [3], "members": []},
        headers=headers,
    )
    
    assert res.status_code == 200
    
    res = client.get(f"{role_route}/1/member", headers=headers)
    members = json.loads(res.data.decode())
    
    assert len(members) == 2
    
    owner_count = 0
    for member in members:
        if member.get("is_owner"):
            owner_count += 1
    
    assert owner_count == 1


def test_delete_combo(client, db_session):
    """Validates that multiple members may be deleted at once."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.delete(
        f"{role_route}/1/member",
        json={"owners": [3], "members": [1]},
        headers=headers,
    )
    
    assert res.status_code == 200
    
    res = client.get(f"{role_route}/1/member", headers=headers)
    members = json.loads(res.data.decode())
    
    assert len(members) == 1
    
    owner_count = 0
    for member in members:
        if member.get("is_owner"):
            owner_count += 1
    
    assert owner_count == 1


def test_put_empty_owners(client, db_session):
    """Validates that a blank owner list is not replacing the old owner list."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.put(
        f"{role_route}/1/member",
        json={"owners": [], "users": [4]},
        headers=headers,
    )
    
    assert res.status_code == 400
    assert "Role must have at least one owner." in res.data.decode()
