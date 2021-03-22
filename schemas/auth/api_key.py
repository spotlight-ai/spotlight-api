from db import ma
from models.auth.api_key import APIKeyModel


class APIKeySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = APIKeyModel
        include_fk = True
        ordered = True
