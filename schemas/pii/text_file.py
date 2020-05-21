from db import ma
from models.pii.text_file import TextFilePIIModel


class TextFilePIISchema(ma.ModelSchema):
    class Meta:
        model = TextFilePIIModel
        include_fk = True
        load_only = ('last_updated_ts',)
