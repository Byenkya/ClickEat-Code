from flask_restful import Resource, marshal_with, fields, reqparse
from Application.flask_imports import request, jsonify
from Application.database.models import Customer, CustomerAddress
from Application.helpers.generators import TokenGenerator
from Application.utils.email import reset_email
from Application.flask_imports import url_for

address_fields = {
    "id": fields.Integer,
    "county": fields.String,
    "sub_county": fields.String,
    "village": fields.String,
    "other_details": fields.String,
    "is_default": fields.Boolean,
    "customer_id": fields.Integer
}

class CheckUserEmail(Resource):
    def post(self):
        email = request.json["email"]
        if email:
            customer = Customer().google_sign_in(email=email)
            return customer


class SignUpApi(Resource):
    def post(self):
        customer_names = request.json["names"]
        email = request.json["email"]
        contact = request.json["contact"]
        profile_picture = request.json["profile_picture"]
        password = request.json["password"]
        customer_details = Customer()(
            name=customer_names,
            email=email,
            contact=contact,
            profile_picture=profile_picture,
            password=password
        )   

        if customer_details:
            customer = Customer().google_sign_in(email=email)
            return customer

class CustomerApi(Resource): 
    def post(self):
        print(request.json)
        customer_names = request.json["names"]
        email = request.json["email"]
        contact = request.json["contact"]
        profile_picture = request.json["profile_picture"]
        password = request.json["password"]
        customer_details = Customer()(
                                name=customer_names,
                                email=email,
                                contact=contact,
                                profile_picture=profile_picture,
                                password=password
                            )

        if customer_details:
            response = {
                    "status": "success",
                    "message": "Your Information was stored successfully!",
                    "data": 0
                }

            return response
                
        else:
            customer = Customer().read_customer(contact=contact)
            if customer:

                response = {
                    "status": "failure",
                    "message": "User already exists!!",
                    "data":0
                } 

                return response
            else:

                response = {
                    "status": "failure",
                    "message": "Your Information was not saved!",
                    "data":0
                } 

                return response


class AuthenticationApi(Resource):
    def post(self):
        telephone = request.json["telephone"]
        password = request.json["password"] 
        customer_details = Customer.check_user(telephone=telephone, password=password)
        return customer_details


class CustomerAddressAPi(Resource):
    # @marshal_with(address_fields)
    def get(self, id):
        customer_addresses = CustomerAddress.get_customer_addresses(id)

        return customer_addresses

    def delete(self, id):
        if(CustomerAddress.delete_customer_address(id)):
            return jsonify(
                status="success",
                message="Address was deleted successfully!!.",
                data=0
            )

        else:
            return jsonify(
                status="error",
                message="Address was not deleted!!",
                data=0
            )

class AddNewCustomerAddressApi(Resource):
    def post(self,id):
        county = request.json['county']
        sub_county = request.json['sub_county']
        village = request.json['village']
        other_details = request.json['other_details']
        is_default = request.json["is_default"]

        if(CustomerAddress()(
            county=county,
            sub_county=sub_county,
            village=village,
            other_details=other_details,
            is_default=is_default,
            customer_id=id)):
            customer_addresses = CustomerAddress.get_customer_addresses(id)

            return customer_addresses

    def put(self, id):
        county = request.json['county']
        sub_county = request.json['sub_county']
        village = request.json['village']
        other_details = request.json['other_details']

        if(CustomerAddress.update_customer_address(
            address_id=id,
            county=county,
            sub_county=sub_county,
            village=village,
            other_details=other_details,
        )):
            return jsonify(
                status="success",
                message="Address was updated successfully!!.",
                data=0
            )
        
        else:
            return jsonify(
                status="error",
                message="Address was not updated successfully!!.",
                data=0
            )




class CustomerUpdateInformationApi(Resource):
    def put(self, id):
        customer_names = request.json["names"]
        email = request.json["email"]
        contact = request.json["contact"]
        second_contact = request.json["secondContact"]

        customer = Customer.read_customer(id=id)

        if customer:
            if(customer.update_customer(name=customer_names,email=email,contact=contact,second_contact=second_contact)):
                new_user_info = customer.serializer()
                new_user_info["token"] = "clickEattokenmissing"
                
                return new_user_info


class UpdateCustomerAccountInfo(Resource):
    def put(self, id):
        old_password = request.json["oldPassword"]
        new_password = request.json["newPassword"]

        customer = Customer.read_customer(id=id)

        if customer:
            if(customer.change_password(old_password=old_password, new_password=new_password)):
                return {
                    "status": "success",
                    "message": "Password was updated successfully!!.",
                    "data": 0
                }
            else:
                return {
                    "status": "error",
                    "message": "Password was not updated successfully!!.",
                    "data": 0
                }  


forgot_password_args = reqparse.RequestParser()
forgot_password_args.add_argument("email", type=str, required=True)
class ForgotPasswordResource(Resource):
    def post(self):
        args = forgot_password_args.parse_args()
        user = Customer.read_customer(email=args["email"])
        if user != None:
            token_gen = TokenGenerator(user=user)
            token = token_gen.generate_password_reset_token()
            mail_ = reset_email
            mail_.context = dict(
                user_name=user.name,
                token=token
            )
            mail_.recipients = [user.email]
            mail_.text = "To reset your password visit the following link "+url_for('set_new_password', token=token, _external=True)+ "\n if you did not request for this email then ignore."
            mail_.send()

            return jsonify(
                status = "success",
                message="Check your email inbox for password reset link.",
                data = 0
            )

        else:
            email = args["email"]
            return jsonify(
                status = "error",
                message= "This email: {} is not registered with clickeat".format(email),
                data = 0
            )



