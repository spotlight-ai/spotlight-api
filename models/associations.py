from db import db

DatasetOwner = db.Table('dataset_owners',
                        db.Column('id', db.Integer, primary_key=True),
                        db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.dataset_id')),
                        db.Column('owner_id', db.Integer, db.ForeignKey('user.user_id')))
