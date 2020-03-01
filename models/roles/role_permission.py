from db import db
import datetime


class RolePermissionModel(db.Model):
    __tablename__ = "role_permission"

    role_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    role_name = db.Column(db.String, nullable=False)
    created_ts = db.Column(db.DateTime)

    def __init__(self, owner_id, role_name):
        self.owner_id = owner_id
        self.role_name = role_name
        self.created_ts = datetime.datetime.now()

    def __repr__(self):
        return f"<Role {self.role_name}>"
