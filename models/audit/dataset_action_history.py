from datetime import datetime

from db import db


class DatasetActionHistoryModel(db.Model):
    __tablename__ = "audit_dataset_action"
    
    item_id = db.Column(db.Integer, primary_key=True)
    dataset_id = db.Column(db.Integer)
    action = db.Column(db.String, nullable=False)
    notes = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    
    def __init__(self, dataset_id, action, notes=None):
        self.dataset_id = dataset_id
        self.action = action
        self.notes = notes
