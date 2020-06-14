from db import ma
from models.datasets.shared_user import SharedDatasetUserModel
from schemas.pii.pii import PIISchema
from schemas.user import UserSchema


class SharedDatasetUserSchema(ma.Schema):
    class Meta:
        model = SharedDatasetUserModel
        strict = True

    permissions = ma.List(ma.Nested(PIISchema))
    user = ma.Nested(UserSchema)
