from flask_restful import Resource, fields, marshal_with, reqparse
from Application.flask_imports import request, jsonify
from Application.database.models import Products, Cart, Customer, SubCategory, Brand, HomeImages, TopSellingProducts, Category
from Application.database.initialize_database import session
from random import sample

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
        customer = Customer.read_customer(id=customer_id)

        if customer:
            cart_item = Cart()(
                product_id=product_id,
                customer_id=customer_id,
                product_name=product_name,
                product_image=product_image,
                unit_price=unit_price,
                quantity=quantity
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
        fruits_vegetables = sample([product.serialize() for product in session.query(Products).join(Products.sub_category).join(SubCategory.category).filter(Category.name=="Fruits and Vegetables").order_by(Products.product_id).all()], 2)
        home_products = Products.home_products()
        home_products.append({"id": 3, "title":"Fruits & Vegetables", "products": fruits_vegetables})
        home_sub_cats_list = []
        sub_cats = SubCategory.read_sub_cat()

        for sub in sub_cats:
            product_image = Products.read_product_by_sub_cat(sub["sub_category_id"])
            if product_image:
                home_sub_cats = {}
                home_sub_cats['id'] = sub["sub_category_id"]
                home_sub_cats['subCatImage'] = product_image.product_picture 
                home_sub_cats['name'] = sub["name"]
                home_sub_cats_list.append(home_sub_cats)
            
        return {"home_images_products": home_products,"home_images": HomeImages.home_images(), "sub_cats": home_sub_cats_list}

#read subcategories
class FetchAllSubCategoriesApi(Resource):
    def get(self):
        home_sub_cats_list = []
        sub_cats = SubCategory.read_sub_cat()
        for sub in sub_cats:
            product_image = Products.read_product_by_sub_cat(sub["sub_category_id"])
            if product_image:
                home_sub_cats = {}
                home_sub_cats['id'] = sub["sub_category_id"]
                home_sub_cats['subCatImage'] = product_image.product_picture 
                home_sub_cats['name'] = sub["name"]
                home_sub_cats_list.append(home_sub_cats)

        return home_sub_cats_list


#searched Products
searchStringsArgs = reqparse.RequestParser()
searchStringsArgs.add_argument("searchString", type=str)
class SearchedProductsResource(Resource):
    def get(self):
        args = searchStringsArgs.parse_args()
        products = []
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
        return [product.serialize() for product in products]

#products based on category
categoryProductsStringsArgs = reqparse.RequestParser()
categoryProductsStringsArgs.add_argument("categoryName", type=str)
class CategoryProductsApI(Resource):
    def get(self):
        args = categoryProductsStringsArgs.parse_args()
        if args.get("categoryName", None):
            categoryName = args["categoryName"]
            products = [product.serialize() for product in session.query(Products).join(Products.sub_category).join(SubCategory.category).filter(Category.name==categoryName).order_by(Products.product_id).all()]
            return products

#sub_category_products
class SubCategoryProductsApI(Resource):
    def get(self, id):
        products = Products.read_products_based_on_sub_cat(id)
    
        return [product.serialize() for product in products]

#other products
class AllProductsAPI(Resource):
    def get(self):
        products = Products.read_products()

        return [product.serialize() for product in products]

#top selling products
class TopSellingProductsAPI(Resource):
    def get(self):
        all_products = [product.serialize() for product in Products.read_products() if product.approved and product.suspend != True]
        products = TopSellingProducts.read_all_top_discount_products()

        return {"all_products": all_products, "top_selling": products}

        
