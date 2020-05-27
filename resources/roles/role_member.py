import datetime

from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.decorators import authenticate_token
from db import db
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel
from schemas.roles.role_member import RoleMemberSchema

role_member_schema = RoleMemberSchema()


class RoleMemberCollection(Resource):
    
    @authenticate_token
    def get(self, user_id, role_id):
        role = RoleModel.query.filter_by(role_id=role_id).first()
        if not role:
            abort(404, 'Role not found')
        
        role_members = RoleMemberModel.query.filter_by(role_id=role_id).all()
        return role_member_schema.dump(role_members, many=True)
    
    @authenticate_token
    def post(self, user_id, role_id):
        """
        Allows for the addition of multiple role users and owners by user ID. Request body is as follows:
        {
          'users': [1, 2, 3],
          'owners': [4, 5]
        }
        
        :param user_id: ID for the currently logged in user
        :param role_id: Role ID for the role receiving new members
        :return: None
        """
        body = request.get_json(force=True)
        users = body.get('users', [])
        owners = body.get('owners', [])
        
        try:
            role_member_objects = []
            for user in users:
                role_member_objects.append({'role_id': role_id, 'user_id': user})
            
            for owner in owners:
                role_member_objects.append({'role_id': role_id, 'user_id': owner, 'is_owner': True})
            
            role_members = role_member_schema.load(role_member_objects, many=True)
            db.session.add_all(role_members)
            
            role = RoleModel.query.filter_by(role_id=role_id).first()
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
        {
          'users': [1, 2],
          'owners': [3]
        }
    
        :param user_id: ID for the currently logged in user
        :param role_id: Role ID for the role receiving new members
        :return: None
        """
        body = request.get_json(force=True)
        users = body.get('users', [])
        owners = body.get('owners', [])
        
        if len(owners) < 1:
            abort(400, "Must have an owner for the dataset")
        
        try:
            RoleMemberModel.query.filter_by(role_id=role_id).delete()
            
            role_member_objects = []
            for user in users:
                role_member_objects.append({'role_id': role_id, 'user_id': user})
            
            for owner in owners:
                role_member_objects.append({'role_id': role_id, 'user_id': owner, 'is_owner': True})
            
            role_members = role_member_schema.load(role_member_objects, many=True)
            db.session.add_all(role_members)
            
            role = RoleModel.query.filter_by(role_id=role_id).first()
            role.updated_ts = datetime.datetime.now()
            
            db.session.commit()
            return None, 201
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
