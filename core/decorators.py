from models.user import UserModel
from flask import request, abort


def authenticate_token(func):
    def wrapper(*args, **kwargs):
        bearer_token = request.headers['authorization'].split(' ')[1]  # Extracts the token directly from the header
        is_authenticated, message = UserModel.verify_auth_token(bearer_token)
        if is_authenticated:
            return func(user_id=message, *args, **kwargs)
        else:
            abort(500, message)
    return wrapper
