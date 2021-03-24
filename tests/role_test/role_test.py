import json

from core.errors import AuthenticationErrors
from tests.conftest import generate_auth_headers, role_route

role_object = {"role_name": "Test Role"}


def test_create_role(client, db_session):
    """Tests functionality of creating a role with a single owner. The role should be returned."""
    headers = generate_auth_headers(client)
    res = client.post(
        role_route, json=role_object, headers=headers
    )
    
    assert 201 == res.status_code
    assert role_object.get("role_name") in res.data.decode()
    
    res = client.get(role_route, headers=headers)
    members = json.loads(res.data.decode())[0].get("members")
    
    assert len(members) == 1
    assert members[0].get("is_owner") == True


def test_create_role_multiple_owners(client, db_session):
    """Tests functionality of creating a role with more than one owner."""
    headers = generate_auth_headers(client)
    
    new_role = role_object.copy()
    new_role["owners"] = [1, 2]
    
    res = client.post(role_route, json=new_role, headers=headers)
    assert res.status_code == 201
    
    res = client.get(role_route, headers=headers)
    members = json.loads(res.data.decode())[0].get("members")
    
    assert len(members) == 2
    assert members[0].get("is_owner") == True
    assert members[1].get("is_owner") == True


def test_create_role_creator_not_owner(client, db_session):
    """Creator should not be able to create a dataset where they are not an owner."""
    headers = generate_auth_headers(client)
    
    new_role = role_object.copy()
    new_role["owners"] = [2, 3]
    
    res = client.post(role_route, json=new_role, headers=headers)
    assert res.status_code == 400
    assert "Creator must be listed as a dataset owner." in res.data.decode()


def test_create_role_authentication(client, db_session):
    """Ensures that role endpoints require authentication."""
    res = client.post(role_route, json=role_object)
    assert res.status_code == 400
    assert AuthenticationErrors.MISSING_AUTH_HEADER in res.data.decode()
    
    res = client.get(role_route)
    
    assert res.status_code == 400
    assert AuthenticationErrors.MISSING_AUTH_HEADER in res.data.decode()
    
    res = client.get(f"{role_route}/1")
    assert res.status_code == 400
    assert AuthenticationErrors.MISSING_AUTH_HEADER in res.data.decode()
    
    res = client.delete(f"{role_route}/1")
    assert res.status_code == 400
    assert AuthenticationErrors.MISSING_AUTH_HEADER in res.data.decode()


def test_get_roles(client, db_session):
    """Tests GET /role endpoint. Should return only roles owned by the requester."""
    headers = generate_auth_headers(client)
    
    res = client.get(role_route, headers=headers)
    roles = json.loads(res.data.decode())
    assert res.status_code == 200
    assert len(roles) == 0
    
    client.post(role_route, json=role_object, headers=headers)
    res = client.get(role_route, headers=headers)
    roles = json.loads(res.data.decode())
    
    assert res.status_code == 200
    assert len(roles) == 1


def test_get_single_role(client, db_session):
    """Get a single, existing role."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.get(f"{role_route}/1", headers=headers)
    role = json.loads(res.data.decode())
    assert res.status_code == 200
    assert role.get("role_name") == "Financial Developers"


def test_get_missing_role(client, db_session):
    """Attempt to retrieve a role that doesn't exist."""
    headers = generate_auth_headers(client)
    
    res = client.get(f"{role_route}/10", headers=headers)
    assert res.status_code == 404
    assert "Role either does not exist or user does not have permissions." in res.data.decode()


def test_get_unowned_role(client, db_session):
    headers = generate_auth_headers(client, user_id=2)
    
    res = client.get(f"{role_route}/2", headers=headers)
    assert res.status_code == 404
    assert "Role either does not exist or user does not have permissions." in res.data.decode()


def test_delete_role(client, db_session):
    """Attempt to retrieve a role that doesn't exist."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.delete(f"{role_route}/1", headers=headers)
    assert res.status_code == 200


def test_delete_missing_role(client, db_session):
    """Attempt to retrieve a role that doesn't exist."""
    headers = generate_auth_headers(client)
    
    res = client.delete(f"{role_route}/10", headers=headers)
    assert res.status_code == 404
    assert "Role either does not exist or user does not have permissions." in res.data.decode()


def test_update_role_name(client, db_session):
    """Owners should be able to update a role's name."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.patch(
        f"{role_route}/1",
        json={"role_name": "Updated Role Name"},
        headers=headers,
    )
    assert res.status_code == 200
    role = json.loads(res.data.decode())
    
    assert role.get("role_name") == "Updated Role Name"


def test_update_unowned_role(client, db_session):
    """Users should not be able to update roles they do not own."""
    headers = generate_auth_headers(client, user_id=2)
    
    res = client.patch(
        f"{role_route}/1",
        json={"role_name": "Updated Role Name"},
        headers=headers,
    )
    assert res.status_code == 404
    assert "Role either does not exist or user does not have permissions." in res.data.decode()


def test_update_owners(client, db_session):
    """Owners should be able to update owner list for roles."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.patch(
        f"{role_route}/1", json={"owners": [2, 3]}, headers=headers
    )
    assert res.status_code == 200
    role = json.loads(res.data.decode())
    
    owner_ids = []
    for member in role.get("members"):
        if member.get("is_owner"):
            owner_ids.append(member.get("user").get("user_id"))
    
    assert owner_ids, [2 == 3]


def test_update_multiple_role_properties(client, db_session):
    """Owners should be able to update multiple properties at once for roles."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.patch(
        f"{role_route}/1",
        json={"owners": [2, 3, 4], "role_name": "Other Role"},
        headers=headers,
    )
    assert res.status_code == 200
    role = json.loads(res.data.decode())
    
    assert role.get("role_name") == "Other Role"
    
    owner_ids = []
    for member in role.get("members"):
        if member.get("is_owner"):
            owner_ids.append(member.get("user").get("user_id"))
    
    assert owner_ids, [2, 3 == 4]


def test_update_empty_owners(client, db_session):
    """Owners should be able to update owner list for roles."""
    headers = generate_auth_headers(client, user_id=4)
    
    res = client.patch(
        f"{role_route}/1", json={"owners": []}, headers=headers
    )
    assert res.status_code == 400
    assert "Role must have at least one owner." in res.data.decode()
