from db import ma
from models.pii.pii_columnar import ColumnarPIIModel


class ColumnarPIISchema(ma.ModelSchema):
    class Meta:
        model = ColumnarPIIModel
        include_fk = True
        dump_only = ("last_updated_ts",)
        