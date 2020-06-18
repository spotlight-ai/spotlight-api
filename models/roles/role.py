import datetime

from db import db
from models.associations import RoleDataset, RolePermission
from models.pii.pii import PIIModel
from models.roles.role_member import RoleMemberModel


class RoleModel(db.Model):
    __tablename__ = "role"
    __table_args__ = (
        db.UniqueConstraint("role_name", "creator_id", name="_role_creator_uc"),
    )
    
    role_id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete='cascade'))
    role_name = db.Column(db.String, nullable=False)
    created_ts = db.Column(db.DateTime)
    updated_ts = db.Column(db.DateTime)
    
    members = db.relationship(RoleMemberModel, cascade="all, delete", backref="role")
    creator = db.relationship("UserModel", backref="role")
    datasets = db.relationship(
        "DatasetModel",
        secondary=RoleDataset,
        cascade="all, delete",
        back_populates="roles",
    )
    permissions = db.relationship(
        PIIModel, secondary=RolePermission, back_populates="roles"
    )
    
    def __init__(self, creator_id, role_name):
        self.creator_id = creator_id
        self.role_name = role_name
        self.created_ts = datetime.datetime.utcnow()
        self.updated_ts = datetime.datetime.utcnow()
    
    def __repr__(self):
        return f"<Role {self.role_name}>"
