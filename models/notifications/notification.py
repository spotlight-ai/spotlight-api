from datetime import datetime
from string import Template

from loguru import logger
from sendgrid.helpers.mail import Mail

from db import db
from models.user import UserModel
from resources.auth.util import send_email


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

    def send_notification_email(self, permissions):
        user_id = self.user_id
        user = UserModel.query.filter(UserModel.user_id == user_id).first()

        user_name = f"{user.first_name} {user.last_name}"
        user_email = user.email

        email_title = self.title
        email_detail = self.detail

        permissions.sort()
        permission_text = f"<br><b>You have the following permissions:</b><br> {'<br>'.join(permissions)}"

        html_body = Template(
            open("./email_templates/notification.html").read()
        ).safe_substitute(
            title=email_title, detail=email_detail, permission=permission_text
        )

        logger.info(f"Loaded HTML template successfully. Sending email to {user_email}")

        message = Mail(
            from_email="hellospotlightai@gmail.com",
            to_emails=user_email,
            subject=f"SpotlightAI | Notification for {user_name}",
            html_content=html_body,
        )

        send_email(message)

        return
