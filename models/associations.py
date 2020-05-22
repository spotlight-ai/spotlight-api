from db import db

# Table to store permissions that each role grants (many-to-many relationship).
RolePermission = db.Table('role_permissions',
                          db.Column('id', db.Integer, primary_key=True),
                          db.Column('role_id', db.Integer, db.ForeignKey('role.role_id')),
                          db.Column('pii_id', db.Integer, db.ForeignKey('pii_marker_base.id')))

# Master table to store PII types that are valid for role permissions.
pii_marker_base = db.Table('pii_marker_base',
                           db.Column('id', db.Integer, primary_key=True),
                           db.Column('pii_description', db.String, nullable=False))

# Table to store Role to Dataset sharing mappings (many-to-many relationship).
RoleDataset = db.Table('role_dataset',
                       db.Column('id', db.Integer, primary_key=True),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.role_id')),
                       db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.dataset_id')))

# Dataset Owners
DatasetOwner = db.Table('dataset_owner',
                        db.Column('id', db.Integer, primary_key=True),
                        db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.dataset_id')),
                        db.Column('owner_id', db.Integer, db.ForeignKey('user.user_id')))
