from db import db

class NotificationSettingsModel(db.Model):
    __tablename__ = "notification_settings"
    __tableargs__ = db.UniqueConstraint(
        "user_id", "notification_type"
    )
    
    setting_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="cascade"), nullable=False)
    notification_type = db.Column(db.String, default="email", nullable=False)
    approved = db.Column(db.Boolean, default=True)
    
    def __init__(self,user_id, notification_type="email", approved=True):
        self.user_id = user_id
        self.notification_type = notification_type
        self.approved = approved
        
    def __repr__(self):
        return f"<Notification settings (id={self.setting_id}, user_id={self.user_id}, notification_type={self.notification_type}, approved={self.approved}>"
