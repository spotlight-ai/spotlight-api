from db import db


class WorkspaceMemberModel(db.Model):
    __tablename__ = "workspace_member"

    workspace_id = db.Column(db.Integer, db.ForeignKey(
        "workspace.workspace_id", ondelete="cascade"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id", ondelete="cascade"), primary_key=True)
    is_owner = db.Column(db.Boolean, default=False)

    def __init__(self, workspace_id: int, user_id: int, is_owner: bool = False):
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.is_owner = is_owner

    def __repr__(self):
        return f"WorkspaceMember(workspace_id={self.workspace_id}, user_id={self.user_id}, is_owner={self.is_owner})"
