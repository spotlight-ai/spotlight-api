from db import db
from models.associations import RolePermission


class PIIModel(db.Model):
    __tablename__ = 'pii_marker_base'
    
    pii_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    long_description = db.Column(db.String)
    category = db.Column(db.String)
    
    roles = db.relationship("RoleModel", secondary=RolePermission, back_populates='permissions')
    
    def __init__(self, description, long_description, category):
        self.description = description
        self.long_description = long_description
        self.category = category
    
    def __repr__(self):
        return f'<PIIModel(ID: {self.pii_id} - {self.description})>'
