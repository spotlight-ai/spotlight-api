import secrets
from distutils.util import strtobool

from flask import request
from flask_restful import Resource

from core.decorators import authenticate_token
from db import db
from models.auth.api_key import APIKeyModel
from schemas.auth.api_key import APIKeySchema

api_key_schema = APIKeySchema()


class APIKeyCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        """
        Regenerates API key for the logged in user.
        :param user_id: Logged in user ID
        :return: Newly generated API key (Note: this can only be retrieved once!)
        """
        revoke_status = request.args.get("revoke_status", True)
        key = secrets.token_hex(40)
        raw_obj = {"user_id": user_id, "api_key": key, "revoked": revoke_status}
        key_obj = api_key_schema.load(raw_obj, session=db.session)

        current_key = APIKeyModel.query.filter_by(user_id=user_id).first()

        if current_key:
            db.session.delete(current_key)

        db.session.add(key_obj)
        db.session.commit()

        return api_key_schema.dump(raw_obj)


class APIKeyRevokeCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        revoke_status = request.args.get("revoke_status", True)

        api_key = APIKeyModel.query.filter_by(user_id=user_id).first()
        parsed_bool = strtobool(revoke_status)
        api_key.revoked = parsed_bool

        db.session.commit()

        return {"revoked": bool(parsed_bool)}
