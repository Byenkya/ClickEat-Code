from sys import getsizeof
from flask_restful import Resource, fields, marshal_with, reqparse
from Application.flask_imports import request, jsonify
from Application.database.models import Products, Cart, Customer, SubCategory, Brand, HomeImages, TopSellingProducts, Category
from Application.database.initialize_database import session
from random import sample, shuffle
import pytz
from datetime import datetime  

timezone = pytz.timezone("Africa/Kampala")
ni_timezone = pytz.timezone('Africa/Nairobi')

#generators
def vegetables_generator(data_list):
    for product in data_list:
        if product.resturant.approved:
            _date = datetime.now(ni_timezone)
            current_time = _date.astimezone(timezone)
            _start_date = ni_timezone.localize(product.resturant.operation_start_time)
            _end_date = ni_timezone.localize(product.resturant.operation_stop_time)
            operation_start_time = _start_date.astimezone(timezone)
            operation_stop_time = _end_date.astimezone(timezone)
            if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                pdt = product.serialize()
                pdt["available"] = True
                yield pdt
            else:
                yield product.serialize()

def home_sub_cat_generator(data_list):
    for sub in data_list:
        product_image = Products.read_product_by_sub_cat(sub["sub_category_id"])
        if product_image:
            home_sub_cats = {}
            home_sub_cats['id'] = sub["sub_category_id"]
            home_sub_cats['subCatImage'] = product_image.product_picture 
            home_sub_cats['name'] = sub["name"]
            yield home_sub_cats

def all_products_generator(data_list):
    _date = datetime.now(ni_timezone)
    current_time = _date.astimezone(timezone)
    for product in data_list:
        if product.resturant.approved:
            if product.approved and product.suspend != True:
                _start_date = ni_timezone.localize(product.resturant.operation_start_time)
                _end_date = ni_timezone.localize(product.resturant.operation_stop_time)
                operation_start_time = _start_date.astimezone(timezone)
                operation_stop_time = _end_date.astimezone(timezone)
                if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                    pdt = product.serialize()
                    pdt["available"] = True
                    yield pdt
                else:
                    yield product.serialize()



product_fields = {
    "product_id": fields.Integer,
    "name": fields.String,
    "product_picture": fields.String,
    "description": fields.String,
    "price": fields.String,
    "resturant_id": fields.Integer,
    "resturant": fields.String,
    "brand_id": fields.Integer,
    "brand": fields.String,
    "sub_category_id": fields.Integer,
    "sub_category": fields.String
}  

class ProductsApi(Resource):
    def get(self, id):
        restaurant_products = Products.read_all_products(resturant_id=id)

        return restaurant_products

class GetProductByIdResource(Resource):
    def get(self, id):
        product = Products.read_product(id)

        return product.serialize()

class DrinksApi(Resource):
    def get(self, id):
        drinks_based_on_sub_cat = Products.read_all_products(sub_category_id=id)

        return drinks_based_on_sub_cat

class AddToCartApi(Resource):
    def post(self):
        product_id = request.json["product_id"]
        customer_id = request.json["customer_id"]
        product_name = request.json["product_name"]
        product_image = request.json["product_image"]
        unit_price = request.json["unit_price"]
        quantity = request.json["quantity"]
        served_with = "none"
        if "served_with" in request.json:
            served_with = request.json["served_with"]
        
        try:
            if "free_delivery" in request.json:
                free_delivery = request.json["free_delivery"]
        except:
            free_delivery = False

        try:
            if "restaurant" in request.json:
                restaurant = request.json["restaurant"]
        except:
            restaurant = "clickEat"

        customer = Customer.read_customer(id=customer_id)

        if customer:
            cart_item = Cart()(
                product_id=product_id,
                customer_id=customer_id,
                product_name=product_name,
                product_image=product_image,
                unit_price=unit_price,
                quantity=quantity,
                served_with=served_with,
                free_delivery=free_delivery,
                restaurant=restaurant
            )

            if cart_item:
                cart_size = str(Cart.cart_total_quantity_or_item_count(customer_id))

                return jsonify(
                    status = "success",
                    message = "Product added to cart successfully!!.",
                    data = cart_size
                )
            
            else:
                return jsonify(
                    status = "failure",
                    message = "Error Whilst adding Product to Cart!!.",
                    data = 0
                )

        else:

            return jsonify(status="failure",message="Customer doesnot exits!!.",data=0)

class CartOperationApi(Resource):       
    def get(self, id):
        cart_items = Cart.read_customer_cart_items(id)

        return cart_items

    def put(self, id):
        product_id = request.json["product_id"]
        quantity = request.json["quantity"]

        cart_items = Cart.update_cart_item(customer_id=id, product_id=product_id, quantity=quantity)

        return cart_items

    def delete(self, id):
        cart_items = Cart.delete_cart_item(id=id)

        return cart_items


#Drinks
class DrinksSubCatApi(Resource):  
    def get(self):
        return jsonify(drinksSubCat = [sub_cat.serialize() for sub_cat in SubCategory.read_drink_sub_categories()])


