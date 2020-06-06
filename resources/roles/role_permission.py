from flask import abort, request
from flask_restful import Resource

from core.decorators import authenticate_token
from core.errors import Role
from db import db
from models.pii.pii import PIIModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel
from schemas.pii.pii import PIISchema
from schemas.roles.role import RoleSchema

pii_schema = PIISchema()
role_schema = RoleSchema()


class RolePermissionCollection(Resource):
    @authenticate_token
    def get(self, user_id, role_id):
        """
        Retrieves the list of PII permissions that a role has the ability to view.
        Note: The requesting user must be the owner of the role.
        :param user_id: ID of the currently logged in user.
        :param role_id: ID of the role requested.
        :return: List of role permissions.
        """
        role = self.retrieve_role(role_id=role_id, user_id=user_id)
        
        return pii_schema.dump(role.permissions, many=True)
    
    @authenticate_token
    def post(self, user_id, role_id):
        """
        Adds one or multiple PII permissions to a role.
        :param user_id: ID of the currently logged in user.
        :param role_id: ID of the role to add permissions to.
        :return: None
        """
        role = self.retrieve_role(role_id=role_id, user_id=user_id)
        
        permission_descriptions = request.get_json(force=True).get('permissions', [])
        
        # Retrieve PII marker objects based on descriptions passed in the POST body
        pii_markers = PIIModel.query.filter((PIIModel.description.in_(permission_descriptions))).all()
        
        # Verify that PII added is not already part of the Role permissions
        role_marker_descriptions = [perm.description for perm in role.permissions]
        permissions_already_existing = list(set(permission_descriptions) & set(role_marker_descriptions))
        
        if len(permissions_already_existing) > 0:
            abort(400, f'{Role.PERMISSION_ALREADY_PRESENT}: {permissions_already_existing}')
        
        role.permissions.extend(pii_markers)
        
        db.session.commit()
        return None, 201
    
    @authenticate_token
    def put(self, user_id, role_id):
        """
        Replaces the list of permissions already present in a given role.
        :param user_id: ID of the currently logged in user.
        :param role_id: ID of the role to replace permissions.
        :return: Role object that has been updated.
        """
        role = self.retrieve_role(role_id=role_id, user_id=user_id)
        
        permission_descriptions = request.get_json(force=True).get('permissions', [])
        
        # Retrieve PII marker objects based on descriptions passed in the POST body
        role.permissions = PIIModel.query.filter((PIIModel.description.in_(permission_descriptions))).all()
        db.session.commit()
        
        return role_schema.dump(role)
    
    @authenticate_token
    def delete(self, user_id, role_id):
        """
        Deletes one or more permissions from a role.
        :param user_id: ID of the currently logged in user.
        :param role_id: ID of the role to replace permissions.
        :return: Role object that has been updated.
        """
        role = self.retrieve_role(role_id=role_id, user_id=user_id)
        
        permission_descriptions = request.get_json(force=True).get('permissions', [])
        pii_markers = PIIModel.query.filter((PIIModel.description.in_(permission_descriptions))).all()
        
        # Verify that PII removed are all currently in role permissions
        role_marker_descriptions = [perm.description for perm in role.permissions]
        permissions_missing = list(set(permission_descriptions) - set(role_marker_descriptions))
        
        if len(permissions_missing) != 0:
            abort(400, f'{Role.PERMISSIONS_MISSING}: {permissions_missing}')
        
        for pii in pii_markers:
            role.permissions.remove(pii)
        
        return role_schema.dump(role)
    
    @staticmethod
    def retrieve_role(role_id, user_id):
        """
        Returns a role if it is owned by the given user. If not, None is returned.
        :param role_id: Role ID to be returned.
        :param user_id: ID of the user to verify ownership.
        :return: Role object if user is owner, otherwise None.
        """
        role = RoleModel.query.filter((RoleModel.role_id == role_id) & (RoleMemberModel.user_id == user_id) & (
                RoleMemberModel.is_owner == True)).first()
        
        if not role:
            abort(401, Role.MISSING_NO_PERMISSIONS)
        
        return role
