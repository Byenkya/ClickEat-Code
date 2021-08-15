from flask_restful import Resource, fields, marshal_with
from Application.flask_imports import jsonify
from Application.database.models import Resturant
from datetime import datetime
import pytz

class RestaurantApi(Resource):
    def get(self):
        time_zone = pytz.timezone("Africa/Kampala")
        current_time = time_zone.localize(datetime.now())
        rests = Resturant.read_restaurants()
        operational_restaurants = []
        for restaurant in rests:
            if restaurant.approved:
                if current_time.hour >= restaurant.operation_start_time.hour and current_time.hour <= restaurant.operation_stop_time.hour:
                    rest = restaurant.serialize()
                    rest["operational_status"] = True
                    operational_restaurants.append(rest)
                else:
                    rest = restaurant.serialize()
                    operational_restaurants.append(rest)
                    
        return jsonify(restaurants = operational_restaurants)