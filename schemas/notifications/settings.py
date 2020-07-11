from db import ma
from models.notifications.settings import NotificationSettingsModel

class NotificationSettingsSchema(ma.ModelSchema):
    class Meta:
        model = NotificationSettingsModel
        include_fk = True



