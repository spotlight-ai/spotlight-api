from datetime import datetime

from db import db


class DatasetActionHistoryModel(db.Model):
    __tablename__ = "audit_dataset_action"

    item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="cascade"))
    dataset_id = db.Column(
        db.Integer, db.ForeignKey("dataset.dataset_id", ondelete="cascade")
    )
    action = db.Column(db.String, nullable=False)
    notes = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def __init__(self, user_id, dataset_id, action, notes=None):
        self.user_id = user_id
        self.dataset_id = dataset_id
        self.action = action
        self.notes = notes
        
    def __repr__(self):
        return f"<DatasetActionHistory(item_id={self.item_id},dataset_id={self.dataset_id}, name={self.dataset_name}, action={self.action}, notes={self.notes}, timestamp={self.timestamp}>"
        
