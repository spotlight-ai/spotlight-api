from flask_restful import Resource
from schemas.login import LoginSchema
from flask_login import logout_user, login_required

login_schema = LoginSchema()


class Logout(Resource):
    @login_required
    def get(self):
        logout_user()
