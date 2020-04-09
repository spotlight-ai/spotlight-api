from db import db
import datetime

class DatasetOwnerModel(db.Model):
    __tablename__="dataset_owner"

    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.dataset_id'), primary_key=True)

    def __init__(self, owner_id, dataset_id):
        self.owner_id = owner_id
        self.dataset_id = dataset_id

    def __repr__(self):
            return f"<DatasetOwner {self.owner_id} - DatasetID {self.dataset_id}>"


