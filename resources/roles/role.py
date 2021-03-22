from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.sql.expression import true

from core.decorators import authenticate_token
from core.errors import RoleErrors
from db import db
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel
from schemas.roles.role import RoleSchema
from schemas.roles.role_member import RoleMemberSchema

role_schema = RoleSchema()
role_member_schema = RoleMemberSchema()


class RoleCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        """
        Retrieve a list of all roles that the user owns.
        :param user_id: ID of the currently logged in user.
        :return: List of Role objects.
        """
        roles = RoleModel.query.filter(
            RoleModel.members.any(
                (RoleMemberModel.user_id == user_id)
                & (RoleMemberModel.is_owner == true())
            )
        ).all()
        print(roles)
        return role_schema.dump(roles, many=True)

    @authenticate_token
    def post(self, user_id):
        """
        Create a new role.
        :param user_id: ID of the currently logged in user.
        :return: None
        """
        try:
            # Add currently logged in user as the creator
            data = request.get_json(force=True)
            print(data)

            data["creator_id"] = user_id

            print(data)
            role = role_schema.load(data)
            print(type(role))
            db.session.add(role)
            db.session.flush()

            # If owners are not given, default to the currently logged in user
            owner_ids = data.get("owners", [user_id])
            if user_id not in owner_ids:
                abort(400, RoleErrors.CREATOR_MUST_BE_OWNER)

            for owner_id in owner_ids:
                db.session.add(
                    role_member_schema.load(
                        {"role_id": role.role_id, "user_id": owner_id, "is_owner": True}
                    )
                )

            db.session.commit()
            return role_schema.dump(role), 201
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
        :return: Role object
        """
        role = self.retrieve_role(role_id=role_id, user_id=user_id)

        return role_schema.dump(role)

    @authenticate_token
    def patch(self, user_id, role_id):
        """
        Updates a role's information and returns the updated object.
        :param user_id: Currently logged in user ID.
        :param role_id: Role ID to be updated
        :return: Role object
        """
        loadable_fields = ["role_name"]
        role = self.retrieve_role(role_id=role_id, user_id=user_id)
        data = request.get_json(force=True)

        for key, value in data.items():
            if key in loadable_fields:
                role.__setattr__(key, value)

        if "owners" in data:
            if len(data.get("owners")) == 0:
                abort(400, RoleErrors.MUST_HAVE_OWNER)
            RoleMemberModel.query.filter_by(
                role_id=role_id, is_owner=True
            ).delete()  # Remove current owners
            for owner_id in data.get("owners"):
                db.session.add(
                    role_member_schema.load(
                        {"role_id": role.role_id, "user_id": owner_id, "is_owner": True}
                    )
                )

        db.session.commit()
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
            self.retrieve_role(role_id=role_id, user_id=user_id)

            RoleModel.query.filter_by(role_id=role_id).delete()

            db.session.commit()
            return
        except UnmappedInstanceError as err:
            db.session.rollback()
            abort(404, err)

    @staticmethod
    def retrieve_role(user_id, role_id):
        """
        Retrieves a role object if the user owns it.
        :param user_id: Currently logged in user ID.
        :param role_id: Role ID to be retrieved.
        :return: Role object or abort if user does not have access.
        """
        role = RoleModel.query.filter(
            (RoleModel.role_id == role_id)
            & (RoleMemberModel.user_id == user_id)
            & (RoleMemberModel.is_owner == true())
        ).first()

        if not role:
            abort(404, RoleErrors.MISSING_NO_PERMISSIONS)

        return role
