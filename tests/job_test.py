import json
import os

from core.errors import AuthenticationErrors
from tests.conftest import generate_auth_headers, job_route


def test_valid_job_creation(client, db_session):
    """Ensures successful job creation by Dataset owner."""
    headers = generate_auth_headers(client, user_id=3)
    
    res = client.post(
        job_route, headers=headers, json={"dataset_id": 1}
    )
    
    assert res.status_code == 201
    assert res.data.decode() == "null\n"


def test_extra_field_job_creation(client, db_session):
    """Ensures failure upon job creation with extra field"""
    headers = generate_auth_headers(client, user_id=3)
    
    res = client.post(
        job_route, headers=headers, json={"dataset_id": 1, "name": "John"}
    )
    
    assert res.status_code == 422
    assert "Unknown field." in str(res.data)


def test_missing_field_job_creation(client, db_session):
    """Ensures failure upon job creation with missing field"""
    headers = generate_auth_headers(client, user_id=3)
    
    job_object = {"dataset_id": 1}
    
    wrong_job = job_object.copy()
    wrong_job.pop("dataset_id")
    
    res = client.post(job_route, headers=headers, json={})
    
    assert res.status_code == 422
    assert "Missing data for required field" in res.data.decode()


def test_retrieve_all_jobs(client, db_session):
    """Ensures that the owner of the Dataset is able to see all active jobs for that Dataset"""
    headers = generate_auth_headers(client, user_id=3)
    
    client.post(job_route, headers=headers, json={"dataset_id": 1})
    
    res = client.get(job_route, headers=headers)
    response_body = json.loads(res.data.decode())
    
    assert res.status_code == 200
    assert len(response_body) == 1


def test_missing_auth_retrieve_all_jobs(client, db_session):
    """Ensures that if the owner of the Dataset is not logged in,
    they won't be able to see all of the jobs"""
    res = client.get(job_route)
    
    assert res.status_code == 400
    assert AuthenticationErrors.MISSING_AUTH_HEADER in res.data.decode()


def test_incorrect_auth_retrieve_all_jobs(client, db_session):
    """Ensures that if the individual trying to retrieve all jobs associated with the Dataset is
    not the owner of the Dataset, they will not be able to see the jobs"""
    incorrect_header = {"authorization": "Bearer wrong"}
    
    res = client.get(job_route, headers=incorrect_header)
    
    assert res.status_code == 401


def test_incorrect_user_create_job(client, db_session):
    """Ensures that if the individual trying to create a job is not the owner of the Dataset,
    they will not be able to create a job"""
    headers = generate_auth_headers(client, user_id=1)
    
    res = client.post(
        job_route, headers=headers, json={"dataset_id": 1}
    )
    
    assert res.status_code == 401


def test_nonexistent_dataset_job_creation(client, db_session):
    """Ensures that if an individual attempts to create a job for a Dataset that doesn't exist,
    they will not be permitted to do so"""
    headers = generate_auth_headers(client, user_id=3)
    
    res = client.post(
        job_route, headers=headers, json={"dataset_id": 9}
    )
    
    assert res.status_code == 404


def test_access_all_active_jobs_all_datasets_user(client, db_session):
    """Ensures that if a user attempts to access all jobs for all Datasets (they own no Datasets)
    they will be refused"""
    header_user1 = generate_auth_headers(client, user_id=1)
    header_user3 = generate_auth_headers(client, user_id=3)
    header_user4 = generate_auth_headers(client, user_id=4)
    
    # User 3 posts a job for each Dataset they own
    client.post(job_route, headers=header_user3, json={"dataset_id": 1})
    client.post(job_route, headers=header_user3, json={"dataset_id": 2})
    client.post(job_route, headers=header_user3, json={"dataset_id": 3})
    
    # User 4 posts a job the Dataset they own
    client.post(job_route, headers=header_user4, json={"dataset_id": 4})
    
    # User 1 attempts to access jobs from all of these Datasets, none of which they own
    res1 = client.get(f"{job_route}/1", headers=header_user1)
    res2 = client.get(f"{job_route}/2", headers=header_user1)
    res3 = client.get(f"{job_route}/3", headers=header_user1)
    res4 = client.get(f"{job_route}/4", headers=header_user1)
    
    assert res1.status_code == 401
    assert res2.status_code == 401
    assert res3.status_code == 401
    assert res4.status_code == 401


