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
        f"{dataset_route}/1/owner", headers=headers, json={"owners": [3, 4]}
    )
    assert res.status_code == 200

    headers = generate_auth_headers(client, user_id=4)
    res = client.get(f"{dataset_route}/1", headers=headers)
    assert res.status_code == 200
    owners = json.loads(res.data.decode()).get("owners")

    assert len(owners) == 2
