from db import ma
from models.pii.file import FilePIIModel


class FilePIISchema(ma.ModelSchema):
    class Meta:
        model = FilePIIModel
        include_fk = True
        dump_only = ("last_updated_ts",)
