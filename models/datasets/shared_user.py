from db import db
from models.associations import UserDatasetPermission


class SharedDatasetUserModel(db.Model):
    __tablename__ = "shared_dataset_user"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.dataset_id"))
    share_expires = db.Column(db.DateTime, nullable=True)

    permissions = db.relationship(
        "PIIModel",
        secondary=UserDatasetPermission,
        back_populates="shared_datasets",
        cascade="all, delete",
    )
    user = db.relationship("UserModel", backref="shared_datasets")

    def __init__(self, user_id, dataset_id, share_expires=None):
        self.user_id = user_id
        self.dataset_id = dataset_id
        self.share_expires = share_expires

    def __repr__(self):
        return f"<SharedDatasetUserModel> (user_id={self.user_id}, dataset_id={self.dataset_id}, share_expires={self.share_expires})"

    def __str__(self):
        return f"Dataset {self.dataset_id} has been shared with user {self.user_id} until {self.share_expires}."
