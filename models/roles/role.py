import datetime

from db import db
from models.associations import RoleMember


class RoleModel(db.Model):
    __tablename__ = "role"
    __table_args__ = (
        db.UniqueConstraint("role_name", "owner_id", name="_role_owner_uc"),
    )
    
    role_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    role_name = db.Column(db.String, nullable=False)
    created_ts = db.Column(db.DateTime)
    
    members = db.relationship("UserModel", secondary=RoleMember, backref='user')
    
    def __init__(self, owner_id, role_name):
        self.owner_id = owner_id
        self.role_name = role_name
        self.created_ts = datetime.datetime.now()
    
    def __repr__(self):
        return f"<Role {self.role_name}>"
