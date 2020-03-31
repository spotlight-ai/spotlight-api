from flask_restful import Resource
from schemas.login import LoginSchema
from schemas.user import UserSchema
from flask import request, abort
from marshmallow import ValidationError
from models.user import UserModel
import datetime
from db import db

login_schema = LoginSchema()
user_schema = UserSchema()


class Login(Resource):
    def post(self):
        try:
            data = login_schema.load(request.get_json(force=True))
            user = UserModel.query.filter_by(email=data.get('email')).first()
            if not user:
                abort(404, "User not found.")

            if user.check_password(data.get('password')):
                user.last_login = datetime.datetime.now()
                token = user.generate_auth_token()
                db.session.commit()
                return {'token': token.decode('ascii'), 'user': user_schema.dump(user)}
            else:
                abort(500, "Credentials incorrect.")
        except ValidationError as err:
            abort(422, err.messages)


