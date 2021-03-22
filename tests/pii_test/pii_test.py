import json

from tests.conftest import generate_auth_headers
from tests.conftest import pii_route


def test_retrieve_pii(client, db_session):
    """Verifies that all PII markers can be retrieved."""
    headers = generate_auth_headers(client, user_id=1)

    res = client.get(pii_route, headers=headers)

    pii = json.loads(res.data.decode())

    assert 200 == res.status_code
    assert 3 == len(pii)
    assert "description" in pii[0]
    assert "long_description" in pii[0]
    assert "category" in pii[0]

def test_unauthenticated_retrieve_pii(client, db_session):
    """Verifies that unauthenticated users cannot retrieve the PII list."""
    res = client.get(pii_route)

    assert 400 == res.status_code
