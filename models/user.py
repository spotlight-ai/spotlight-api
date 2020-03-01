from db import db
import datetime
import bcrypt
from flask_login import UserMixin


class UserModel(db.Model, UserMixin):
    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    last_login = db.Column(db.DateTime)
    created_ts = db.Column(db.DateTime)

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        self.last_login = datetime.datetime.now()
        self.created_ts = datetime.datetime.now()

    def get_id(self):
        return self.user_id

    def check_password(self, password):
        """Check hashed password."""
        return bcrypt.checkpw(password.encode(), self.password.encode())

    def __repr__(self):
        return f"<User {self.email}>"
