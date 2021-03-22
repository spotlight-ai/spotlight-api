import json

import pytest
from dotenv import load_dotenv
from pytest_factoryboy import register

from app import create_app
from app import db as _db
from models.auth.user import UserModel
from models.datasets.base import DatasetModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel
from models.pii.pii import PIIModel
from models.datasets.file import FileModel
from models.notifications.notification import NotificationModel
from models.pii.file import FilePIIModel
# from tests.factories import UserFactory
from dotenv import find_dotenv, load_dotenv


# register(UserFactory)


@pytest.fixture(scope="session")
def app():
    # load_dotenv(".testenv")
    load_dotenv(find_dotenv())
    app = create_app("config.TestingConfig")
    return app

@pytest.fixture
def client(app, request):
    with app.test_client() as client:
        request.cls.client = client
        yield client

@pytest.fixture(scope="session")
def db(app):
    _db.app = app

    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture(scope="session")
def load_db_test_data(db):
    with open("tests/setup/user_info.json") as f_user:
        user_info = json.loads(f_user.read())
        for info in user_info:
            user = UserModel(**info)
            db.session.add(user)
    
    dataset_list = []
    with open("tests/setup/dataset_info.json") as f_dataset:
        related_info = json.loads(f_dataset.read())
        for item in related_info:
            dataset = DatasetModel(**item["dataset"])
            db.session.add(dataset)
            dataset_list.append(dataset)
            for file_info in item.get("files") or []:
                _file = FileModel(**file_info)
                db.session.add(_file)
            for info in item.get("markers") or []:
                marker = FilePIIModel(**info)
                db.session.add(marker)

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
            print(dataset_list)
            for ind in item.get("datasets") or []:
                role_datasets.append(dataset_list[ind])
            role_permissions = []
            for perm in item.get("permissions") or []:
                role_permissions.append(pii_list[perm])
            db.session.add(role)

    with open("tests/setup/role_user_info.json") as f_role_user:
        role_user_info = json.loads(f_role_user.read())
        for info in role_user_info:
            role_user = RoleMemberModel(**info)
            db.session.add(role_user)

    db.session.commit()
    print("checking db")
    print(UserModel.query.filter(UserModel.user_id == 1).first())
