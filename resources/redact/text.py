import os

import requests
from flask import request
from flask_restful import Resource


class RedactText(Resource):
    def post(self):
        body = request.get_json(force=True)
        url = f'http://{os.getenv("MODEL_HOST")}:{os.getenv("MODEL_PORT")}/predict/text'
        data = {'text': body.get('text')}
        
        r = requests.post(url=url, json=data)
        return r.json()
