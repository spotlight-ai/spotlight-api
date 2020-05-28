from db import db
from models.associations import RolePermission, UserDatasetPermission
from models.datasets.shared_user import SharedDatasetUserModel


class PIIModel(db.Model):
    __tablename__ = 'pii_marker_base'
    
    pii_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    
    roles = db.relationship("RoleModel", secondary=RolePermission, back_populates='permissions')
    shared_datasets = db.relationship(SharedDatasetUserModel, secondary=UserDatasetPermission,
                                      back_populates='permissions')
    
    def __init__(self, description):
        self.description = description
    
    def __repr__(self):
        return f'<PIIModel(ID: {self.pii_id} - {self.description})>'
