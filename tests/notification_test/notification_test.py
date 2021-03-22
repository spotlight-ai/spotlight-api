import json
from tests.conftest import generate_auth_headers
from tests.conftest import notification_route


def test_retrieve_notifications(client, db_session):
    headers = generate_auth_headers(client, user_id=1)
    res = client.get("/notification", headers=headers)
    notifications = json.loads(res.data.decode())
    assert res.status_code == 200
    assert len(notifications) == 3
    notification = notifications[0].keys()
    assert "created_ts" in notification
    assert "viewed" in notification
    assert "last_updated_ts" in notification
    assert "notification_id" in notification
    assert "title" in notification
    assert "detail" in notification

    assert notifications[0].get("viewed") == False
    assert notifications[1].get("viewed") == False
    assert notifications[2].get("viewed") == True


def test_retrieve_notifications_user_with_none(client, db_session):
    headers = generate_auth_headers(client, user_id=3)
    res = client.get(notification_route, headers=headers)
    notifications = json.loads(res.data.decode())
    assert res.status_code == 200
    assert len(notifications) == 0


def test_retrieved_notifications_all_viewed(client, db_session):
    headers = generate_auth_headers(client, user_id=2)

    res = client.get(notification_route, headers=headers)

    notifications = json.loads(res.data.decode())

    assert res.status_code == 200
    assert len(notifications) == 1
    for notification in notifications:
        assert notification.get("viewed") == True


def test_update_notifications(client, db_session):

    headers = generate_auth_headers(client, user_id=2)

    res = client.patch(
        f"{notification_route}/4", headers=headers, json={"viewed": False}
    )

    notification = json.loads(res.data.decode())
    assert res.status_code == 200
    assert notification.get("last_updated_ts") != notification.get("created_ts")
    assert notification.get("viewed") == False
    



def test_update_notification_bad_keys(client, db_session):
    headers = generate_auth_headers(client, user_id=2)
    res = client.patch(
        f"{notification_route}/4",
        headers=headers,
        json={"viewed": False, "otherTitle": "New Title"},
    )


def test_update_notification_bad_keys(client, db_session):
    """Verifies that an error is thrown if a user tries to update invalid keys."""
    headers = generate_auth_headers(client, user_id=2)

    res = client.patch(
        f"{notification_route}/4",
        headers=headers,
        json={"viewed": False, "otherTitle": "New Title"},
    )

    assert res.status_code == 422

def test_update_notification_no_keys(client, db_session):
    """Verifies that an error is thrown if a user tries to update invalid keys."""
    headers = generate_auth_headers(client, user_id=2)

    res = client.patch(
        f"{notification_route}/4", headers=headers, json={},
    )

    notification = json.loads(res.data.decode())
    assert res.status_code == 200
    assert notification.get("title") == "Third Notification"
    assert notification.get("detail") == "More Detail"
    assert notification.get("viewed") == True


def test_update_notification_viewed_not_bool(client, db_session):
    """Verifies that an error is thrown if a user tries to update viewed with a non-boolean."""
    headers = generate_auth_headers(client, user_id=2)

    res = client.patch(
        f"{notification_route}/4", headers=headers, json={"viewed": "cat"},
    )

    assert res.status_code == 422


def test_update_notification_doesnt_exist(client, db_session):
    """Verifies that an error is thrown if a user tries to update viewed with a non-boolean."""
    headers = generate_auth_headers(client, user_id=2)

    res = client.patch(
        f"{notification_route}/59", headers=headers, json={"viewed": False},
    )

    assert 404 == res.status_code
    assert "Notification not found." in res.data.decode()

def test_update_notification_doesnt_own(client, db_session):
    """Verifies that an error is thrown if a user tries to update a notification that isn't theirs."""
    headers = generate_auth_headers(client, user_id=2)

    res = client.patch(
        f"{notification_route}/1", headers=headers, json={"viewed": False},
    )

    assert 401 == res.status_code
