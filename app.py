import os

from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from db import db
from db import login_manager
from resources.auth.login import Login
from resources.auth.logout import Logout
from resources.datasets.base import DatasetCollection
from resources.datasets.flat_file import FlatFileCollection
from resources.job import JobCollection, Job
from resources.roles.role import RoleCollection, Role
from resources.roles.role_member import RoleMemberCollection, RoleMember
from resources.roles.role_permission import RolePermissionCollection
from resources.user import UserCollection, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.environ.get("POSTGRES_USER")}:' \
                                        f'{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:' \
                                        f'{os.environ.get("POSTGRES_PORT")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET')
db.init_app(app)
login_manager.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

api.add_resource(RoleCollection, '/role')
api.add_resource(Role, '/role/<int:role_id>')
api.add_resource(RolePermissionCollection, '/role/permission')
api.add_resource(RoleMemberCollection, '/role/<int:role_id>/member')
api.add_resource(RoleMember, '/role/<int:role_id>/member/<int:user_id>')
api.add_resource(DatasetCollection, '/dataset')
api.add_resource(FlatFileCollection, '/dataset/flat_file')
api.add_resource(JobCollection, '/job')
api.add_resource(Job, '/job/<int:job_id>')
api.add_resource(UserCollection, '/user')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
