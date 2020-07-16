import datetime

from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.decorators import authenticate_token
from core.errors import RoleErrors
from db import db
from models.roles.role_member import RoleMemberModel
from resources.roles.util import retrieve_role
from schemas.roles.role_member import RoleMemberSchema

role_member_schema = RoleMemberSchema()


class RoleMemberCollection(Resource):
    @authenticate_token
    def get(self, user_id, role_id):
        """
        Retrieves the members of a role if the user owns it.
        :param user_id: Currently logged in user ID
        :param role_id: ID of the role requested
        :return: List of role members
        """
        role = retrieve_role(role_id=role_id, user_id=user_id)
        return role_member_schema.dump(role.members, many=True)

    @authenticate_token
    def post(self, user_id, role_id):
        """
        Allows for the addition of multiple role users and owners by user ID. Request body is as follows:
        :param user_id: ID for the currently logged in user
        :param role_id: Role ID for the role receiving new members
        :return: None
        """
        body = request.get_json(force=True)
        users = body.get("users", [])
        owners = body.get("owners", [])

        # Make sure that body is correct
        for key in body.keys():
            if key not in ["users", "owners"]:
                abort(422, RoleErrors.MEMBER_INCORRECT_FIELDS)

        try:
            role = retrieve_role(role_id=role_id, user_id=user_id)
            current_members = [member.user_id for member in role.members]

            role_member_objects = self.format_role_members(
                users, current_members, role_id
            )
            role_member_objects.extend(
                self.format_role_members(
                    owners, current_members, role_id, is_owner=True
                )
            )

            role_members = role_member_schema.load(role_member_objects, many=True)
            role.members.extend(role_members)
            role.updated_ts = datetime.datetime.now()

            db.session.commit()
            return None, 201
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)

    @authenticate_token
    def put(self, user_id, role_id):
        """
        Completely replaces the permissions list for the given role. Request body is as follows:
        :param user_id: ID for the currently logged in user
        :param role_id: Role ID for the role receiving new members
        :return: None
        """
        body = request.get_json(force=True)
        users = body.get("users", [])
        owners = body.get("owners", [])

        if len(owners) < 1:
            abort(400, RoleErrors.MUST_HAVE_OWNER)

        try:
            role = retrieve_role(role_id=role_id, user_id=user_id)
            RoleMemberModel.query.filter_by(role_id=role_id).delete()

            role_member_objects = self.format_role_members(users, [], role_id)
            role_member_objects.extend(
                self.format_role_members(owners, [], role_id, is_owner=True)
            )

            role_members = role_member_schema.load(role_member_objects, many=True)
            role.members = role_members
            role.updated_ts = datetime.datetime.now()

            db.session.commit()
            return None, 200
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)

    @authenticate_token
    def delete(self, user_id, role_id):
        data = request.get_json(force=True)
        owners = data.get("owners", [])
        members = data.get("members", [])

        role = retrieve_role(role_id=role_id, user_id=user_id)
        current_owners = [member.user_id for member in role.members if member.is_owner]
        if len(list(set(current_owners) - set(owners))) == 0:
            abort(400, RoleErrors.MUST_HAVE_OWNER)

        all_members = owners
        all_members.extend(members)

        RoleMemberModel.query.filter(
            (RoleMemberModel.role_id == role_id)
            & (RoleMemberModel.user_id.in_(all_members))
        ).delete(synchronize_session="fetch")
        role.updated_ts = datetime.datetime.now()
        db.session.commit()
        return

    @staticmethod
    def format_role_members(members, current_members, role_id, is_owner=False):
        role_member_objects = []
        for member in members:
            if member in current_members:
                abort(400, RoleErrors.MEMBER_ALREADY_EXISTS)
            role_member_objects.append(
                {"role_id": role_id, "user_id": member, "is_owner": is_owner}
            )
        return role_member_objects
