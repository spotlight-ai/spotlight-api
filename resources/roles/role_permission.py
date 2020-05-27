from flask import abort, request
from flask_restful import Resource

from core.decorators import authenticate_token
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
        role = RoleModel.query.filter((RoleModel.role_id == role_id) & (RoleMemberModel.user_id == user_id) & (
                RoleMemberModel.is_owner == True)).first()
        
        if not role:
            abort(401, "Role either does not exist or user does not have permissions")
        
        return pii_schema.dump(role.permissions, many=True)
    
    @authenticate_token
    def post(self, user_id, role_id):
        role = RoleModel.query.filter((RoleModel.role_id == role_id) & (RoleMemberModel.user_id == user_id) & (
                RoleMemberModel.is_owner == True)).first()
        
        if not role:
            abort(401, "Role either does not exist or user does not have permissions")
        
        data = request.get_json(force=True)
        permission_descriptions = data.get('permissions', [])
        pii_markers = PIIModel.query.filter((PIIModel.description.in_(permission_descriptions))).all()
        
        for pii in pii_markers:
            if pii in role.permissions:
                abort(400, f'Permission {pii.description} already present in role.')
            
            role.permissions.append(pii)
        
        db.session.commit()
        return None, 201
    
    @authenticate_token
    def put(self, user_id, role_id):
        role = RoleModel.query.filter((RoleModel.role_id == role_id) & (RoleMemberModel.user_id == user_id) & (
                RoleMemberModel.is_owner == True)).first()
        
        if not role:
            abort(401, "Role either does not exist or user does not have permissions")
        
        data = request.get_json(force=True)
        permission_descriptions = data.get('permissions', [])
        pii_markers = PIIModel.query.filter((PIIModel.description.in_(permission_descriptions))).all()
        role.permissions = pii_markers
        
        return role_schema.dump(role)
    
    @authenticate_token
    def delete(self, user_id, role_id):
        role = RoleModel.query.filter((RoleModel.role_id == role_id) & (RoleMemberModel.user_id == user_id) & (
                RoleMemberModel.is_owner == True)).first()
        
        if not role:
            abort(401, "Role either does not exist or user does not have permissions")
        
        data = request.get_json(force=True)
        permission_descriptions = data.get('permissions', [])
        pii_markers = PIIModel.query.filter((PIIModel.description.in_(permission_descriptions))).all()
        
        for pii in pii_markers:
            role.permissions.remove(pii)
        
        return role_schema.dump(role)
