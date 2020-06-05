from flask_restful import Resource

from core.decorators import authenticate_token


class DatasetActionHistoryCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        pass
