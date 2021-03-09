from db import db

# Table to store permissions that each role grants (many-to-many relationship).
RolePermission = db.Table(
    "role_permissions",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.role_id", ondelete="cascade")),
    db.Column(
        "pii_id",
        db.Integer,
        db.ForeignKey("pii_marker_base.pii_id", ondelete="cascade"),
    ),
)

# Table to store Role to Dataset sharing mappings (many-to-many relationship).
RoleDataset = db.Table(
    "role_dataset",
    db.Column("id", db.Integer, primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.role_id", ondelete="cascade")),
    db.Column(
        "dataset_id",
        db.Integer,
        db.ForeignKey("dataset.dataset_id", ondelete="cascade"),
    ),
)

# Table to store Dataset to Owner relationships (many-to-many relationships).
DatasetOwner = db.Table(
    "dataset_owner",
    db.Column("id", db.Integer, primary_key=True),
    db.Column(
        "dataset_id",
        db.Integer,
        db.ForeignKey("dataset.dataset_id", ondelete="cascade"),
    ),
    db.Column(
        "owner_id", db.Integer, db.ForeignKey("user.user_id", ondelete="cascade")
    ),
)

WorkspaceMember = db.Table(
    "workspace_member",
    db.Column("workspace_id", db.Integer, db.ForeignKey("workspace.workspace_id", ondelete="cascade")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id", ondelete="cascade")),
    db.Column("is_owner", db.Boolean, default=False)
)
