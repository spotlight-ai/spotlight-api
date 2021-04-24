import typing

from flask import abort, request
from flask_restful import Resource
from loguru import logger
from sqlalchemy.sql.expression import true

from core import aws as aws_util
from core.constants import AuditConstants, UserConstants
from core.decorators import authenticate_token
from core.errors import DatasetErrors
from db import db
from models.associations import RoleDataset
from models.audit.dataset_action_history import DatasetActionHistoryModel
from models.auth.user import UserModel
from models.datasets.base import DatasetModel
from models.datasets.file import FileModel
from models.job import JobModel
from models.pii.pii import PIIModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel
from resources.datasets import util as dataset_util
from schemas.datasets.base import DatasetSchema
from schemas.datasets.file import FileSchema
from schemas.job import JobSchema

flat_file_dataset_schema = FileSchema()
dataset_schema = DatasetSchema()
job_schema = JobSchema()


class Dataset(Resource):
    """
    Resource for manipulating individual Dataset objects.
    """

    @authenticate_token
    def get(self, user_id: int, dataset_id: int) -> dict:
        """
        Retrieves metadata for a dataset.
        :param user_id: User ID requesting the dataset information
        :param dataset_id: Dataset identifier to be retrieved
        :return: Dataset metadata object
        """
        is_model: bool = user_id == "MODEL"  # Is the model requesting the metadata?

        dataset: typing.Optional[DatasetModel] = None

        try:
            dataset = dataset_util.retrieve_dataset(dataset_id)
        except ValueError as e:
            logger.error(e.args)
            abort(404, e.args[0])

        is_owner: bool = dataset_util.check_dataset_ownership(dataset, user_id)

        if is_model or is_owner:
            return dataset_schema.dump(dataset)
        else:
            is_shared, _ = dataset_util.check_dataset_role_permissions(dataset_id, user_id)

            if is_shared:
                return dataset_schema.dump(dataset)

        abort(401, DatasetErrors.NOT_AUTHORIZED)

    @authenticate_token
    def delete(self, user_id: int, dataset_id: int) -> tuple:
        """
        Deletes a dataset from the system.
        :param user_id: Currently logged in user ID.
        :param dataset_id: Dataset unique identifier to delete
        :return: None
        """
        dataset: typing.Optional[DatasetModel] = None

        try:
            dataset = dataset_util.retrieve_dataset(dataset_id)
        except ValueError as e:
            logger.error(e.args)
            abort(404, e.args[0])

        if not dataset_util.check_dataset_ownership(dataset, user_id):
            abort(401, DatasetErrors.USER_DOES_NOT_OWN)

        files: list = dataset_util.retrieve_files(dataset_id)

        for file_object in files:
            aws_util.dataset_cleanup(file_object.location)

        dataset_util.delete_datasets([dataset_id])
        return None, 202


class DatasetCollection(Resource):
    """
    Resource for viewing multiple Dataset objects at once.
    """
    @authenticate_token
    def get(self, user_id: int) -> list:
        """
        Returns a list of datasets that are owned by and shared with the currently logged in user.
        Note: This will only return datasets that have been verified.
        :param user_id: Currently logged in user ID
        :return: List of datasets
        """
        logged_in_user: UserModel = UserModel.query.filter_by(user_id=user_id).first()
        
        all_datasets: list = []
        
        # Retrieve all datasets that the user owns
        owned_datasets: list = DatasetModel.query.filter(
            DatasetModel.verified == true(),
            DatasetModel.owners.contains(logged_in_user),
        ).all()
        
        owned_datasets_json: list = dataset_schema.dump(owned_datasets, many=True)
        owned_dataset_ids: list = [
            dataset.get("dataset_id") for dataset in owned_datasets_json
        ]
        for dataset in owned_datasets_json:
            dataset["permission"] = "owned"
        all_datasets.extend(owned_datasets_json)
        
        # Retrieve datasets the user may access via role permissions
        shared: list = (
            DatasetModel.query.join(RoleDataset)
            .join(RoleModel)
            .join(RoleMemberModel)
            .filter(RoleMemberModel.user_id == user_id)
        )
        
        shared_json = dataset_schema.dump(shared, many=True)
        for dataset in shared_json:
            if dataset.get("dataset_id") not in owned_dataset_ids:
                dataset["permission"] = "shared"
                all_datasets.append(dataset)
        
        return all_datasets


class DatasetVerification(Resource):
    """
    Resource for validating that a Dataset has been successfully uploaded to an external source.
    """
    @authenticate_token
    def post(self, user_id: int) -> dict:
        """
        Verifies that a dataset has been uploaded. Accepts a list of dataset IDs that are to be verified, and checks
        dataset upload on AWS S3.
        :param user_id: Currently logged in user ID
        :return: None
        """
        dataset_ids: list = request.get_json(force=True).get("dataset_ids", [])  # Datasets to verify
        datasets: typing.Optional[list] = None

        try:
            datasets = dataset_util.retrieve_datasets(dataset_ids)
        except ValueError as e:
            logger.error(e.args)
            abort(404, e.args[0])
        
        job_ids: list = []
        
        for dataset in datasets:
            if not dataset.verified:
                dataset.verified = True

                job: JobModel = JobModel(dataset.dataset_id)
                db.session.add(job)
                db.session.commit()

                try:
                    dataset_util.send_job(job.job_id)
                    job_ids.append(job.job_id)
                except SystemExit as e:
                    logger.error(e.args)
                    abort(500, DatasetErrors.COULD_NOT_CREATE_JOB)
                except ValueError as e:
                    logger.error(e.args)
                    abort(500, e.args[0])

                db.session.add(
                    DatasetActionHistoryModel(
                        user_id=user_id,
                        dataset_id=dataset.dataset_id,
                        action=AuditConstants.DATASET_VERIFIED,
                    )
                )
                db.session.commit()

        if len(job_ids) == 0:
            abort(400, DatasetErrors.ALL_DATASETS_ALREADY_VERIFIED)

        return {"job_ids": job_ids}
