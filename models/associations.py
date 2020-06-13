from db import db

# Table to store permissions that each role grants (many-to-many relationship).
RolePermission = db.Table('role_permissions',
                          db.Column('id', db.Integer, primary_key=True),
                          db.Column('role_id', db.Integer, db.ForeignKey('role.role_id')),
                          db.Column('pii_id', db.Integer, db.ForeignKey('pii_marker_base.pii_id')))

# Table to store Role to Dataset sharing mappings (many-to-many relationship).
RoleDataset = db.Table('role_dataset',
                       db.Column('id', db.Integer, primary_key=True),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.role_id')),
                       db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.dataset_id')))

# Table to store Dataset to Owner relationships (many-to-many relationships).
DatasetOwner = db.Table('dataset_owner',
                        db.Column('id', db.Integer, primary_key=True),
                        db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.dataset_id')),
                        db.Column('owner_id', db.Integer, db.ForeignKey('user.user_id')))

# Table to store permissions for individual users on a dataset (many-to-many relationship).
UserDatasetPermission = db.Table('shared_dataset_user_permissions',
                                 db.Column('id', db.Integer, primary_key=True),
                                 db.Column('dataset_user_id', db.Integer,
                                           db.ForeignKey('shared_dataset_user.id', ondelete='cascade',
                                                         onupdate='cascade')),
                                 db.Column('pii_id', db.Integer,
                                           db.ForeignKey('pii_marker_base.pii_id', ondelete='cascade',
                                                         onupdate='cascade')))
