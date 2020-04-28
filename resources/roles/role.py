from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from core.decorators import authenticate_token
from db import db
from models.roles.role import RoleModel
from schemas.roles.role import RoleSchema

role_schema = RoleSchema()


class RoleCollection(Resource):

    @authenticate_token
    def get(self, user_id):
        """
        Retrieve a list of all roles.
        :return: List of Role objects.
        """
        roles = RoleModel.query.all()
        return role_schema.dump(roles, many=True)

    @authenticate_token
    def post(self, user_id):
        """
        Create a new role.
        :param user_id: Currently logged in user ID.
        :return: None
        """
        try:
            data = request.get_json(force=True)
            data['owner_id'] = user_id

            print(user_id, flush=True)

            role = role_schema.load(data)
            db.session.add(role)
            db.session.commit()
            return None, 201
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)


class Role(Resource):
    @authenticate_token
    def get(self, user_id, role_id):
        """
        Get an individual role.
        :param user_id: Currently logged in user ID.
        :param role_id: Role ID to be retrieved.
        :return: Role object.
        """
        role = RoleModel.query.filter_by(role_id=role_id).first()

        if not role:
            abort(404, "Role not found.")
        return role_schema.dump(role)

    @authenticate_token
    def delete(self, user_id, role_id):
        """
        Deletes an individual role.
        :param user_id: Currently logged in user ID.
        :param role_id: Role ID to be deleted.
        :return: None
        """
        try:
            role = RoleModel.query.filter_by(role_id=role_id).first()
            if not role:
                abort(404, "Role not found.")
            db.session.delete(role)
            db.session.commit()
            return
        except UnmappedInstanceError as err:
            db.session.rollback()
            abort(404, err)
