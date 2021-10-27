from flask import Blueprint, render_template, redirect, flash, url_for, request
from Application.database.models import Products
from Application.database.initialize_database import session


product_bp = Blueprint('product_bp', __name__, url_prefix='/product', template_folder='../templates')


class Product:
	name = "Beef Burger - Town Grill"
	preprice = "UGX 22,000"
	price = "UGX 16,000"


@product_bp.route('')
def get_products():
	# code to get / search products
	products = session.query(Products).all()
	# render patches
	patches = {
		"form_templates": {
			"#productsPatch": render_template('product/products.html', products=products)
		}
	}
	return patches


@product_bp.route('<int:product_id>')
def get_product(product_id):
	# code to get product
	product = session.query(Products).get(product_id)
	return render_template('product/product.html', product=product)


@product_bp.route('<int:product_id>')
def add_product_to_cart(product_id):
	# code to order product
	product = session.query(Products).get(product_id)
	customer_id = None
	if current_user.is_authenticated:
		customer_id = current_user.id

	served_with = request.args.get("served_with")

	cart = Cart()(
                product_id=product.id,
                customer_id=customer_id,
                product_name=product.name,
                product_image=product.image,
                unit_price=product.unit_price,
                quantity=1,
                served_with=served_with,
                free_delivery=product.free_delivery,
                restaurant=product.restaurant.business_name
            )
	
	return render_template('product/product.html', product=product)


@product_bp.route('<int:product_id>')
def order_product(product_id):
	# code to order product
	product = session.query(Products).get(product_id)

	return render_template('product/product.html', product=product)
