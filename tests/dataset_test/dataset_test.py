import json
from unittest.mock import patch

from tests.conftest import generate_auth_headers
from tests.conftest import dataset_route
import pytest



@pytest.fixture
def mock_api_call(mocker):
    return mocker.patch("botocore.client.BaseClient._make_api_call")

def test_update_owners(client, db_session, mock_api_call):
    """Verifies that a dataset owner is able to update the owner list."""
    headers = generate_auth_headers(client, user_id=3)

    res = client.put(
        f"{dataset_route}/1", headers=headers, json={"owners": [3, 4]}
    )
    assert res.status_code == 200

    headers = generate_auth_headers(client, user_id=4)
    res = client.get(f"{dataset_route}/1", headers=headers)
    assert res.status_code == 200
    owners = json.loads(res.data.decode()).get("owners")

    assert len(owners) == 2


def test_delete_dataset(client, db_session, mock_api_call):
    """Verifies that datasets can be deleted."""
    headers = generate_auth_headers(client, user_id=3)

    res = client.delete(f"{dataset_route}/1", headers=headers)

    assert 202 == res.status_code

def test_delete_missing_dataset(client, db_session):
    """Verifies that an error is thrown when a non-existent dataset is deleted."""
    headers = generate_auth_headers(client, user_id=3)

    res = client.delete(f"{dataset_route}/50", headers=headers)

    assert res.status_code == 404

def test_delete_unowned_dataset(client, db_session):
    """Verifies that an error is thrown when an unowned dataset is deleted."""
    headers = generate_auth_headers(client, user_id=1)

    res = client.delete(f"{dataset_route}/4", headers=headers)

    assert res.status_code == 401

def test_owner_get_dataset(client, db_session):
    headers = generate_auth_headers(client, user_id=3)

    res = client.get(f"{dataset_route}/1", headers=headers)

    assert 200 == res.status_code
