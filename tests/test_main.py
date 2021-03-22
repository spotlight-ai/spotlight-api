import json
import unittest
import pytest
from dotenv import find_dotenv, load_dotenv

from app import create_app, db

load_dotenv(find_dotenv())

@pytest.mark.usefixtures("load_db_test_data")
@pytest.mark.usefixtures("db")
@pytest.mark.usefixtures("client")
class BaseTest(unittest.TestCase):
        self.role_object = {"role_name": "Test Role"}
        
        self.user_route = "/user"
        self.role_route = "/role"
        self.login_route = "/login"
        self.job_route = "/job"
        self.dataset_route = "/dataset"
        self.flatfile_route = "/dataset/flat_file"
        self.pii_route = "/pii"
        self.notification_route = "/notification"
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

    
    def generate_auth_headers(self, client, user_id=1):
        """Logs in for user and generates authentication token."""
        user = self.users[user_id - 1]
        
        creds = {"email": user.get("email"), "password": user.get("password")}
        
        login_res = client.post(self.login_route, json=creds)
        token = json.loads(login_res.data.decode()).get("token")
        return {"Authorization": f"Bearer {token}"}
