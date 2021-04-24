from models.notifications.notification import NotificationModel
import marshmallow_sqlalchemy as ma

class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NotificationModel
        ordered = True
        dump_only = ("created_ts", "last_updated_ts")
