import os

from loguru import logger
import requests

from core.errors import DatasetErrors
from models.associations import RoleDataset
from models.datasets.base import DatasetModel
from models.datasets.file import FileModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel

JOB_URL = f'http://{os.getenv("MODEL_HOST")}:{os.getenv("MODEL_PORT")}/predict/file'


def check_dataset_ownership(dataset: DatasetModel, user_id: int) -> bool:
    logger.info(f"Checking dataset ownership for dataset {dataset.dataset_id} and user {user_id}")

    return user_id in {x for x in dataset.owners}


def check_dataset_role_permissions(dataset_id: int, user_id: int) -> bool:
    """
    Check if the user is a member of a role that has access to a dataset.
    :param dataset_id: Dataset identifier to be accessed
    :param user_id: User ID requesting permission
    :return: Boolean representing authorization
    """
    logger.info(f"Checking permissions on dataset {dataset_id} for user {user_id}...")

    # Generate a list of roles that the user is a member of and that have access to the requested dataset
    roles: int = RoleModel.query.join(RoleMemberModel).join(RoleDataset)\
        .filter((user_id == user_id) & (dataset_id == dataset_id)).count()

    return roles > 0


def delete_datasets(dataset_ids: list) -> None:
    """
    Delete datasets and associated objects from the database.
    :param dataset_ids: List of dataset identifiers for datasets to delete
    :return: None
    """
    logger.info(f"Deleting datasets: {dataset_ids}")
    DatasetModel.query.filter((DatasetModel.dataset_id.in_(dataset_ids))).delete()


def retrieve_datasets(dataset_ids: list) -> list:
    """
    Retrieves a list of datasets by their IDs.
    :param dataset_ids: Dataset IDs to retrieve.
    :return: List of datasets
    """
    logger.info(f"Retrieving datasets: {dataset_ids}")
    datasets: list = DatasetModel.query.filter((DatasetModel.dataset_id.in_(dataset_ids))).all()

    if len(datasets) == 0:
        raise ValueError(DatasetErrors.DOES_NOT_EXIST, dataset_ids)

    return datasets


def retrieve_dataset(dataset_id: int) -> DatasetModel:
    """
    Retrieves a single dataset object by ID.
    :param dataset_id: Dataset ID to query
    :return: Dataset object
    """
    logger.info(f"Retrieving dataset {dataset_id}...")

    dataset: DatasetModel = DatasetModel.query.filter_by(dataset_id=dataset_id).first()

    if not dataset:
        raise ValueError(DatasetErrors.DOES_NOT_EXIST, dataset_id)

    return dataset


def retrieve_files(dataset_id: int) -> list:
    """
    Retrieves a list of all files applied to a particular dataset.
    :param dataset_id: Dataset identifier to be queried
    :return: List of file objects
    """
    logger.info(f"Retrieving files for dataset {dataset_id}")

    return FileModel.query.filter_by(dataset_id=dataset_id).all()


def send_job(job_id: int) -> None:
    """
    Sends a job request to the model server via an API call.
    :param job_id: Job ID to be initiated
    :return: None
    """
    logger.info(f"Sending job request {job_id} to model server...")

    payload: dict = {"job_id": job_id}

    try:
        r: requests.Response = requests.post(JOB_URL, json=payload)

        if not r.ok:
            raise ValueError(DatasetErrors.COULD_NOT_CREATE_JOB, job_id)

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

