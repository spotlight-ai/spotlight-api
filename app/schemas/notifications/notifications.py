from db import ma
from models.notifications.notification import NotificationModel


class NotificationSchema(ma.ModelSchema):
    class Meta:
        model = NotificationModel
        ordered = True
        dump_only = ("created_ts", "last_updated_ts")
