
import json

import pytest
from dotenv import load_dotenv
from pytest_factoryboy import register
from flask_jwt_extended import create_access_token, decode_token

from app import create_app
from app import db as app_db
from models.auth.user import UserModel
from models.datasets.base import DatasetModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel
from models.pii.pii import PIIModel
from models.pii.marker_base import PIIMarkerBaseModel
from models.pii.marker_character import PIIMarkerCharacterModel
from models.pii.marker_image import PIIMarkerImageModel
from models.datasets.file import FileModel
from models.notifications.notification import NotificationModel
from models.pii.marker_base import PIIMarkerBaseModel
from models.pii.marker_character import PIIMarkerCharacterModel
from models.pii.marker_image import PIIMarkerImageModel
from models.workspaces.workspace import WorkspaceModel
from models.workspaces.workspace_member import WorkspaceMemberModel
from dotenv import find_dotenv, load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, event

user_route = "/user"
role_route = "/role"
login_route = "/login"
job_route = "/job"
dataset_route = "/dataset"
flatfile_route = "/dataset/flat_file"
pii_route = "/pii"
notification_route = "/notification"
WORKSPACE_ROUTE = "/workspace"


@pytest.fixture(scope="session")
def app():
    # load_dotenv(".testenv")
    load_dotenv(find_dotenv())
    app = create_app("config.TestingConfig")
    with app.app_context():
        yield app


user_info_list = []
user_list = []
dataset_list = []


@pytest.fixture(scope="session")
def database(app):
    app_db.app = app
    app_db.drop_all()
    db = app_db
    db.create_all()
    with open("tests/setup/user_info.json") as f_user:
        user_info = json.loads(f_user.read())
        for info in user_info:
            user_info_list.append(info)
            user = UserModel(**info)
            db.session.add(user)
            user_list.append(user)
    
    with open("tests/setup/dataset_info.json") as f_dataset:
        related_info = json.loads(f_dataset.read())
        for item in related_info:
            dataset = DatasetModel(**item["dataset"])
            for owner in item.get("owners") or []:
                dataset.owners.append(user_list[owner-1])
            for file_info in item.get("files") or []:
                _file = FileModel(**file_info)
                db.session.add(_file)
            for info in item.get("markers") or []:
                if "start_location" in info.keys():
                    marker = PIIMarkerCharacterModel(**info)
                elif "x1" in info.keys():
                    marker = PIIMarkerImageModel(**info)
                else:
                    marker = PIIMarkerBaseModel(**info)
                db.session.add(marker)
            db.session.add(dataset)
            dataset_list.append(dataset)

    with open("tests/setup/notification_info.json") as f_notification:
        notification_info = json.loads(f_notification.read())
        for info in notification_info:
            notification = NotificationModel(**info)
            db.session.add(notification)

    pii_list = {}
    with open("tests/setup/pii_info.json") as f_pii:
        pii_info = json.loads(f_pii.read())
        for info in pii_info:
            pii = PIIModel(**info)
            db.session.add(pii)
            pii_list[info["description"]] = pii
    
    with open("tests/setup/role_info.json") as f_role:
        related_info = json.loads(f_role.read())
        for item in related_info:
            role = RoleModel(**item["role"])
            role_datasets = []
            for ind in item.get("datasets") or []:
                role_datasets.append(dataset_list[ind])
            role_permissions = []
            for perm in item.get("permissions") or []:
                role_permissions.append(pii_list[perm])
            role.datasets = role_datasets
            role.permissions = role_permissions
            db.session.add(role)

    with open("tests/setup/role_user_info.json") as f_role_user:
        role_user_info = json.loads(f_role_user.read())
        for info in role_user_info:
            role_user = RoleMemberModel(**info)
            db.session.add(role_user)

    with open("tests/setup/workspace_info.json") as f_workspace:
        workspace_info = json.loads(f_workspace.read())
        for info in workspace_info:
            workspace = WorkspaceModel(**info)
            db.session.add(workspace)

    with open("tests/setup/workspace_member_info.json") as f_workspace_member:
        member_info = json.loads(f_workspace_member.read())
        for info in member_info:
            member = WorkspaceMemberModel(**info)
            db.session.add(member)

    db.session.commit()

    return db


@pytest.fixture(scope="session")
def _db(database):
    return database


@pytest.mark.usefixtures("user_info")
def generate_auth_headers(client, user_id=1):
        """Logs in for user and generates authentication token."""
        user = user_info_list[user_id - 1]
        creds = {"email": user.get("email"), "password": user.get("password")}
        login_res = client.post("/login", json=creds)
        token = json.loads(login_res.data.decode()).get("token")
        return {"Authorization": f"Bearer {token}"}


def generate_access_token(body, expires_delta):
    token = create_access_token(identity=body, expires_delta=expires_delta)
    return token

def decode_access_token(token: str):
    return json.loads(decode_token(token).get("sub"))
