from flask_restful import Resource 
from Application.database.models import PlacePrices

class PlacesApi(Resource):
    def get(self):
        return PlacePrices.read_place_prices()