from flask import abort, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from core.errors import SlackErrors
from db import db
from models.slack.slack_token import SlackTokenModel
from schemas.slack.slack_token import SlackTokenSchema

slack_token_schema = SlackTokenSchema()


class SlackTokenCollection(Resource):
    def get(self):
        tokens = SlackTokenModel.query.all()
        
        return slack_token_schema.dump(tokens, many=True)
    
    def post(self):
        try:
            data = request.get_json(force=True)
            
            token = slack_token_schema.load(data, session=db.session)
            team_id = data.get("team_id")
            existing_token = SlackTokenModel.query.get(team_id)
            
            if existing_token:
                abort(400, SlackErrors.TOKEN_ALREADY_EXISTS)
            
            db.session.add(token)
            db.session.commit()
            
            return None, 201
        
        except ValidationError as err:
            abort(422, err.messages)
        except IntegrityError as err:
            db.session.rollback()
            abort(400, err)
