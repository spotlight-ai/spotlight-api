import datetime
import os
from string import Template

from flask import abort, request
from flask_jwt_extended import create_access_token, decode_token
from flask_restful import Resource
from loguru import logger
from marshmallow import ValidationError
from sendgrid.helpers.mail import Mail

from core.errors import AuthenticationErrors
from core.errors import UserErrors
from db import db
from models.auth.user import UserModel
from resources.auth.util import send_email
from schemas.login import LoginSchema
from schemas.user import UserSchema

login_schema = LoginSchema()
user_schema = UserSchema()


class Login(Resource):
    @staticmethod
    def post() -> dict:
        """
        Logs in a user and returns an authentication token.
        :return: Token and User object.
        """
        try:
            # Look up user in DB using the supplied e-mail address
            data: dict = login_schema.load(request.get_json(force=True))
            user: UserModel = UserModel.query.filter_by(email=data.get("email")).first()

            if not user:
                abort(404, UserErrors.USER_NOT_FOUND)

            # Verify that password hashes match and update last login time to current
            if user.check_password(data.get("password")):
                user.last_login = datetime.datetime.now()
                token: str = user.generate_auth_token().decode("utf-8")
                db.session.commit()

                return {"token": token, "user": user_schema.dump(user)}
            else:
                logger.error(
                    f'User {data.get("email")} supplied incorrect login credentials'
                )
                abort(400, AuthenticationErrors.INCORRECT_CREDS)
        except ValidationError as err:
            abort(422, err.messages)


class ForgotPassword(Resource):
    @staticmethod
    def post() -> None:
        """
        Sends password reset e-mail.
        :return: None
        """
        data: dict = request.get_json(force=True)

        try:
            # Attempt to locate the user record for the reset password request
            email: str = data.get("email")
            user: UserModel = UserModel.query.filter_by(email=email).first()

            if not user:
                logger.error(f"User not found for reset password request: {email}")
                abort(404, UserErrors.USER_NOT_FOUND)

            # Generate a password reset token that expires in 24 hours, send this with e-mail link
            reset_token: str = create_access_token(
                str(user.user_id), expires_delta=datetime.timedelta(hours=24)
            )

            # Create the e-mail to send the user
            html_body: Template = Template(
                open("./email_templates/forgot_password.html").read()
            ).safe_substitute(
                url=f"{os.environ.get('BASE_WEB_URL')}/reset?token={reset_token}"
            )

            message: Mail = Mail(
                from_email="hellospotlightai@gmail.com",
                to_emails=email,
                subject="SpotlightAI | Password Reset Request",
                html_content=html_body,
            )

            # Send the e-mail from a separate thread
            send_email(message)
            return

        except KeyError as err:
            abort(422, str(err))


class ResetPassword(Resource):
    @staticmethod
    def post() -> None:
        """
        Resets password of a user.
        :return: None
        """
        data: dict = request.get_json(force=True)

        try:
            password: str = data.get("password")
            reset_token: str = data.get("reset_token")

            # Verify token for identity, otherwise throw a key error
            user_id: int = decode_token(reset_token).get("identity")
            user: UserModel = UserModel.query.filter_by(user_id=user_id).first()

            # Set user's new password
            user.password = UserModel.hash_password(password)
            db.session.commit()
            return
        except KeyError as err:
            abort(422, str(err))
