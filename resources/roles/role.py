from flask_restful import Resource
from flask import request, abort
from schemas.roles.role import RoleSchema
from schemas.roles.role_member import RoleMemberSchema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from models.roles.role import RoleModel
from flask_login import login_required, current_user
from db import db

role_schema = RoleSchema()
role_member_schema = RoleMemberSchema()


class RoleCollection(Resource):

    @login_required
    def get(self):
        roles = RoleModel.query.all()
        return role_schema.dump(roles, many=True)

    @login_required
    def post(self):
        try:
            data = request.get_json(force=True)
            data['owner_id'] = current_user.user_id

            role = role_schema.load(data)
            db.session.add(role)
            db.session.commit()
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)


class Role(Resource):
    @login_required
    def get(self, role_id):
        role = RoleModel.query.filter_by(role_id=role_id).first()
        return role_schema.dump(role)

    @login_required
    def delete(self, role_id):
        try:
            role = RoleModel.query.filter_by(role_id=role_id).first()
            db.session.delete(role)
            db.session.commit()
        except UnmappedInstanceError as err:
            db.session.rollback()
            abort(404, err)



