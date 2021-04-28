from Application.flask_imports import Flask, make_response, abort
from Application import config
from flask_migrate import Migrate
from flask_restful import Api
import Application.extensions as ext

app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
        template_folder="routes/home/templates"
        
    )

#login Manager
login_manager = ext.login_manager
login_manager.init_app(app)
login_manager.login = "info"


app.config.from_object(config.DevelopmentConfig)


#flask mail
mail = ext.mail
mail.init_app(app)

# crsf protect
csrf = ext.csrf
csrf.init_app(app)

#Api Flask RestFul
api = Api(app, decorators=[csrf.exempt])

#celery
celery = ext.celery
celery.__init__(app)
celery.config_from_object(config.CeleryConfig)

#create the database
from Application.database.initialize_database import Base, engine, session
from Application.database.models import *

def init_db():  
    Base.metadata.bind = engine
    Base.metadata.create_all()

init_db()

#Initializing the admin blue print.
from Application.routes.admin.initialize_admin import admin, ad_views
admin.init_app(
    app,
    url = "/admin",
    index_view = ad_views.AdminHomeView(name="DashBoard", url="/admin")
)

#load manager user loader

login_manager.user_loader(load_user)

#register api routes
from Application.API.resources.Products.products import (ProductsApi, 
AddToCartApi, CartOperationApi, DrinksSubCatApi, DrinksApi, HomeProductsResource,
SearchedProductsResource, SubCategoryProductsApI)
from Application.API.resources.Products.comments import CommentsApi
from Application.API.resources.Products.product_rates import ProductRatingApi
from Application.API.resources.Restaurants.restaurants import RestaurantApi
from Application.API.resources.Places.places import PlacesApi
from Application.API.resources.Customer.customer import (
    CustomerApi, AuthenticationApi, CustomerAddressAPi, 
    CustomerUpdateInformationApi, UpdateCustomerAccountInfo, AddNewCustomerAddressApi, ForgotPasswordResource
    )
from Application.API.resources.Customer.customer_order import OrdersApi, CustomerOrdersApi


#product routes
api.add_resource(ProductsApi, '/api/v1/products/<int:id>')
api.add_resource(AddToCartApi, '/api/v1/addToCart')
api.add_resource(CartOperationApi, '/api/v1/cart_operations/<int:id>')
api.add_resource(CommentsApi, '/api/v1/product_comments/<int:id>')
api.add_resource(ProductRatingApi, '/api/v1/rate_product/<int:id>')
api.add_resource(DrinksSubCatApi, '/api/v1/drinks_sub_cat')
api.add_resource(DrinksApi, '/api/v1/drinks_based_on_sub_cat/<int:id>')
api.add_resource(HomeProductsResource, '/api/v1/home_products')
api.add_resource(SearchedProductsResource, '/api/v1/searched_products')
api.add_resource(SubCategoryProductsApI, '/api/v1/sub_cat_products/<int:id>')


#restaurants routes
api.add_resource(RestaurantApi, '/api/v1/restaurants')
   
#Arua places routes
api.add_resource(PlacesApi, '/api/v1/arua_places')

#customer routes
api.add_resource(CustomerApi, '/api/v1/register')
api.add_resource(AuthenticationApi, '/api/v1/customer_sign_in')
api.add_resource(CustomerAddressAPi, '/api/v1/customer_addresses/<int:id>')
api.add_resource(OrdersApi, '/api/v1/customer_order')
api.add_resource(CustomerOrdersApi, '/api/v1/customer_orders/<int:id>')
api.add_resource(CustomerUpdateInformationApi, '/api/v1/update_info/<int:id>')
api.add_resource(UpdateCustomerAccountInfo, '/api/v1/update_account_info/<int:id>')
api.add_resource(AddNewCustomerAddressApi, '/api/v1/add_address/<int:id>')
api.add_resource(ForgotPasswordResource, '/api/v1/forgot_password')


#Register Blueprints
from Application.routes.customer_care.routes import customer_care
from Application.flask_imports import _session, request

app.register_blueprint(customer_care)

@app.after_request
def after_request_function(response):
    if _session.get("new_token"):
        print(">>>>>>>>>>>>>>", _session["new_token"])
        new_headers = {
            "Authorization": "Basic: "+_session["new_token"]
        }
        response.headers.update(new_headers)
        _session.pop("new_token")

    return response

import base64
from Application.helpers.generators import TokenGenerator
@app.before_request
def before_request_function():
    if str(request.url_rule).startswith("/api/v1"):
        try:
            
            token = base64.b64decode(request.headers.get(
                "Authorization").split("Basic ")[1]).decode("utf-8").split(":")[0]

            if token:
                customer = TokenGenerator().verify_api_token(token)
                if customer:
                    pass
                else:
                    return None
            else:
                return None
        except:
            abort(404)

    return None

@app.teardown_request
def remove_session(exception=None):
    session.remove()