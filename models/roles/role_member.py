from db import db
import datetime


class RoleMemberModel(db.Model):
    __tablename__ = "role_member"

    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    is_owner = db.Column(db.Boolean, default=False)
    created_ts = db.Column(db.DateTime)

    def __init__(self, role_id, user_id, is_owner=False):
        self.role_id = role_id
        self.user_id = user_id
        self.is_owner = is_owner
        self.created_ts = datetime.datetime.now()

    def __repr__(self):
        return f"<Role {self.role_id} - Member {self.user_id}>"
