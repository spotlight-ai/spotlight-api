import datetime

from db import db
from models.roles.role_member import RoleMemberModel
from models.user import UserModel


class RoleModel(db.Model):
    __tablename__ = "role"
    __table_args__ = (
        db.UniqueConstraint("role_name", "creator_id", name="_role_creator_uc"),
    )
    
    role_id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    role_name = db.Column(db.String, nullable=False)
    created_ts = db.Column(db.DateTime)
    updated_ts = db.Column(db.DateTime)
    
    members = db.relationship(RoleMemberModel, backref='role')
    creator = db.relationship(UserModel, backref='role')
    
    def __init__(self, creator_id, role_name):
        self.creator_id = creator_id
        self.role_name = role_name
        self.created_ts = datetime.datetime.now()
        self.updated_ts = datetime.datetime.now()
    
    def __repr__(self):
        return f"<Role {self.role_name}>"
