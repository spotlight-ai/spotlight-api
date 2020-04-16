from db import db

# Table to store which user owns which dataset. A dataset can have multiple owners (many-to-many relationship).
DatasetOwner = db.Table('dataset_owners',
                        db.Column('id', db.Integer, primary_key=True),
                        db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.dataset_id')),
                        db.Column('owner_id', db.Integer, db.ForeignKey('user.user_id')))

# Table to store the members of a given role. Also defines role owner relationship (many-to-many relationship).
RoleMember = db.Table('role_members',
                      db.Column('id', db.Integer, primary_key=True),
                      db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'), nullable=False),
                      db.Column('role_id', db.Integer, db.ForeignKey('role.role_id'), nullable=False),
                      db.Column('is_owner', db.Boolean, default=False, nullable=False))

# Table to store permissions that each role grants (many-to-many relationship).
RolePermission = db.Table('role_permissions',
                          db.Column('id', db.Integer, primary_key=True),
                          db.Column('role_id', db.Integer, db.ForeignKey('role.role_id')),
                          db.Column('pii_id', db.Integer, db.ForeignKey('pii_marker_base.id')))

# Master table to store PII types that are valid for role permissions.
pii_marker_base = db.Table('pii_marker_base',
                           db.Column('id', db.Integer, primary_key=True),
                           db.Column('pii_description', db.String, nullable=False))
