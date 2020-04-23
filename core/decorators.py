import os

from flask import abort, request

from models.user import UserModel


def authenticate_token(func):
    """
    Authenticates user token and decorates API endpoints. If the token is invalid, the endpoint will not be run.
    :param func: Endpoint function
    :return: None
    """
    
    def wrapper(*args, **kwargs):
        bearer_token = request.headers['authorization'].split(' ')[1]  # Extracts the token directly from the header
        is_authenticated, message = UserModel.verify_auth_token(bearer_token)
        if is_authenticated or os.getenv("MODEL_KEY") == bearer_token:
            return func(user_id=message, *args, **kwargs)
        else:
            if message == "Token expired":
                abort(401, message)
            abort(500, message)
    
    return wrapper
