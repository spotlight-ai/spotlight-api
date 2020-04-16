from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from db import db
from models.roles.role import RoleModel
from schemas.roles.role import RoleSchema

role_schema = RoleSchema()


class RoleCollection(Resource):
    
    def get(self):
        roles = RoleModel.query.all()
        return role_schema.dump(roles, many=True)
    
    def post(self):
        try:
            data = request.get_json(force=True)
            
            role = role_schema.load(data)
            db.session.add(role)
            db.session.commit()
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)


class Role(Resource):
    def get(self, role_id):
        role = RoleModel.query.filter_by(role_id=role_id).first()
        return role_schema.dump(role)
    
    def delete(self, role_id):
        try:
            role = RoleModel.query.filter_by(role_id=role_id).first()
            db.session.delete(role)
            db.session.commit()
        except UnmappedInstanceError as err:
            db.session.rollback()
            abort(404, err)
