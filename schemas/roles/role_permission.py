from marshmallow import Schema, fields, validate


class RolePermission(Schema):
    class Meta:
        strict = True

    role_id = fields.Int(required=True)
    dataset_id = fields.Int(required=True)
    allowed_fields = fields.List(fields.Str(), required=True)
