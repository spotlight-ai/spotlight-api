from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from core.decorators import authenticate_token
from db import db
from models.user import UserModel
from schemas.user import UserSchema

user_schema = UserSchema()


class UserCollection(Resource):
    
    @authenticate_token
    def get(self, user_id):
        """
        Return all users.
        :param user_id: Logged in user ID.
        :return: List of User objects.
        """
        args = request.args
        query = f'%{args.get("query", None)}%'
        
        if args.get('query'):
            users = UserModel.query.filter((UserModel.first_name.ilike(query) |
                                            (UserModel.last_name.ilike(query) |
                                             (UserModel.email.ilike(query))))).all()
        else:
            users = UserModel.query.all()
        
        return user_schema.dump(users, many=True)
    
    def post(self):
        """
        Register a new user.
        :return: None.
        """
        try:
            data = user_schema.load(request.get_json(force=True))
            
            # Check if user already exists
            if UserModel.query.filter_by(email=data.email).first():
                abort(400, "User already exists.")
            
            db.session.add(data)
            db.session.commit()
            return None, 201
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)


class User(Resource):
    loadable_fields = ["first_name", "last_name"]
    
    @authenticate_token
    def get(self, user_id, user_query_id):
        """
        Retrieves a single user.
        :param user_id: Currently logged in user ID.
        :param user_query_id: User ID to be retrieved.
        :return: User object.
        """
        user = UserModel.query.filter_by(user_id=user_query_id).first()
        if not user:
            abort(404, "User not found.")
        return user_schema.dump(user)
    
    @authenticate_token
    def patch(self, user_id, user_query_id):
        """
        Edits a single user.
        :param user_id: Currently logged in user ID.
        :param user_query_id: User ID to be edited.
        :return: None
        """
        try:
            user = UserModel.query.filter_by(user_id=user_query_id).first()
            if not user:
                abort(404, "User not found.")
            
            data = request.get_json(force=True)
            
            for k, v in data.items():
                if k in self.loadable_fields:
                    user.__setattr__(k, v)
            
            db.session.commit()
            return
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            abort(400, err)
    
    @authenticate_token
    def delete(self, user_id, user_query_id):
        """
        Deletes a user.
        :param user_id: Currently logged in user ID.
        :param user_query_id: User ID to be deleted.
        :return: None
        """
        try:
            user = UserModel.query.filter_by(user_id=user_query_id).first()
            
            if not user:
                abort(404, "User not found.")
            
            db.session.delete(user)
            db.session.commit()
            return
        except UnmappedInstanceError as err:
            db.session.rollback()
            abort(404, err)
