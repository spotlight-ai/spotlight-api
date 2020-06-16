from flask_restful import Resource

from core.decorators import authenticate_token
from models.pii.pii import PIIModel
from schemas.pii.pii import PIISchema

pii_schema = PIISchema()


class PIICollection(Resource):
    @authenticate_token
    def get(self, user_id):
        """
        Returns the list of currently accepted PII and their details.
        :param user_id: Currently logged in user ID.
        :return: List of PII markers
        """
        pii = PIIModel.query.all()

        return pii_schema.dump(pii, many=True)
