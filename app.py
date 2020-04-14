import os

from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from db import db
from resources.auth.login import Login
from resources.datasets.base import Dataset, DatasetCollection, DatasetVerification
from resources.datasets.dataset_owner import DatasetOwnerCollection
from resources.datasets.flat_file import FlatFileCollection
from resources.job import Job, JobCollection
from resources.pii.text_file import TextFilePIICollection
from resources.redact.text import RedactText
from resources.roles.role import Role, RoleCollection
from resources.roles.role_member import RoleMember, RoleMemberCollection
from resources.roles.role_permission import RolePermissionCollection
from resources.user import User, UserCollection

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.environ.get("POSTGRES_USER")}:' \
                                        f'{os.environ.get("POSTGRES_PASSWORD")}@{os.environ.get("POSTGRES_HOST")}:' \
                                        f'{os.environ.get("POSTGRES_PORT")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET')
db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

api.add_resource(RoleCollection, '/role')
api.add_resource(Role, '/role/<int:role_id>')
api.add_resource(RolePermissionCollection, '/role/permission')
api.add_resource(RoleMemberCollection, '/role/<int:role_id>/member')
api.add_resource(RoleMember, '/role/<int:role_id>/member/<int:user_id>')
api.add_resource(DatasetCollection, '/dataset')
api.add_resource(Dataset, '/dataset/<int:dataset_id>')
api.add_resource(FlatFileCollection, '/dataset/flat_file')
api.add_resource(JobCollection, '/job')
api.add_resource(Job, '/job/<int:job_id>')
api.add_resource(UserCollection, '/user')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(Login, '/login')
api.add_resource(RedactText, '/redact/text')
api.add_resource(DatasetVerification, '/dataset/verification')
api.add_resource(TextFilePIICollection, '/pii/text_file')
api.add_resource(DatasetOwnerCollection, '/dataset/dataset_owner')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
