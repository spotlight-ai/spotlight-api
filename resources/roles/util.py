from flask import abort
from sqlalchemy.sql.expression import true

from core.errors import RoleErrors
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
        & (RoleMemberModel.user_id == user_id)
        & (RoleMemberModel.is_owner == true())
    ).first()

    if not role:
        abort(401, RoleErrors.MISSING_NO_PERMISSIONS)

    return role
