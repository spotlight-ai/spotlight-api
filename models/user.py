import datetime
import os

import bcrypt
from itsdangerous import (BadSignature, SignatureExpired, TimedJSONWebSignatureSerializer as Serializer)

from db import db
from models.associations import DatasetOwner, RoleMember
from models.datasets.base import DatasetModel
from models.roles.role import RoleModel


class UserModel(db.Model):
    __tablename__ = "user"
    
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    last_login = db.Column(db.DateTime)
    created_ts = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    
    datasets_owned = db.relationship(DatasetModel, secondary=DatasetOwner, backref='user')
    roles = db.relationship(RoleModel, secondary=RoleMember, backref='user')
    
    def __init__(self, email, password, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.last_login = datetime.datetime.now()
        self.created_ts = datetime.datetime.now()
    
    def generate_auth_token(self, ttl=604800):
        s = Serializer(os.environ.get('SECRET'), expires_in=ttl)
        return s.dumps({'id': self.user_id})
    
    def check_password(self, password):
        """Check hashed password."""
        return bcrypt.checkpw(password.encode(), self.password.encode())
    
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(os.environ.get('SECRET'))
        
        try:
            data = s.loads(token)
        except SignatureExpired:
            return False, "Token expired"  # Valid token, but TTL is passed
        except BadSignature:
            return False, "Bad token received"  # Invalid token
        
        return True, data['id']
    
    def __repr__(self):
        return f"<User {self.email}>"
