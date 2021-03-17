import bcrypt

from db import db
from models.auth.util import hash_token


class APIKeyModel(db.Model):
    __tablename__ = "api_keys"

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.user_id", ondelete="cascade"), primary_key=True,
    )
    api_key = db.Column(db.String, nullable=False, primary_key=True)
    revoked = db.Column(db.Boolean, nullable=False, server_default="True")

    def __init__(self, api_key, **kwargs):
        super().__init__(**kwargs)
        self.api_key = hash_token(api_key)

    def check_api_key(self, api_key):
        return bcrypt.checkpw(api_key.encode(), self.api_key.encode())

    def __str__(self):
        return f"APIKeyModel (User #{self.user_id} - {self.api_key}"

    def __repr__(self):
        return f"APIKeyModel(user_id={self.user_id}, api_key={self.api_key})"
