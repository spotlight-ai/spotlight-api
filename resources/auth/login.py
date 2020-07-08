import datetime
import os
from string import Template

from flask import abort, request
from flask_jwt_extended import create_access_token, decode_token
from flask_restful import Resource
from loguru import logger
from marshmallow import ValidationError
from sendgrid.helpers.mail import Mail

from core.errors import UserErrors
from db import db
from models.user import UserModel
from resources.auth.util import send_email
from schemas.login import LoginSchema
from schemas.user import UserSchema

login_schema = LoginSchema()
user_schema = UserSchema()


class Login(Resource):
    def post(self):
        """
        Logs in a user and returns an authentication token.
        :return: Token and User object.
        """
        try:
            data = login_schema.load(request.get_json(force=True))
            user = UserModel.query.filter_by(email=data.get("email")).first()
            if not user:
                abort(404, "User not found.")

            if user.check_password(data.get("password")):
                user.last_login = datetime.datetime.now()
                token = user.generate_auth_token()
                db.session.commit()
                return {"token": token.decode("ascii"), "user": user_schema.dump(user)}
            else:
                abort(400, "Credentials incorrect.")
        except ValidationError as err:
            abort(422, err.messages)


class ForgotPassword(Resource):
    def post(self):
        """
        Sends password reset e-mail.
        :return: None
        """
        logger.info("ForgotPassword request received...")
        data = request.get_json(force=True)

        try:
            email = data.get("email")

            user = UserModel.query.filter_by(email=email).first()

            if not user:
                logger.error(UserErrors.USER_NOT_FOUND)
                abort(404, UserErrors.USER_NOT_FOUND)

            reset_token = create_access_token(
                str(user.user_id), expires_delta=datetime.timedelta(hours=24)
            )

            html_body = Template(
                open("./email_templates/forgot_password.html").read()
            ).safe_substitute(
                url=f"{os.environ.get('BASE_WEB_URL')}/reset?token={reset_token}"
            )

            logger.info("Loaded HTML template successfully...")

            message = Mail(
                from_email="hellospotlightai@gmail.com",
                to_emails=email,
                subject="SpotlightAI | Password Reset Request",
                html_content=html_body,
            )

            send_email(message)
            return
        except KeyError as err:
            abort(422, str(err))


class ResetPassword(Resource):
    def post(self):
        """
        Resets password of a user.
        :return: None
        """
        data = request.get_json(force=True)

        try:
            password = data.get("password")
            reset_token = data.get("reset_token")

            user_id = decode_token(reset_token).get("identity")

            user = UserModel.query.filter_by(user_id=user_id).first()

            user.password = UserModel.hash_password(password)

            db.session.commit()

            return
        except KeyError as err:
            abort(422, str(err))
