class RoleErrors:
    MISSING_NO_PERMISSIONS = (
        "Role either does not exist or user does not have permissions."
    )
    PERMISSION_ALREADY_PRESENT = "Permissions already present"
    PERMISSIONS_MISSING = "Permissions missing"
    CREATOR_MUST_BE_OWNER = "Creator must be listed as a dataset owner."
    MUST_HAVE_OWNER = "Role must have at least one owner."
    MEMBER_INCORRECT_FIELDS = (
        "Body must have only the accepted keys: ['owners', 'users']"
    )
    MEMBER_ALREADY_EXISTS = "Role member already exists."
    DATASET_ALREADY_PRESENT = "Role already has access to this dataset."
    DATASET_NOT_PRESENT = "Dataset not present in the role."


class DatasetErrors:
    USER_DOES_NOT_OWN = "User does not own this dataset."
    MUST_HAVE_OWNER = "Dataset must have at least one owner."
    DOES_NOT_EXIST = "Dataset does not exist."


class UserErrors:
    USER_NOT_FOUND = "User or users not found."
    USER_ALREADY_EXISTS = "User already exists."
    EDITING_INVALID_FIELD = "Cannot edit this field."

class AuditErrors:
    NO_DATASET_OWNED = "User does not own any dataset."

class NotificationErrors:
    NOTIFICATION_NOT_FOUND = "Notification not found."
    USER_DOES_NOT_HAVE_PERMISSION = (
        "User does not have permission to view this notification."
    )
    CANNOT_UPDATE_FIELDS = 'Only "viewed" property can be updated.'


class DatabaseErrors:
    ISSUE_WRITING_TO_DB = "There was an issue writing to the database. Ensure query params are the correct type."
