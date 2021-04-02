from datetime import datetime

from db import db


class WorkspaceModel(db.Model):
    __tablename__ = "workspace"

    workspace_id = db.Column(db.Integer, primary_key=True)
    workspace_name = db.Column(db.String, nullable=False)
    created_ts = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __init__(self, workspace_name):
        self.workspace_name = workspace_name
        self.created_ts = datetime.now()

    def __repr__(self):
        return f"Workspace(workspace_name={self.workspace_name})"
