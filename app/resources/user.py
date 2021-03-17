from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy import or_

from core.constants import UserConstants
from core.decorators import authenticate_token
from core.errors import UserErrors
from db import db
from models.auth.user import UserModel
from schemas.user import UserSchema

user_schema = UserSchema()


class UserCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        """
        Return all users.
        :param user_id: Logged in user ID.
        :return: List of User objects.
        """
        query = f'%{request.args.get("query", None)}%'
        user = UserModel.query.filter_by(user_id=user_id).first()

        user_domain = user.email.split("@")[1]
        domains = set(UserConstants.PUBLIC_DOMAINS + [user_domain])
        domain_filters = [f"%{public_domain}%" for public_domain in domains]

        if request.args.get("query"):
            user_filter_query = UserModel.query.filter(
                (
                    UserModel.first_name.ilike(query)
                    | (
                        UserModel.last_name.ilike(query)
                        | (UserModel.email.ilike(query))
                    )
                )
            )
        else:
            user_filter_query = UserModel.query

        filter_args = [UserModel.email.ilike(domain) for domain in domain_filters]
        user_filter_query = user_filter_query.filter(or_(*filter_args))
        user_filter_query = user_filter_query.filter(UserModel.email != user.email)

        return user_schema.dump(
            user_filter_query.order_by(UserModel.last_name).limit(10).all(), many=True
        )

    def post(self):
        """
        Register a new user.
        :return: None.
        """
        try:
            user = user_schema.load(request.get_json(force=True))

            # Check if user already exists
            if UserModel.query.filter_by(email=user.email).first():
                abort(400, UserErrors.USER_ALREADY_EXISTS)

            db.session.add(user)
            db.session.commit()
            return None, 201
        except ValidationError as err:
            abort(422, err.messages)


class User(Resource):
    @authenticate_token
    def get(self, user_id, user_query_id):
        """
        Retrieves a single user.
        :param user_id: Currently logged in user ID.
        :param user_query_id: User ID to be retrieved.
        :return: User object.
        """
        user = UserModel.query.filter_by(user_id=user_query_id).first()
        if not user:
            abort(404, UserErrors.USER_NOT_FOUND)

        return user_schema.dump(user)

    @authenticate_token
    def patch(self, user_id, user_query_id):
        """
        Edits a single user.
        :param user_id: Currently logged in user ID.
        :param user_query_id: User ID to be edited.
        :return: None
        """
        loadable_fields = [
            "first_name",
            "last_name",
        ]  # Only these fields in the User model can be edited

        try:
            user = UserModel.query.filter_by(user_id=user_query_id).first()
            if not user:
                abort(404, UserErrors.USER_NOT_FOUND)

            data = request.get_json(force=True)

            user = user_schema.load(
                data, instance=user, partial=True
            )  # Validate fields

            for k, v in data.items():
                if k in loadable_fields:
                    user.__setattr__(k, v)
                else:
                    abort(400, f"{k}: {UserErrors.EDITING_INVALID_FIELD}")

            db.session.commit()
            return user_schema.dump(user)
        except ValidationError as err:
            abort(422, err.messages)

    @authenticate_token
    def delete(self, user_id, user_query_id):
        """
        Deletes a user.
        :param user_id: Currently logged in user ID.
        :param user_query_id: User ID to be deleted.
        :return: None
        """
        UserModel.query.filter_by(user_id=user_query_id).delete()
        db.session.commit()
        return
