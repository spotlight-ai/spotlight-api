from marshmallow import Schema


class RolePermissionSchema(Schema):
    class Meta:
        fields = ('role_id', 'pii_id')
