from db import db


class RoleMemberModel(db.Model):
    __tablename__ = "role_member"
    __table_args__ = (db.UniqueConstraint("role_id", "user_id", name="_role_user_uc"),)

    role_member_id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.role_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    is_owner = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("UserModel", backref="role_member")

    def __init__(self, role_id, user_id, is_owner=False):
        self.role_id = role_id
        self.user_id = user_id
        self.is_owner = is_owner

    def __repr__(self):
        return f"RoleMember(Role: {self.role_id}, User: {self.user_id}, Owner: {self.is_owner})"
