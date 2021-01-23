import typing
import os

from loguru import logger
import requests
from sqlalchemy import orm
from sqlalchemy.sql import true

from core.errors import DatasetErrors, FileErrors
from db import db
from models.associations import RoleDataset
from models.datasets.base import DatasetModel
from models.datasets.file import FileModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel

JOB_URL = f'http://{os.getenv("MODEL_HOST")}:{os.getenv("MODEL_PORT")}/predict/file'


def check_dataset_ownership(dataset: DatasetModel, user_id: int) -> bool:
    logger.info(f"Checking dataset ownership for dataset {dataset.dataset_id} and user {user_id}")

    return user_id in {x.user_id for x in dataset.owners}


def check_dataset_role_permissions(dataset_id: int, user_id: int) -> tuple:
    """
    Check if the user is a member of a role that has access to a dataset.
    :param dataset_id: Dataset identifier to be accessed
    :param user_id: User ID requesting permission
    :return: Boolean representing authorization
    """
    logger.info(f"Checking permissions on dataset {dataset_id} for user {user_id}...")

    # Generate a list of roles that the user is a member of and that have access to the requested dataset
    roles: list = RoleModel.query.join(RoleMemberModel).join(RoleDataset)\
        .filter((user_id == user_id) & (dataset_id == dataset_id)).all()

    return len(roles) > 0, roles


def delete_datasets(dataset_ids: list) -> None:
    """
    Delete datasets and associated objects from the database.
    :param dataset_ids: List of dataset identifiers for datasets to delete
    :return: None
    """
    logger.info(f"Deleting datasets: {dataset_ids}")
    DatasetModel.query.filter(DatasetModel.dataset_id.in_(dataset_ids)).delete(synchronize_session=False)
    db.session.commit()


def retrieve_datasets(dataset_ids: list, owner_only: bool = False, user_id: typing.Optional[int] = None,
                      verified_only: bool = False) -> list:
    """
    Retrieves a list of datasets by their IDs.
    :param dataset_ids: Dataset IDs to retrieve.
    :param owner_only: Retrieve datasets that are owned by a particular user
    :param user_id: Required if owner_only is True
    :param verified_only: Retrieve only verified datasets
    :return: List of datasets
    """
    logger.info(f"Retrieving datasets: {dataset_ids}")

    query: orm.query = DatasetModel.query.filter(DatasetModel.dataset_id.in_(dataset_ids))

    if owner_only:
        if not user_id:
            raise ValueError(DatasetErrors.MUST_SUPPLY_USER_ID)
        query.filter(DatasetModel.owners.contains(user_id))

    if verified_only:
        query.filter(DatasetModel.verified == true())

    datasets: list = query.all()

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


def retrieve_file(file_id: int, dataset_id: int) -> FileModel:
    """
    Retrieves a single File object.
    :param file_id: File identifier to be requested
    :param dataset_id: Dataset identifier that maintains the file
    :return: File object
    """
    logger.info(f"Retrieving file {file_id}...")

    file: FileModel = FileModel.query.filter_by(file_id=file_id, dataset_id=dataset_id).first()

    if not file:
        raise ValueError(FileErrors.FILE_NOT_FOUND, file_id)

    return file


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

