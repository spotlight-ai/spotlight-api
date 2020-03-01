from flask_restful import Resource
from schemas.login import LoginSchema
from flask import request, abort
from marshmallow import ValidationError
from models.user import UserModel
import datetime
from db import db, login_manager
from flask_login import login_user

login_schema = LoginSchema()


class Login(Resource):
    def post(self):
        try:
            data = login_schema.load(request.get_json(force=True))
            user = UserModel.query.filter_by(email=data.get('email')).first()
            if not user:
                abort(404, "User not found.")

            if user.check_password(data.get('password')):
                login_user(user)
                user.last_login = datetime.datetime.now()
                db.session.commit()
            else:
                abort(500, "Credentials incorrect.")
        except ValidationError as err:
            abort(422, err.messages)

    @staticmethod
    @login_manager.user_loader
    def user_loader(user_id):
        if user_id:
            return UserModel.query.filter_by(user_id=user_id).first()
        return None


