from datetime import datetime

from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError

from core.decorators import authenticate_token
from core.errors import NotificationErrors
from db import db
from models.notifications.notification import NotificationModel
from schemas.notifications.notifications import NotificationSchema

notification_schema = NotificationSchema()


class NotificationCollection(Resource):
    @authenticate_token
    def get(self, user_id):
        """
        Retrieves the list of un-viewed notifications for a user.
        :param user_id: Currently logged in user ID.
        :return: List of notification objects.
        """

        notifications = (
            NotificationModel.query.filter_by(user_id=user_id, viewed=False)
            .order_by(NotificationModel.last_updated_ts.desc())
            .all()
        )

        if len(notifications) < 5:
            notifications = (
                NotificationModel.query.filter_by(user_id=user_id)
                .order_by(
                    NotificationModel.viewed, NotificationModel.last_updated_ts.desc()
                )
                .limit(5)
            )

        return notification_schema.dump(notifications, many=True)


class Notification(Resource):
    @authenticate_token
    def patch(self, user_id, notification_id):
        """
        Updates a notification object.
        :param user_id: Currently logged in user ID.
        :param notification_id: Notification unique identifier.
        :return: Updated notification object.
        """
        data = request.get_json(force=True)

        notification = NotificationModel.query.filter_by(
            notification_id=notification_id
        ).first()

        if not notification:
            abort(404, NotificationErrors.NOTIFICATION_NOT_FOUND)

        if notification.user_id != user_id:
            abort(401, NotificationErrors.USER_DOES_NOT_HAVE_PERMISSION)

        try:
            notification_schema.load(data, instance=notification, partial=True)
            notification.last_updated_ts = datetime.utcnow()
            db.session.commit()

            return notification_schema.dump(notification)
        except ValidationError as err:
            abort(422, err.messages)
