from Application.flask_imports import Flask, make_response, abort
from Application import config
# from flask_migrate import Migrate, MigrateCommand, Manager
from flask_restful import Api
import Application.extensions as ext
from flask_cors import CORS

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
login_manager.login_view = "index_bp.signin_signup"

# cors
CORS(app, resources={r'/api/*': {'origins': '*'}})


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
from Application.database.initialize_database import Base, engine, session, pwd_context
from Application.database.models import *

# class db(object):
#     engine = engine
#     metadata = Base.metadata

def init_db():  
    Base.metadata.bind = engine
    Base.metadata.create_all()

#flask migrate
# migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)

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

# load template filters
from Application import template_filters

#register api routes
from Application.API.resources.Products.products import (ProductsApi, 
AddToCartApi, CartOperationApi, DrinksSubCatApi, DrinksApi, HomeProductsResource,
SearchedProductsResource, SubCategoryProductsApI, CategoryProductsApI, 
FetchAllSubCategoriesApi, GetProductByIdResource)
from Application.API.resources.Products.comments import CommentsApi
from Application.API.resources.Products.product_rates import ProductRatingApi
from Application.API.resources.Restaurants.restaurants import RestaurantApi, GetRestaurantById
from Application.API.resources.Places.places import PlacesApi
from Application.API.resources.Customer.customer import (
    CustomerApi, AuthenticationApi, CustomerAddressAPi, 
    CustomerUpdateInformationApi, UpdateCustomerAccountInfo, AddNewCustomerAddressApi, ForgotPasswordResource,
    SignUpApi, CheckUserEmail
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
api.add_resource(CategoryProductsApI, '/api/v1/cat_products')
api.add_resource(FetchAllSubCategoriesApi, '/api/v1/fetch_all_subcats')
api.add_resource(CheckUserEmail, '/api/v1/check_user_email')
api.add_resource(GetProductByIdResource, '/api/v1/get_product/<int:id>')


#restaurants routes
api.add_resource(RestaurantApi, '/api/v1/restaurants')
api.add_resource(GetRestaurantById, '/api/v1/get_restaurant/<int:id>')
   
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
api.add_resource(SignUpApi, '/api/v1/register_via_email')


#Register Blueprints
from Application.routes.customer_care.routes import customer_care
from Application.flask_imports import _session, request

# load web app views
from Application.views.index import index_bp
from Application.views.product import product_bp
from Application.views.cart import cart_bp
from Application.views.customer import customer_bp
from Application.views.order import order_bp
from Application.views.checkout import checkout_bp

app.register_blueprint(index_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(order_bp)
app.register_blueprint(checkout_bp)

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
    if request.args.get("platform")=="web":
        return
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

from Application.flask_imports import *
from Application.helpers.generators import TokenGenerator
from Application.utils.email import reset_email
from Application.database.models import Customer, Resturant, StaffAccounts
from Application.routes.password_reset.forms import ForgotPasswordForm, NewPasswordForm

@app.route("/forgot_password/<string:user_type>", methods=["GET", "POST"])
def forgot_password(user_type):
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        if user_type == "customer":
            user = Customer.read_customer(email=form.email.data.strip())
        elif user_type == "clickeat_employee":
            user = StaffAccounts.read_user(email=form.email.data)
        else:
            flash("Failed to send password reset.", "danger")
            return redirect(url_for(".forgot_password", user_type=user_type))

        if user is not None:
            try:
                token_gen = TokenGenerator(user=user)
                token = token_gen.generate_password_reset_token()
                mail_ = reset_email
                # mail_.context = dict(
                #     user_name=user.name,
                #     token=token
                # )
                mail_.text = "To reset your password visit the following link "+url_for('set_new_password', token=token, _external=True)+ "\n if you did not request for this email then ignore."
                mail_.recipients = [user.email]
                mail_.send()  
                flash("If you provided a right email, check your email inbox for password reset link.", "success")
                return redirect(url_for(".forgot_password", user_type=user_type))

            except Exception as e:
                print("Error whilst sending email: ", e)

       

    context = dict(form=form, user_type=user_type)
    return render_template("reset.html", **context)

@app.route("/new_password/<string:token>", methods=["GET", "POST"])
def set_new_password(token):
    form = NewPasswordForm()
    if form.validate_on_submit():
        token_gen = TokenGenerator()
        token_gen.verify_password_token(token)
        user = token_gen.user
        if user != None:
            customer = Customer.read_customer(id=user.id)
            if customer:
                customer.password = form.new_password.data
            else:
                user.password = pwd_context.hash(form.new_password.data)
            session.commit()
            flash("Your new password has been reset. Please try to log in with the new password.", "success")
        else:
            flash("Please request a new password reset. Either this link is invalid or expired.", "danger")
    context = dict(form=form,token=token)
    return render_template("new_password.html",**context)

app.config['LOG_FILE'] = 'application.log'

# RECEPIENTS = ['jbyenkyaaaron@gmail.com', 'tayebwaian0@gmail.com', 'willbrodmutesi@gmail.com']

# if not app.debug:
#     import os
#     import logging
#     from logging import FileHandler, Formatter
#     from logging.handlers import SMTPHandler
#     file_handler = FileHandler(app.config['LOG_FILE'])
#     file_handler.setLevel(logging.INFO)
#     app.logger.addHandler(file_handler)

#     mail_handler = SMTPHandler(
#         ("smtp.gmail.com", 587), os.environ["MAIL_USERNAME"], RECEPIENTS,
#         'Error occurred in your ClickEat application',
#         (os.environ["MAIL_USERNAME"], os.environ['MAIL_PASSWORD']), secure=()
#     )

#     mail_handler.setLevel(logging.ERROR)
#     app.logger.addHandler(mail_handler)

#     for handler in [file_handler, mail_handler]:
#         handler.setFormatter(
#             Formatter(
#                 '%(asctime)s %(levelname)s: %(message)s '
#                 '[in %(pathname)s: %(lineno)d]'
#             )
#         )