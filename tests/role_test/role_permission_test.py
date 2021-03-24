import json

from tests.conftest import generate_auth_headers
from tests.conftest import role_route


def test_get_role_permissions(client, db_session):
    """Role owner should be able to retrieve permissions assigned to a given role."""
    headers = generate_auth_headers(client, user_id=4)

    res = client.get(f"{role_route}/1/permission", headers=headers)

    assert res.status_code == 200
    permissions = json.loads(res.data.decode())
    assert len(permissions) == 1
    assert permissions[0].get("description") == "ssn"

def test_get_role_permissions_unowned_role(client, db_session):
    """User of an unowned role should not be able to see permission details."""
    headers = generate_auth_headers(client, user_id=2)

    res = client.get(f"{role_route}/1/permission", headers=headers)

    assert res.status_code == 401
    assert "Role either does not exist or user does not have permissions." in res.data.decode()

def test_add_new_role_permission(client, db_session):
    """Tests that a role owner can add an individual permission to a role."""
    headers = generate_auth_headers(client, user_id=4)

    res = client.post(
        f"{role_route}/1/permission",
        headers=headers,
        json={"permissions": ["name"]},
    )

    assert res.status_code == 201

    res = client.get(f"{role_route}/1/permission", headers=headers)
    permissions = json.loads(res.data.decode())

    assert res.status_code == 200
    assert len(permissions) == 2

def test_add_multiple_permissions(client, db_session):
    """Verify that owners can add multiple permissions at once to a role."""
    headers = generate_auth_headers(client, user_id=4)

    res = client.post(
        f"{role_route}/1/permission",
        headers=headers,
        json={"permissions": ["address", "name"]},
    )

    assert res.status_code == 201

    res = client.get(f"{role_route}/1/permission", headers=headers)
    permissions = json.loads(res.data.decode())

    assert res.status_code == 200
    assert len(permissions) == 3

def test_add_same_permission(client, db_session):
    """Owners should not be able to add the same permission to a role."""
    headers = generate_auth_headers(client, user_id=4)

    res = client.post(
        f"{role_route}/1/permission",
        headers=headers,
        json={"permissions": ["ssn", "name"]},
    )

    assert res.status_code == 400
    assert "Permissions already present: ['ssn']" in res.data.decode()

    res = client.get(f"{role_route}/1/permission", headers=headers)
    permissions = json.loads(res.data.decode())

    assert len(permissions) == 1

def test_update_role_permissions(client, db_session):
    """Owners should be able to overwrite role permissions."""
    headers = generate_auth_headers(client, user_id=4)

    res = client.put(
        f"{role_route}/1/permission",
        json={"permissions": ["address"]},
        headers=headers,
    )

    assert res.status_code == 200
    permissions = json.loads(res.data.decode()).get("permissions")

    assert len(permissions) == 1
    assert permissions[0].get("description") == "address"

def test_remove_role_permission(client, db_session):
    """Owners should be able to remove role permissions."""
    headers = generate_auth_headers(client, user_id=4)

    res = client.delete(
        f"{role_route}/1/permission",
        json={"permissions": ["ssn"]},
        headers=headers,
    )

    assert res.status_code == 200
    permissions = json.loads(res.data.decode()).get("permissions")

    assert len(permissions) == 0

def test_remove_missing_permission(client, db_session):
    """Owners should not be able to remove role permissions that do not exist."""
    headers = generate_auth_headers(client, user_id=4)

    res = client.delete(
        f"{role_route}/1/permission",
        json={"permissions": ["name"]},
        headers=headers,
    )

    assert res.status_code == 400
    assert "Permissions missing: ['name']" in res.data.decode()
