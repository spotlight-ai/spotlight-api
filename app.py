from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from db import db
from resources.auth.login import Login
from resources.datasets.base import Dataset, DatasetCollection, DatasetVerification
from resources.datasets.flat_file import FlatFileCollection
from resources.job import Job, JobCollection
from resources.pii.text_file import TextFilePII, TextFilePIICollection
from resources.redact.text import RedactText
from resources.roles.role import Role, RoleCollection
from resources.roles.role_permission import RolePermissionCollection
from resources.user import User, UserCollection
import os


def create_app(config):
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config)
    db.init_app(app)
    
    return app


app = create_app(config=os.getenv("ENV"))

migrate = Migrate(app, db)

api = Api(app)

api.add_resource(RoleCollection, '/role')
api.add_resource(Role, '/role/<int:role_id>')
api.add_resource(RolePermissionCollection, '/role/permission')
api.add_resource(DatasetCollection, '/dataset')
api.add_resource(Dataset, '/dataset/<int:dataset_id>')
api.add_resource(FlatFileCollection, '/dataset/flat_file')
api.add_resource(JobCollection, '/job')
api.add_resource(Job, '/job/<int:job_id>')
api.add_resource(Login, '/login')
api.add_resource(RedactText, '/redact/text')
api.add_resource(DatasetVerification, '/dataset/verification')
api.add_resource(TextFilePIICollection, '/pii/text_file')
api.add_resource(TextFilePII, '/pii/text_file/<int:dataset_id>')
api.add_resource(UserCollection, '/user')
api.add_resource(User, '/user/<int:user_query_id>')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
