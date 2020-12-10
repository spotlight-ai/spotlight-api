import os

from flask import abort, request

from core.errors import AuthenticationErrors
from models.auth.api_key import APIKeyModel
from models.auth.user import UserModel
from models.datasets.base import  DatasetModel
from models.auth.util import hash_token


def is_dataset_owner(func):
    def wrapper(*args, **kwargs):
        """Checking the ownership of current user"""

        dataset_id = kwargs.get('dataset_id',None)
        user_id = kwargs.get('user_id',None)

        if not dataset_id or not user_id:
            abort(400, DatasetErrors.DOES_NOT_EXIST)

        dataset = DatasetModel.query.filter_by(dataset_id=dataset_id).first()

        if not dataset:
            abort(400, DatasetErrors.DOES_NOT_EXIST)

        owners = [owner.user_id for owner in dataset.owners]

        if user_id not in owners:
            abort(400, DatasetErrors.USER_DOES_NOT_OWN)

        return func(dataset=dataset,existing_owners=owners,*args, **kwargs)

    return wrapper


def authenticate_token(func):
    """
    Authenticates user token and decorates API endpoints. If the token is invalid, the endpoint will not be run.
    :param func: Endpoint function
    :return: None
    """

    def wrapper(*args, **kwargs):
        is_authenticated = False
        message = ""

        api_key = request.headers.get("x-api-key", None)
        bearer_token = request.headers.get("authorization", None)

        if not api_key and not bearer_token:
            abort(400, AuthenticationErrors.MISSING_AUTH_HEADER)

        if api_key:
            is_authenticated, message = _authenticate_api_key(api_key)

        elif bearer_token:
            bearer_token = bearer_token.split(" ")[1]
            is_authenticated, message = UserModel.verify_auth_token(bearer_token)

        if bearer_token == os.getenv("MODEL_KEY"):
            return func(user_id="MODEL", *args, **kwargs)

        elif is_authenticated:
            return func(user_id=message, *args, **kwargs)
        else:
            abort(401, message)

    return wrapper


def _authenticate_api_key(api_key: str) -> tuple:
    """
    Authenticates that the API key exists in the database.
    :param api_key: Raw API key
    :return: Boolean representing authentication status
    """
    hashed_key: str = hash_token(api_key)
    key: APIKeyModel = APIKeyModel.query.filter_by(api_key=hashed_key).first()

    try:
        if key.revoked:
            return False, AuthenticationErrors.UNAUTHORIZED_API_KEY
        return True, key.user_id

    except AttributeError:
        return False, AuthenticationErrors.INCORRECT_API_KEY
