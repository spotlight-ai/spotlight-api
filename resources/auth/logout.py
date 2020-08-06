from flask import abort, request
from flask_restful import Resource

from models.auth.util import invalidate_token
from core.decorators import authenticate_token

class Logout(Resource):
    @authenticate_token    
    def get(self, user_id):
        bearer_token = request.headers.get("authorization", None)
        
        if bearer_token:
            bearer_token = bearer_token.split(" ")[1]
            message = invalidate_token(user_id, bearer_token)
        else:
            message = "Missing authentication header"
        
        return {"message": message}



