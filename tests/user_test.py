import json
from core.errors import AuthenticationErrors
from tests.conftest import generate_auth_headers
from tests.conftest import user_route


def test_valid_user_creation(client, db_session):
    """Validates that a user can be created with an entirely correct body."""
    res = client.post(
        user_route,
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@user.com",
            "password": "testpass",
        },
    )
    assert 201 == res.status_code
    assert "null\n" == res.data.decode()

def test_duplicate_user_creation(client, db_session):
    """Validates that an error is thrown if a user with the same e-mail address already exists."""
    res = client.post(
        user_route,
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "dana@spotlight.ai",
            "password": "testpassword",
        },
    )

    assert 400 == res.status_code
    assert "User already exists." in res.data.decode()
    
def test_blank_input_user_creation(client, db_session):
    """Validates that each input must meet the expected criteria before creating the user."""
    res = client.post(
        user_route,
        json={"email": "", "password": "", "first_name": "", "last_name": ""},
    )

    assert 422 == res.status_code
    response = res.data.decode()
    assert "Not a valid email address." in response
    assert "Shorter than minimum length 8." in response
    assert "Shorter than minimum length 1." in response

def test_some_blank_fields(client, db_session):
    """Validates that errors are thrown even when some inputs are valid."""
    res = client.post(
        user_route,
        json={
            "email": "test@user.com",
            "password": "testpassword",
            "first_name": "",
            "last_name": "",
        },
    )

    assert 422 == res.status_code
    assert "Shorter than minimum length 1." in res.data.decode()

def test_extra_field_user_creation(client, db_session):
    """Validates that an error is thrown when extra fields are present."""
    res = client.post(
        user_route,
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@user.com",
            "password": "testpass",
            "middle_name": "Middle",
        },
    )

    assert 422 == res.status_code
    assert "Unknown field." in str(res.data)

def test_missing_field_user_creation(client, db_session):
    """Validates that an error is thrown when fields are missing."""
    res = client.post(
        user_route,
        json={"first_name": "Test", "last_name": "User", "email": "test@user.com"},
    )

    assert 422 == res.status_code
    assert "Missing data for required field." in res.data.decode()

def test_password_too_short(client, db_session):
    """Validates that passwords must be of a certain length."""
    res = client.post(
        user_route,
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@user.com",
            "password": "test",
        },
    )

    assert 422 == res.status_code
    assert "Shorter than minimum length 8." in res.data.decode()

def test_invalid_email_format(client, db_session):
    """Validates that email addresses must be a valid format."""
    res = client.post(
        user_route,
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test.com",
            "password": "testpass",
        },
    )

    assert 422 == res.status_code
    assert "Not a valid email address." in res.data.decode()

def test_invalid_user_update(client, db_session):
    """Validates that user e-mails cannot be updated."""
    headers = generate_auth_headers(client, user_id=1)
    res = client.patch(
        f"{user_route}/1", json={"email": "new@spotlight.ai"}, headers=headers,
    )

    assert 400 == res.status_code
    assert "Cannot edit this field." in res.data.decode()

def test_retrieve_all_users(client, db_session):
    """Verifies that all users can be successfully retrieved."""
    headers = generate_auth_headers(client, user_id=2)

    res = client.get(user_route, headers=headers)
    response_body = json.loads(res.data.decode())

    assert 200 == res.status_code
    number_of_users_available_spotlightai_public = 5
    assert number_of_users_available_spotlightai_public == len(response_body)

def test_missing_auth_retrieve_all_users(client, db_session):
    """Verifies that users cannot be retrieved without an authorization token."""
    res = client.get(user_route)

    assert 400 == res.status_code
    assert AuthenticationErrors.MISSING_AUTH_HEADER in res.data.decode()

def test_incorrect_auth_retrieve_all_users(client, db_session):
    """Verifies that users cannot be retrieved with an incorrect authorization token."""
    incorrect_header = {"authorization": "Bearer wrong"}

    res = client.get(user_route, headers=incorrect_header)

    assert 401 == res.status_code

def test_filter_user_list(client, db_session):
    """Verifies that the user list can be filtered based on a query."""
    headers = generate_auth_headers(client, user_id=2)

    res = client.get(f"{user_route}?query=doug", headers=headers)
    response_body = json.loads(res.data.decode())

    assert 200 == res.status_code
    """Doug belongs to a different domain so should return empty"""
    assert 0 == len(response_body)

    res = client.get(f"{user_route}", headers=headers)
    response_body = json.loads(res.data.decode())

    assert 200 == res.status_code
    """Dana should see every one from her domain and public users"""
    assert 5 == len(response_body)

    res = client.get(f"{user_route}?query=rando", headers=headers)
    response_body = json.loads(res.data.decode())

    assert 200 == res.status_code
    """Dana should be able to see public user"""
    assert 1 == len(response_body)

    res = client.get(f"{user_route}?query=manager", headers=headers)
    response_body = json.loads(res.data.decode())

    assert 200 == res.status_code
    assert 2 == len(response_body)

    res = client.get(f"{user_route}?query=dana@spotli", headers=headers)
    response_body = json.loads(res.data.decode())

    assert 200 == res.status_code
    """Dana cant search for her own user details"""
    assert 0 == len(response_body)

def test_update_user(client, db_session):
    """Verifies that user information can be updated."""
    headers = generate_auth_headers(client, user_id=1)

    res = client.patch(
        f"{user_route}/1",
        headers=headers,
        json={"first_name": "New", "last_name": "User"},
    )

    assert 200 == res.status_code

    user = json.loads(res.data.decode())

    assert "New" == user.get("first_name")
    assert "User" == user.get("last_name")

def test_delete_user(client, db_session):
    """Verifies that a user can be deleted."""
    # TODO: test for admin only access to delete?

    test_user = 1
    path = f"{user_route}/{test_user}"

    headers = generate_auth_headers(client, user_id=test_user)

    res = client.delete(path, headers=headers)

    assert 200 == res.status_code

    res = client.get(path, headers=headers)
    user_message = json.loads(res.data.decode())
    assert "User or users not found." == user_message["message"]

def test_get_individual_user(client, db_session):
    """Verifies that individual user information can be fetched."""
    headers = generate_auth_headers(client, user_id=1)

    res = client.get(f"{user_route}/1", headers=headers)

    assert 200 == res.status_code

    user = json.loads(res.data.decode())
    assert "doug@spotlightai.com" == user.get("email")

def test_update_user_invalid_input(client, db_session):
    """Verifies that fields are valid when updating a user."""
    headers = generate_auth_headers(client, user_id=1)
    res = client.patch(
        f"{user_route}/1", json={"first_name": ""}, headers=headers,
    )

    assert 422 == res.status_code
    assert "Shorter than minimum length 1." in res.data.decode()

def test_get_user_doesnt_exist(client, db_session):
    """Verifies that an error is thrown when a non-existent user is fetched."""
    headers = generate_auth_headers(client, user_id=1)

    res = client.get(f"{user_route}/0", headers=headers)

    assert 404 == res.status_code

def test_patch_user_doesnt_exist(client, db_session):
    """Verifies that an error is thrown when a non-existent user is updated."""
    headers = generate_auth_headers(client, user_id=1)
    res = client.patch(
        f"{user_route}/0", json={"first_name": ""}, headers=headers,
    )

    assert 404 == res.status_code
