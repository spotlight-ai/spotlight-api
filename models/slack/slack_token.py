from db import db


class SlackTokenModel(db.Model):
    __tablename__ = "slack_token"
    
    team_id = db.Column(db.String, primary_key=True)
    enterprise_id = db.Column(db.String, nullable=True)
    bot_token = db.Column(db.String, nullable=False)
    bot_id = db.Column(db.String, nullable=False)
    bot_user_id = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return f"SlackTokensModel(team_id={self.team_id}, enterprise_id={self.enterprise_id}, " \
               f"bot_token={self.bot_token}, bot_id={self.bot_id}, bot_user_id={self.bot_user_id}"
    
    def __str__(self):
        return f"SlackBotToken - Team: {self.team_id}, Enterprise: {self.enterprise_id}"
