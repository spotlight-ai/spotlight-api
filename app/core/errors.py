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
    ALL_DATASETS_ALREADY_VERIFIED: str = "All datasets have already been previously verified."
    COULD_NOT_CREATE_JOB: str = "Unforseen error when attempting to create a job for the model."
    DOES_NOT_EXIST: str = "Dataset does not exist."
    GIVEN_USERS_DO_NOT_OWN: str = (
        "Cannot process this request as user(s) {not_an_owner} are not the owner(s) of this "
        "dataset."
    )
    MUST_HAVE_OWNER: str = "Dataset must have at least one owner."
    MUST_SUPPLY_USER_ID: str = "Must supply user ID to perform this operation."
    NO_NEW_OWNERS: str = "No new owners to be added."
    NOT_AUTHORIZED: str = "This user is not authorized to access metadata for this dataset."
    USER_DOES_NOT_OWN: str = "User does not own this dataset."


class FileErrors:
    FILE_NOT_FOUND = "File was not found."
    DOES_NOT_HAVE_PERMISSION = "User does not have permission to view this file."


class UserErrors:
    USER_NOT_FOUND = "User or users not found."
    USER_ALREADY_EXISTS = "User already exists."
    EDITING_INVALID_FIELD = "Cannot edit this field."


class NotificationErrors:
    NOTIFICATION_NOT_FOUND = "Notification not found."
    USER_DOES_NOT_HAVE_PERMISSION = (
        "User does not have permission to view this notification."
    )
    CANNOT_UPDATE_FIELDS = 'Only "viewed" property can be updated.'


class JobErrors:
    JOB_ACTIVE = "There are currently active jobs for this dataset."


class DatabaseErrors:
    ISSUE_WRITING_TO_DB = "There was an issue writing to the database. Ensure query params are the correct type."


class SlackErrors:
    TOKEN_ALREADY_EXISTS = "A token already exists for this team ID."
    NO_TOKEN_FOUND = "No token was found for this team ID."


class MaskingErrors:
    PII_TYPE_NOT_SUPPORTED = "The requested PII type is not supported for masking."


class AuthenticationErrors:
    MISSING_AUTH_HEADER = "Missing authentication header."
    UNAUTHORIZED_API_KEY = "Unauthorized API key."
    INCORRECT_API_KEY = "Incorrect API key."
    INCORRECT_CREDS = "Incorrect credentials."
