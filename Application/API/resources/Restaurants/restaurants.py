from flask_restful import Resource, fields, marshal_with
from Application.flask_imports import jsonify
from Application.database.models import Resturant

class RestaurantApi(Resource):
    def get(self):
        rests = Resturant.read_restaurants()

        return jsonify(restaurants = [restaurant.serialize() for restaurant in rests])