import os

from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sendgrid import SendGridAPIClient

db = SQLAlchemy()
ma = Marshmallow()
sg = SendGridAPIClient(os.environ.get("SENDGRID_KEY"))
