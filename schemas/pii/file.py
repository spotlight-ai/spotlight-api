from db import ma
from models.pii.file import FilePIIModel


class FilePIISchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FilePIIModel
        include_fk = True
        dump_only = ("last_updated_ts",)
