from db import db

DatasetOwner = db.Table('dataset_owners',
                        db.Column('id', db.Integer, primary_key=True),
                        db.Column('dataset_id', db.Integer, db.ForeignKey('dataset.dataset_id')),
                        db.Column('owner_id', db.Integer, db.ForeignKey('user.user_id')))

RoleMember = db.Table('role_members',
                      db.Column('id', db.Integer, primary_key=True),
                      db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
                      db.Column('role_id', db.Integer, db.ForeignKey('role.role_id')))

RolePermission = db.Table('role_permissions',
                          db.Column('id', db.Integer, primary_key=True),
                          db.Column('role_id', db.Integer, db.ForeignKey('role.role_id')))
