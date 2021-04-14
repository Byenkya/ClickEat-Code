from flask_restful import Resource
from Application.flask_imports import request
from Application.database.models import Rate


class ProductRatingApi(Resource):
    def get(self, id):
        rate = Rate.read_product_rate(id)

        return {"rate": rate}

    def post(self, id):
        rate = request.json["rate"]
        customer_id = request.json["customerID"]

        Rate()(rate=rate, customer_id=customer_id, product_id=id)

        rate = Rate.read_product_rate(id)

        return {"rate": rate}