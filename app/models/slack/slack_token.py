from db import db


class SlackTokenModel(db.Model):
    __tablename__ = "slack_token"

    team_id = db.Column(db.String, primary_key=True)
    enterprise_id = db.Column(db.String, nullable=True)
    bot_token = db.Column(db.String, nullable=False)
    bot_id = db.Column(db.String, nullable=False)
    bot_user_id = db.Column(db.String, nullable=False)
    user_token = db.Column(db.String, nullable=True)

    def __repr__(self):
        return (
            f"SlackTokensModel(team_id={self.team_id}, enterprise_id={self.enterprise_id}, "
            f"bot_token={self.bot_token}, bot_id={self.bot_id}, bot_user_id={self.bot_user_id}, "
            f"user_token={self.user_token}"
        )

    def __str__(self):
        return f"SlackBotToken - Team: {self.team_id}, Enterprise: {self.enterprise_id}"
