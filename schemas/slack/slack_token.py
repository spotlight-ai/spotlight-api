from db import ma
from models.slack.slack_token import SlackTokenModel


class SlackTokenSchema(ma.ModelSchema):
    class Meta:
        model = SlackTokenModel