#Home products
class HomeProductsResource(Resource):
    def get(self):
        home_products = Products.home_products()
        home_products.append(
            {
                "id": 3, 
                "title":"Fruits & Vegetables", 
                "products": sample(list(vegetables_generator(session.query(Products).join(Products.sub_category).join(SubCategory.category).filter(Category.name=="Fruits and Vegetables").order_by(Products.product_id).all())), 2)
            }
        )
        
        top_selling_products = TopSellingProducts.read_all_top_discount_products()    
        return {
                "home_images_products": home_products,
                "home_images": HomeImages.home_images(), 
                "sub_cats": list(home_sub_cat_generator(SubCategory.read_sub_cat())),
                "all_products": list(all_products_generator(Products.read_products())),
                "top_selling_products": top_selling_products
            }

#generators
def sub_cat_generator(data_list):
    for sub in data_list:
        product_image = Products.read_product_by_sub_cat(sub["sub_category_id"])
        if product_image:
            home_sub_cats = {}
            home_sub_cats['id'] = sub["sub_category_id"]
            home_sub_cats['subCatImage'] = product_image.product_picture 
            home_sub_cats['name'] = sub["name"]

            yield home_sub_cats


#read subcategories
class FetchAllSubCategoriesApi(Resource):
    def get(self):
        return list(sub_cat_generator(SubCategory.read_sub_cat()))

#generator for seacrhed products
def search_pdt_generator(data_list):
    _date = datetime.now(ni_timezone)
    current_time = _date.astimezone(timezone)
    for product in data_list:
        if product.resturant.approved:
            if product.approved and product.suspend != True:
                _start_date = ni_timezone.localize(product.resturant.operation_start_time)
                _end_date = ni_timezone.localize(product.resturant.operation_stop_time)
                operation_start_time = _start_date.astimezone(timezone)
                operation_stop_time = _end_date.astimezone(timezone)
                if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                    pdt = product.serialize()
                    pdt["available"] = True
                    yield pdt
                else:
                    yield product.serialize()


#searched Products
searchStringsArgs = reqparse.RequestParser()
searchStringsArgs.add_argument("searchString", type=str)
class SearchedProductsResource(Resource):
    def get(self):
        # _date = datetime.now(ni_timezone)
        # current_time = _date.astimezone(timezone)
        args = searchStringsArgs.parse_args()
        products = []
        # searched_pdts = []
        if args.get("searchString", None):
            search_item = args["searchString"]
            products = session.query(Products).filter(
                Products.name.like(f"%{search_item}%")
                ).order_by(Products.product_id).all()
            
            if not products:
                products = session.query(Products).join(Products.brand)\
                    .filter(
                        Brand.name.like(f"%{search_item}%")
                    ).order_by(Products.product_id).all()

            if not products:
                products = session.query(Products).join(Products.sub_category)\
                    .filter(
                        SubCategory.name.like(f"%{search_item}%")
                    ).order_by(Products.product_id).all()
        return list(search_pdt_generator(products))

#category generator
def cat_pdt_generator(data_list):
    _date = datetime.now(ni_timezone)
    current_time = _date.astimezone(timezone)
    for product in data_list:
        if product.resturant.approved:
            if product.approved and product.suspend != True:
                _start_date = ni_timezone.localize(product.resturant.operation_start_time)
                _end_date = ni_timezone.localize(product.resturant.operation_stop_time)
                operation_start_time = _start_date.astimezone(timezone)
                operation_stop_time = _end_date.astimezone(timezone)
                if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                    pdt = product.serialize()
                    pdt["available"] = True
                    yield pdt
                else:
                    yield product.serialize()


#products based on category
categoryProductsStringsArgs = reqparse.RequestParser()
categoryProductsStringsArgs.add_argument("categoryName", type=str)
class CategoryProductsApI(Resource):
    def get(self):
        args = categoryProductsStringsArgs.parse_args()
        if args.get("categoryName", None):
            categoryName = args["categoryName"]
            return list(cat_pdt_generator(session.query(Products).join(Products.sub_category).join(SubCategory.category).filter(Category.name==categoryName).order_by(Products.product_id).all()))

#sub_cat pdts generator
def sub_cat_pdt_generator(data_list):
    _date = datetime.now(ni_timezone)
    current_time = _date.astimezone(timezone)
    for product in data_list:
        if product.resturant.approved:
            if product.approved and product.suspend != True:
                    _start_date = ni_timezone.localize(product.resturant.operation_start_time)
                    _end_date = ni_timezone.localize(product.resturant.operation_stop_time)
                    operation_start_time = _start_date.astimezone(timezone)
                    operation_stop_time = _end_date.astimezone(timezone)
                    if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                        pdt = product.serialize()
                        pdt["available"] = True
                        yield pdt
                    else:
                        yield product.serialize()


#sub_category_products
class SubCategoryProductsApI(Resource):
    def get(self, id):
        return list(sub_cat_pdt_generator(Products.read_products_based_on_sub_cat(id)))


        
