import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api

from db import db
from resources.audit.dataset_action_history import DatasetActionHistoryCollection
from resources.auth.api_key import APIKeyCollection, APIKeyRevokeCollection
from resources.auth.login import ForgotPassword, Login, ResetPassword
from resources.auth.logout import Logout
from resources.datasets.base import Dataset, DatasetCollection, DatasetVerification
from resources.datasets.file import File, FlatFileCollection
from resources.datasets.owners import DatasetOwners
from resources.datasets.shared_user import DatasetSharedUserCollection
from resources.job import Job, JobCollection
from resources.mask.text import MaskText
from resources.notifications.notification import Notification, NotificationCollection
from resources.notifications.settings import (
    NotificationSettings,
    NotificationSettingsCollection,
)
from resources.pii.pii import PIICollection
from resources.pii.text_file import (
    TextFilePII,
    TextFilePIICollection,
    TextFilePIIDatasetCollection,
)
from resources.redact.text import RedactText
from resources.roles.role import Role, RoleCollection
from resources.roles.role_dataset import RoleDatasetCollection
from resources.roles.role_member import RoleMemberCollection
from resources.roles.role_permission import RolePermissionCollection
from resources.slack.slack_token import SlackToken, SlackTokenCollection
from resources.user import User, UserCollection


def create_app(config):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config)
    db.init_app(app)
    
    api = Api(app)
    JWTManager(app)
    
    api.add_resource(DatasetActionHistoryCollection, "/audit/dataset")
    api.add_resource(APIKeyCollection, "/auth/api_key")
    api.add_resource(APIKeyRevokeCollection, "/auth/api_key/revoke")
    api.add_resource(DatasetCollection, "/dataset")
    api.add_resource(FlatFileCollection, "/dataset/file")
    api.add_resource(DatasetVerification, "/dataset/verification")
    api.add_resource(Dataset, "/dataset/<int:dataset_id>")
    api.add_resource(DatasetSharedUserCollection, "/dataset/<int:dataset_id>/user")
    api.add_resource(DatasetOwners, "/dataset/<int:dataset_id>/owner")
    api.add_resource(File, "/dataset/<int:dataset_id>/file/<int:file_id>")
    api.add_resource(ForgotPassword, "/forgot")
    api.add_resource(JobCollection, "/job")
    api.add_resource(Job, "/job/<int:job_id>")
    api.add_resource(Login, "/login")
    api.add_resource(Logout, "/logout")
    api.add_resource(PIICollection, "/pii")
    api.add_resource(TextFilePIICollection, "/pii/text_file")
    api.add_resource(TextFilePIIDatasetCollection, "/pii/text_file/<int:dataset_id>")
    api.add_resource(TextFilePII, "/pii/text_file/<int:marker_id>")
    api.add_resource(NotificationCollection, "/notification")
    api.add_resource(Notification, "/notification/<int:notification_id>")
    api.add_resource(NotificationSettingsCollection, "/settings/notification")
    api.add_resource(NotificationSettings, "/settings/notification/<int:setting_id>")
    api.add_resource(RedactText, "/redact/text")
    api.add_resource(MaskText, "/mask/text")
    api.add_resource(ResetPassword, "/reset")
    api.add_resource(RoleCollection, "/role")
    api.add_resource(Role, "/role/<int:role_id>")
    api.add_resource(RoleDatasetCollection, "/role/<int:role_id>/dataset")
    api.add_resource(RoleMemberCollection, "/role/<int:role_id>/member")
    api.add_resource(RolePermissionCollection, "/role/<int:role_id>/permission")
    api.add_resource(SlackTokenCollection, "/slack_token")
    api.add_resource(SlackToken, "/slack_token/<string:team_id>")
    api.add_resource(UserCollection, "/user")
    api.add_resource(User, "/user/<int:user_query_id>")
    
    return app


app = create_app(config=os.getenv("ENV"))

migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
