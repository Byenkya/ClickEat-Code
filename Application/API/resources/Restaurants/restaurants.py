from flask_restful import Resource, fields, marshal_with
from Application.flask_imports import jsonify
from Application.database.models import Resturant
from datetime import datetime
import pytz

ni_timezone = pytz.timezone('Africa/Nairobi')
timezone = pytz.timezone("Africa/Kampala")


#rest generatot
def rest_generator(data_list):
    _date = datetime.now(ni_timezone)
    current_time = _date.astimezone(timezone)
    for restaurant in data_list:
        _start_date = ni_timezone.localize(restaurant.operation_start_time)
        _end_date = ni_timezone.localize(restaurant.operation_stop_time)
        operation_start_time = _start_date.astimezone(timezone)
        operation_stop_time = _end_date.astimezone(timezone)
        if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
            rest = restaurant.serialize()
            rest["operational_status"] = True
            yield rest
        else:
            yield restaurant.serialize()

class RestaurantApi(Resource):
    def get(self):             
        return jsonify(restaurants = list(rest_generator(Resturant.read_restaurants())))

class GetRestaurantById(Resource):
    def get(self, id):
        rest = Resturant.read_restaurant(id)
        return rest.serialize()