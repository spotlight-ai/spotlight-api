from flask import abort
from sqlalchemy.sql.expression import true

from core.constants import NotificationConstants
from core.errors import RoleErrors
from models.notifications.notification import NotificationModel
from models.roles.role import RoleModel
from models.roles.role_member import RoleMemberModel


def retrieve_role(role_id, user_id):
    """
    Returns a role if it is owned by the given user. If not, None is returned.
    :param role_id: Role ID to be returned.
    :param user_id: ID of the user to verify ownership.
    :return: Role object if user is owner, otherwise None.
    """
    role = RoleModel.query.filter(
        (RoleModel.role_id == role_id)
        & RoleModel.members.any(
            (RoleMemberModel.user_id == user_id) & (RoleMemberModel.is_owner == true())
        )
    ).first()

    if not role:
        abort(401, RoleErrors.MISSING_NO_PERMISSIONS)

    return role


def send_notifications(session, role, datasets, new_members):
    """
    Adds notifications to the session for each member in the role.
    :param session: Current DB session
    :param role: Role to send notifications to.
    :param datasets: Datasets that have been shared for detail.
    :return: None
    """
    role_permission_descriptions = [perm.long_description for perm in role.permissions]
    role_dataset_names = [d.get("dataset_name") for d in datasets]

    role_dataset_names.sort()

    for member in new_members:
        # Add notification for each new member of the role
        notification = NotificationModel(
            user_id=member,
            title=NotificationConstants.DATASET_SHARED_TITLE,
            detail=f"{NotificationConstants.DATASET_SHARED_DETAIL}-{', '.join(role_dataset_names)}",
        )
        notification.send_notification_email(role_permission_descriptions)
        session.add(notification)
