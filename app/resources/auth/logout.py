import datetime
from flask import abort, request
from flask_restful import Resource

from models.auth.util import add_invalid_token
from models.auth.user import UserModel
from core.decorators import authenticate_token

from schemas.user import UserSchema

user_schema = UserSchema()

class Logout(Resource):
    @authenticate_token    
    def get(self, user_id):
        bearer_token: str = request.headers.get("authorization", None)
        user: UserModel = UserModel.query.filter_by(user_id=user_id).first()  
        
        expiry = user.last_login + datetime.timedelta(seconds=86400)      
        
        if bearer_token:
            bearer_token = bearer_token.split(" ")[1]
            message: str = add_invalid_token(bearer_token, expiry)
        else:
            message: str = "Missing authentication header"
        
        return {"message": message}



