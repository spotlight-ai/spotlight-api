from datetime import datetime

from db import db


class NotificationModel(db.Model):
    __tablename__ = "notification"

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="cascade"))
    title = db.Column(db.String, nullable=False)
    detail = db.Column(db.String)
    viewed = db.Column(db.Boolean, nullable=False, default=False)
    created_ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    last_updated_ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def __init__(self, user_id, title, detail=None, viewed=False):
        self.user_id = user_id
        self.title = title
        self.detail = detail
        self.viewed = viewed

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(user_id={self.user_id}, title={self.title}, detail={self.detail}, "
            f"created_ts={self.created_ts}, last_updated_ts={self.last_updated_ts}, viewed={self.viewed})"
        )

    def __str__(self):
        return f"Notification ({self.created_ts}): {self.title} - {self.detail}"
