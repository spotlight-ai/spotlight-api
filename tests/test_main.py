import json
import unittest

from dotenv import find_dotenv, load_dotenv

from app import create_app, db

load_dotenv(find_dotenv())


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config.TestingConfig")
        self.client = self.app.test_client

        # Define common objects to use in downstream test cases
        self.role_object = {"role_name": "Test Role"}

        self.user_route = "/user"
        self.role_route = "/role"
        self.login_route = "/login"
        self.job_route = "/job"
        self.dataset_route = "/dataset"
        self.flatfile_route = "/dataset/flat_file"
        self.pii_route = "/pii"
        self.notification_route = "/notification"

        with self.app.app_context():
            # Pre-load database to desired state
            from models.auth.user import UserModel
            from models.roles.role import RoleModel
            from models.roles.role_member import RoleMemberModel
            from models.pii.pii import PIIModel
            from models.datasets.flat_file import FlatFileDatasetModel
            from models.datasets.shared_user import SharedDatasetUserModel
            from models.notifications.notification import NotificationModel
            from models.pii.text_file import TextFilePIIModel

            db.create_all()

            self.users = [
                {
                    "first_name": "Doug",
                    "last_name": "Developer",
                    "email": "doug@spotlightai.com",
                    "password": "testpassword",
                },
                {
                    "first_name": "Dana",
                    "last_name": "Developer",
                    "email": "dana@spotlight.ai",
                    "password": "pass123",
                },
                {
                    "first_name": "Mary",
                    "last_name": "Manager",
                    "email": "mary@spotlight.ai",
                    "password": "pass123",
                },
                {
                    "first_name": "Mark",
                    "last_name": "Manager",
                    "email": "mark@spotlight.ai",
                    "password": "pass123",
                },
                {
                    "first_name": "Cindy",
                    "last_name": "Compliance",
                    "email": "cindy@spotlight.ai",
                    "password": "pass123",
                    "admin": True,
                },
                {
                    "first_name": "Craig",
                    "last_name": "Compliance",
                    "email": "craig@spotlight.ai",
                    "password": "pass123",
                    "admin": True,
                },
                {
                    "first_name": "Oscar",
                    "last_name": "Outsider",
                    "email": "oscar@oscartime.com",
                    "password": "pass123",
                },
                {
                    "first_name": "Rando",
                    "last_name": "Public",
                    "email": "rando@gmail.com",
                    "password": "pass123",
                },
            ]

            # Create PII markers
            pii_ssn = PIIModel(
                "ssn", category="Identity", long_description="Social Security Number"
            )
            pii_name = PIIModel("name", category="Identity", long_description="Name")
            pii_address = PIIModel(
                "address", category="Identity", long_description="Address"
            )

            # Create datasets
            dataset_1 = FlatFileDatasetModel(
                dataset_name="Call Center Transcripts",
                uploader=3,
                location="dataset.txt",
            )
            dataset_2 = FlatFileDatasetModel(
                dataset_name="Resumes", uploader=3, location="resumes.txt"
            )
            dataset_3 = FlatFileDatasetModel(
                dataset_name="Drivers Licenses", uploader=3, location="drivers.txt"
            )
            dataset_4 = FlatFileDatasetModel(
                dataset_name="Auto Loan", uploader=4, location="auto_loans.txt"
            )

            dataset_1_shared_user_1 = SharedDatasetUserModel(dataset_id=1, user_id=1)
            dataset_1_shared_user_1.permissions = [pii_ssn]
            dataset_1_shared_user_2 = SharedDatasetUserModel(dataset_id=1, user_id=2)

            text_file_pii_1 = TextFilePIIModel(
                dataset_id=1,
                pii_type="ssn",
                start_location=12,
                end_location=21,
                confidence=0.9,
            )

            dataset_1.markers = [text_file_pii_1]

            # Create roles, owners, members and assign datasets to roles
            role_1 = RoleModel(creator_id=4, role_name="Financial Developers")
            role_2 = RoleModel(creator_id=4, role_name="Personal Developers")
            role_1_owner_1 = RoleMemberModel(role_id=1, user_id=4, is_owner=True)
            role_1_owner_2 = RoleMemberModel(role_id=1, user_id=3, is_owner=True)
            role_1_user_1 = RoleMemberModel(role_id=1, user_id=1)
            role_1.datasets = [dataset_1]

            role_2_owner_1 = RoleMemberModel(role_id=2, user_id=4, is_owner=True)
            role_2_user_1 = RoleMemberModel(role_id=2, user_id=2)

            # Create notifications
            notification_1 = NotificationModel(
                user_id=1, title="New Notification", detail="Notification Detail"
            )
            notification_2 = NotificationModel(
                user_id=1, title="Additional Notification", detail="Detail"
            )
            notification_3 = NotificationModel(
                user_id=1, title="Third Notification", detail="More Detail", viewed=True
            )
            notification_4 = NotificationModel(
                user_id=2, title="Third Notification", detail="More Detail", viewed=True
            )

            # Create system users and allocate dataset owners
            for user in self.users:
                user = UserModel(
                    first_name=user.get("first_name"),
                    last_name=user.get("last_name"),
                    email=user.get("email"),
                    password=user.get("password"),
                    admin=user.get("admin", False),
                )
                if user.email == "mary@spotlight.ai":
                    dataset_1.owners = [user]
                    dataset_2.owners = [user]
                    dataset_3.owners = [user]
                elif user.email == "mark@spotlight.ai":
                    dataset_2.owners.append(user)
                    dataset_4.owners = [user]

                db.session.add(user)

            db.session.add(dataset_1)
            db.session.add(dataset_2)
            db.session.add(dataset_3)
            db.session.add(dataset_4)

            db.session.add(dataset_1_shared_user_1)
            db.session.add(dataset_1_shared_user_2)

            # Add permissions to roles
            role_1.permissions = [pii_ssn]
            role_2.permissions = [pii_name, pii_address]

            # Store all objects in database
            db.session.add(role_1)
            db.session.add(role_2)
            db.session.add(role_1_owner_1)
            db.session.add(role_1_owner_2)
            db.session.add(role_1_user_1)
            db.session.add(role_2_owner_1)
            db.session.add(role_2_user_1)

            # Store notifications
            db.session.add(notification_1)
            db.session.add(notification_2)
            db.session.add(notification_3)
            db.session.add(notification_4)

            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def generate_auth_headers(self, user_id=1):
        """Logs in for user and generates authentication token."""
        user = self.users[user_id - 1]

        creds = {"email": user.get("email"), "password": user.get("password")}

        login_res = self.client().post(self.login_route, json=creds)
        token = json.loads(login_res.data.decode()).get("token")
        return {"Authorization": f"Bearer {token}"}
