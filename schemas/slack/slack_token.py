from db import ma
from models.slack.slack_token import SlackTokenModel


class SlackTokenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SlackTokenModel
