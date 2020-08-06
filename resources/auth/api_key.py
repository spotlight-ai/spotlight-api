import secrets
from distutils.util import strtobool

from flask import request
from flask_restful import Resource
from loguru import logger

from core.decorators import authenticate_token
from db import db
from models.auth.api_key import APIKeyModel
from schemas.auth.api_key import APIKeySchema

api_key_schema: APIKeySchema = APIKeySchema()


class APIKeyCollection(Resource):
    @authenticate_token
    def get(self, user_id: int) -> dict:
        """
        Regenerates API key for the logged in user. By default, key starts revoked.
        :param user_id: Logged in user ID
        :return: Newly generated API key (Note: this can only be retrieved once!)
        """
        revoke_status: bool = strtobool(request.args.get("revoke_status", "true"))
        key: str = secrets.token_hex(40)  # Generate a 40 byte string for the key

        raw_obj: dict = {"user_id": user_id, "api_key": key, "revoked": revoke_status}
        key_obj: APIKeyModel = api_key_schema.load(raw_obj, session=db.session)

        # Delete the current key if it exists for the user
        current_key: APIKeyModel = APIKeyModel.query.filter_by(user_id=user_id).first()

        if current_key:
            db.session.delete(current_key)

        db.session.add(key_obj)
        db.session.commit()

        return api_key_schema.dump(raw_obj)


class APIKeyRevokeCollection(Resource):
    @authenticate_token
    def get(self, user_id: int) -> dict:
        """
        Update the revoke status of a user's API key. Default revoke status is True (API is revoked by default)
        :param user_id: Currently logged in user ID
        :return: JSON response
        """
        revoke_status: bool = strtobool(request.args.get("revoke_status", "True"))

        api_key: APIKeyModel = APIKeyModel.query.filter_by(user_id=user_id).first()
        api_key.revoked = revoke_status

        db.session.commit()

        logger.info(f"User {user_id}: API token revoke status: {revoke_status}")
        return {"revoked": revoke_status}