def test_access_all_active_jobs_all_datasets_owner(client, db_session):
    """Ensures that if a user attempts to access all jobs for all Datasets (including Datasets
    that they don't own) they will be refused"""
    header_user3 = generate_auth_headers(client, user_id=3)
    header_user4 = generate_auth_headers(client, user_id=4)
    
    # User 3 posts a job for each Dataset they own
    client.post(job_route, headers=header_user3, json={"dataset_id": 1})
    client.post(job_route, headers=header_user3, json={"dataset_id": 2})
    client.post(job_route, headers=header_user3, json={"dataset_id": 3})
    
    # User 4 posts a job for the Dataset they own
    client.post(job_route, headers=header_user4, json={"dataset_id": 4})
    
    # User 3 attempts to access all of the jobs pertaining to their Dataset as well
    # as a job that doesn't belong to their Dataset
    res1 = client.get(f"{job_route}/1", headers=header_user3)
    res2 = client.get(f"{job_route}/2", headers=header_user3)
    res3 = client.get(f"{job_route}/3", headers=header_user3)
    res4 = client.get(f"{job_route}/4", headers=header_user3)
    
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res3.status_code == 200
    assert res4.status_code == 401


def test_access_all_active_jobs_all_datasets_admin(client, db_session):
    """Ensures that if an administrator attempts to access all jobs for all Datasets
    (including Datasets that they don't own) they will be granted permission"""
    header_user5 = generate_auth_headers(client, user_id=5)
    header_user3 = generate_auth_headers(client, user_id=3)
    header_user4 = generate_auth_headers(client, user_id=4)
    
    # User 3 posts a job for each Dataset they own
    client.post(job_route, headers=header_user3, json={"dataset_id": 1})
    client.post(job_route, headers=header_user3, json={"dataset_id": 2})
    client.post(job_route, headers=header_user3, json={"dataset_id": 3})
    
    # User 4 posts a job the Dataset they own
    client.post(job_route, headers=header_user4, json={"dataset_id": 4})
    
    # Admin attempts to see all jobs associated with all Datasets
    res1 = client.get(f"{job_route}/1", headers=header_user5)
    res2 = client.get(f"{job_route}/2", headers=header_user5)
    res3 = client.get(f"{job_route}/3", headers=header_user5)
    res4 = client.get(f"{job_route}/4", headers=header_user5)
    
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res3.status_code == 200
    assert res4.status_code == 200


def test_access_nonexistent_job(client, db_session):
    """Ensures that the Dataset owner will receive an error if they try to access a job that does
    not exist"""
    headers = generate_auth_headers(client, user_id=3)
    
    res = client.get(f"{job_route}/1", headers=headers)
    
    assert res.status_code == 404


def test_change_job_status_user(client, db_session):
    """Ensures that users are unable to change job status"""
    header_user3 = generate_auth_headers(client, user_id=3)
    
    # User 3 posts a job for a Dataset they own
    client.post(
        f"{job_route}/1", headers=header_user3, json={"dataset_id": 1}
    )
    
    res = client.patch(
        f"{job_route}/1",
        headers=header_user3,
        json={"user_id": 3, "job_id": 1, "job_status": "FAILED"},
    )
    assert res.status_code == 404


def test_change_job_status_model(client, db_session):
    """Ensures that the model is able to change job status"""
    header_user3 = generate_auth_headers(client, user_id=3)
    # header_model = generate_auth_headers("MODEL_KEY")
    model_header = {"authorization": f'Bearer {os.environ.get("MODEL_KEY")}'}
    
    # User 3 posts three jobs for Datasets they own
    client.post(job_route, headers=header_user3, json={"dataset_id": 1})
    client.post(job_route, headers=header_user3, json={"dataset_id": 2})
    client.post(job_route, headers=header_user3, json={"dataset_id": 3})
    
    res1 = client.patch(
        f"{job_route}/1",
        headers=model_header,
        json={"user_id": 3, "job_id": 2, "job_status": "FAILED"},
    )
    
    res2 = client.patch(
        f"{job_route}/2",
        headers=model_header,
        json={"user_id": 3, "job_id": 2, "job_status": "COMPLETE"},
    )
    
    res3 = client.patch(
        f"{job_route}/3",
        headers=model_header,
        json={"user_id": 3, "job_id": 3, "job_status": "PENDING"},
    )
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res3.status_code == 200
