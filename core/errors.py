class RoleErrors:
    MISSING_NO_PERMISSIONS = 'Role either does not exist or user does not have permissions.'
    PERMISSION_ALREADY_PRESENT = 'Permissions already present'
    PERMISSIONS_MISSING = 'Permissions missing'
    CREATOR_MUST_BE_OWNER = 'Creator must be listed as a dataset owner.'
    MUST_HAVE_OWNER = 'Role must have at least one owner.'
    MEMBER_INCORRECT_FIELDS = 'Body must have only the accepted keys: [\'owners\', \'users\']'
    MEMBER_ALREADY_EXISTS = 'Role member already exists.'
