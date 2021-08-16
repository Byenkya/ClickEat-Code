from flask_restful import Resource, marshal_with, fields
from Application.flask_imports import request
from Application.database.models import Order
from datetime import datetime

def check_for_pre_order_date(date):
    if date != "":
        date_ = date.split("-")
        return datetime(int(date_[0]),int(date_[1]),int(date_[2]),int(date_[3]),int(date_[4]))
    else:
        return datetime.now()

class OrdersApi(Resource):
    def post(self):
        method = request.json["payment_method"]
        customer_id = request.json["customer_id"]
        delivery_contact = request.json["deliveryContact"]
        delivery_fee = request.json["deliveryFee"]
        address = request.json["address"]
        county = address['county']
        sub_county = address['sub_county']
        village = address['village']
        other_details = address['other_details']
        pre_order = request.json["pre_order"]
        pre_order_time = check_for_pre_order_date(request.json["pre_order_date"])

        if(
            Order.place_customer_order(
            payment_method=method,
            customer_id=customer_id,
            county=county,
            sub_county=sub_county,
            village=village,
            other_details=other_details,
            delivery_contact=delivery_contact,
            delivery_fee=delivery_fee,
            pre_order=pre_order,
            pre_order_time=pre_order_time
            )):
            response = {
                "status":"success",
                "message": "Order placed successfully.",
                "data": 0
            }

            return response

        else:

            response = {
                "status": "error",
                "message": "There was a problem while trying to place your order. Please try again",
                "data": 0
            }

            return response

class CustomerOrdersApi(Resource):
    def get(self, id):
        customer_orders = Order.read_customer_orders(id)
        return customer_orders

    def post(self, id):
        customer_id = id
        reason = request.json["reason"]

        Order.terminate_order(customer_id=customer_id, reason=reason)
        
        return Order.read_customer_orders(customer_id)