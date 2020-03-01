from flask_restful import Resource
from flask import request, abort
from schemas.roles.role_member import RoleMemberSchema
from models.roles.role_member import RoleMemberModel
from sqlalchemy.orm.exc import UnmappedInstanceError
from flask_login import login_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from db import db

role_member_schema = RoleMemberSchema()


class RoleMemberCollection(Resource):
    @login_required
    def post(self, role_id):
        try:
            data = request.get_json(force=True)
            for member in data:
                member['role_id'] = role_id

            new_members = role_member_schema.load(data, many=True, session=db.session)
            for member in new_members:
                db.session.add(member)
            db.session.commit()
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)


class RoleMember(Resource):
    @login_required
    def delete(self, role_id, user_id):
        try:
            member = RoleMemberModel.query.filter_by(role_id=role_id).filter_by(user_id=user_id).first()
            db.session.delete(member)
            db.session.commit()
        except UnmappedInstanceError as err:
            db.session.rollback()
            abort(404, err)
