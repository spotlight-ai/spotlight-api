from flask_restful import Resource
from flask import request, abort
from schemas.user import UserSchema
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError
from models.user import UserModel
from flask_login import login_required
from db import db

user_schema = UserSchema()


class UserCollection(Resource):

    @login_required
    def get(self):
        users = UserModel.query.all()
        return user_schema.dump(users, many=True)

    def post(self):
        try:
            data = user_schema.load(request.get_json(force=True))
            db.session.add(data)
            db.session.commit()
            return
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)


class User(Resource):
    @login_required
    def get(self, user_id):
        user = UserModel.query.filter_by(user_id=user_id).first()
        return user_schema.dump(user)

    @login_required
    def delete(self, user_id):
        try:
            user = UserModel.query.filter_by(user_id=user_id).first()
            db.session.delete(user)
            db.session.commit()
        except UnmappedInstanceError as err:
            db.session.rollback()
            abort(404, err)
