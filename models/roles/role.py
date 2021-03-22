import datetime

from db import db
from models.associations import RoleDataset, RolePermission
# from models.pii.pii import PIIModel
# from models.roles.role_member import RoleMemberModel


class RoleModel(db.Model):
    """
    Roles are groups of one or more users. These roles are applied to one or more datasets and are given permissions
    to see certain PII markers on those datasets.

    Datasets shared with individuals are represented as one-member roles. The "individual_role" boolean tag should be
    set to True in these instances.
    """
    __tablename__ = "role"
    __table_args__ = (
        db.UniqueConstraint("role_name", "creator_id", name="_role_creator_uc"),
    )

    role_id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(
        db.Integer, db.ForeignKey("user.user_id", ondelete="cascade")
    )
    individual_role = db.Column(db.Boolean, default=False, server_default="False")
    role_name = db.Column(db.String, nullable=False)
    created_ts = db.Column(db.DateTime)
    updated_ts = db.Column(db.DateTime)

    members = db.relationship("RoleMemberModel", cascade="all, delete", backref="role")
    creator = db.relationship("UserModel", backref="role")
    datasets = db.relationship(
        "DatasetModel",
        secondary=RoleDataset,
        cascade="all, delete",
        back_populates="roles", lazy=True
    )
    permissions = db.relationship(
        "PIIModel", secondary=RolePermission, back_populates="roles"
    )

    def __init__(self, creator_id, role_name, individual_role=False):
        self.creator_id = creator_id
        self.role_name = role_name
        self.individual_role = individual_role
        self.created_ts = datetime.datetime.utcnow()
        self.updated_ts = datetime.datetime.utcnow()

    def __repr__(self):
        return f"Role(creator_id={self.creator_id}, role_name={self.role_name}, individual_role={self.individual_role})"

    def __str__(self):
        return f"Role: {self.role_name}"
