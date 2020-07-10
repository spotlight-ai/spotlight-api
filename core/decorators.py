import os

from flask import abort, request

from models.auth.api_key import APIKeyModel
from models.auth.user import UserModel
from models.auth.util import hash_token


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
            abort(400, "Missing authentication header")

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


def _authenticate_api_key(api_key):
    """
    Authenticates that the API key exists in the database.
    :param api_key: Raw API key
    :return: Boolean representing authentication status
    """
    hashed_key = hash_token(api_key)
    key = APIKeyModel.query.filter_by(api_key=hashed_key).first()

    if key:
        if key.revoked:
            return False, "Unauthorized API key"
        return True, key.user_id

    return False, "Incorrect API key"
