from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError

from core.decorators import authenticate_token
from db import db
from models.auth.user import UserModel
from models.notifications.settings import NotificationSettingsModel

from schemas.notifications.settings import NotificationSettingsSchema

notification_settings_schema = NotificationSettingsSchema()

class NotificationSettingsCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        user_notification_settings = NotificationSettingsModel.query.filter(NotificationSettingsModel.user_id == user_id).all()
        
        return notification_settings_schema.dump(user_notification_settings, many=True)
    
    @authenticate_token    
    def post(self, user_id):
        try:
            user_settings = NotificationSettingsModel.query.filter(NotificationSettingsModel.user_id == user_id).all()
            request_body = request.get_json(force=True)
            
            for setting in user_settings:
                if setting.notification_type == request_body.get('notification_type',''):
                    abort(400, "This notification setting has already been initialised for the user.")
                    
            request_body['user_id'] = user_id
            notification_setting = notification_settings_schema.load(request_body)
        
            db.session.add(notification_setting)
            db.session.commit()
            
            return notification_settings_schema.dump(notification_setting), 201
        except ValidationError as err:
            abort(422, err.messages)

class NotificationSettings(Resource):
    @authenticate_token
    def put(self, user_id, setting_id):
        request_body = request.get_json(force=True)
        notification = NotificationSettingsModel.query.filter(NotificationSettingsModel.setting_id == setting_id).first()
        
        if 'approved' in request_body:
            #The value of 'approved' in the request_body is a string and not a boolean. Converting it explicitly...
            
            if request_body['approved'] == "False" :
                notification.approved = False
            else:
                notification.approved = True
            
        if 'notification_type' in request_body:
            notification.notification_type = request_body['notification_type']
            
        db.session.commit()
            
        return notification_settings_schema.dump(notification)
        
