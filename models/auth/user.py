import datetime
import os

import bcrypt
from itsdangerous import (
    BadSignature,
    SignatureExpired,
    TimedJSONWebSignatureSerializer as Serializer,
)

from db import db
from models.associations import DatasetOwner
from models.auth.api_key import APIKeyModel
from models.auth.util import add_valid_token, check_validity
from models.datasets.base import DatasetModel

class UserModel(db.Model):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    admin = db.Column(db.Boolean, server_default="False", nullable=False)
    last_login = db.Column(db.DateTime)
    created_ts = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow()
    )

    owned_datasets = db.relationship(
        DatasetModel, secondary=DatasetOwner, back_populates="owners"
    )
    api_keys = db.relationship(APIKeyModel, backref="user", lazy=True)

    def __init__(self, email, password, first_name, last_name, admin=False):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = self.hash_password(password)
        self.admin = admin
        self.last_login = datetime.datetime.utcnow()
        self.created_ts = datetime.datetime.utcnow()

    def generate_auth_token(self, ttl=604800):
        """
        Generates an authorization token for the user upon login.
        :param ttl: Time from generation until the token expires.
        :return: Authorization token.
        """
        s = Serializer(os.environ.get("SECRET", "default_secret"), expires_in=ttl)
        
        token = s.dumps({"id": self.user_id})
        
        # Add token to an in-memory set
        add_valid_token(self.user_id, token.decode("ascii"))
        return token

    def check_password(self, password):
        """
        Check hashed password against the one stored in the database.
        :param password: Hashed password entered by the user.
        :return: Boolean representing successful password match.
        """
        return bcrypt.checkpw(password.encode(), self.password.encode())

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_auth_token(token):
        """
        Verifies that the authorization token is valid and correct.
        :param token: Authorization Token
        :return: Boolean representing successful login.
        """
        s = Serializer(os.environ.get("SECRET", "default_secret"))

        try:
            data = s.loads(token)
        except SignatureExpired:
            return False, "Token expired"  # Valid token, but TTL is passed
        except BadSignature:
            return False, "Bad token received"  # Invalid token
        
        # check if the hash of token is present in the memory to validate it.
        if check_validity(data["id"], token):
            return True, data["id"]
        else:
            return False, "Invalid token received"
            
    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.user_id}, {self.email}, {self.password}, {self.first_name}, "
            f"{self.last_name}, {self.admin}, {self.last_login})"
        )

    def __str__(self):
        return f"User {self.user_id} ({self.first_name} {self.last_name}): {self.email}"
