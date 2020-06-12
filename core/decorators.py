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
        try:
            bearer_token = request.headers['authorization'].split(' ')[1]  # Extracts the token directly from the header
            is_authenticated, message = UserModel.verify_auth_token(bearer_token)

            if bearer_token == os.getenv('MODEL_KEY'):
                return func(user_id='MODEL', *args, **kwargs)
            elif is_authenticated:
                return func(user_id=message, *args, **kwargs)
            else:
                abort(401, message)
        except KeyError:
            abort(400, "Missing authorization header")
    
    return wrapper
