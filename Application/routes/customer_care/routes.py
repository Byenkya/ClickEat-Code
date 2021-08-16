from Application.flask_imports import (
    Blueprint, login_user, _session, url_for,redirect,render_template,flash,
    login_required, logout_user, request, current_user, jsonify
    )

from Application.database.models import (StaffAccounts, Customer,
Resturant, Products, Order, DeliveryMethods, Cart, Courier, DeliveryDetails,
Courier, Sales, SubCategory, Category, Comments, Rate, ProductDiscounts, Brand, TopSellingProducts)

from .forms import LoginForm, ReasonForm, OrderReturnsForm, AccountSettingsForm, ChangePasswordForm, ProductsVerificationForm, SetPromotionForm, SuspendProductForm, AddProductForm
from Application.utils import employee_login_required, Paginate, DateUtil
from Application.database.sqlalchemy_imports import and_
from Application.database.initialize_database import session
from datetime import datetime
import pytz

customer_care = Blueprint(
    'customer_care',__name__,template_folder="templates/",
    url_prefix="/customer_care"
)

@customer_care.before_request
def init_cusomter_care_page():
	orders_not_prepared = Order().read_orders_not_prepared_count()
	_session["orders_not_prepared"] = orders_not_prepared

@customer_care.route("/login", methods=["GET", "POST"])
def customer_care_login():
    form = LoginForm()

    if form.validate_on_submit():
        user = StaffAccounts.read_user(username=form.username.data)

        if not user:
            user = StaffAccounts.read_user(email=form.username.data)

        if user and user.verify_password(form.password.data):
            login_user(user)
            _session["account_type"] = "Employee"
            return redirect(url_for(".dashboard"))  
        else:
            flash("User name or Password is incorrect", "danger")
            return redirect(url_for(".customer_care_login"))

    return render_template("customer_care_login.html", form=form)

@customer_care.route("/logout")
@login_required
@employee_login_required
def logout():
    logout_user()
    _session.pop("account_type")

    return redirect(url_for(".customer_care_login"))

@customer_care.route("/orders_not_prepared", methods=["GET"])
@login_required
@employee_login_required
def orders_not_prepared():
	orders_not_prepared = Order.read_orders_not_prepared_count()
	return jsonify(orders_not_prepared=orders_not_prepared)

@customer_care.route("/")
@customer_care.route("/dashboard", methods=["GET"])
@login_required
@employee_login_required
def dashboard():
	product_sales_today = Sales.read_sales_sum(
		Sales.amount, 
		Sales.sales_day==DateUtil().current_date.day,
		Sales.sales_month==DateUtil().current_date.month,
		Sales.sales_year==DateUtil().current_date.year,
		)

	commission_sales_today = Sales.read_sales_sum(
		Sales.commision_amount,
		Sales.sales_day == DateUtil().current_date.day,
		Sales.sales_month == DateUtil().current_date.month,
		Sales.sales_year == DateUtil().current_date.year,
	)
	customer_count = Customer.read_customer_count()
	vendors_count = Resturant.read_restaurants_count()
	products_count = Products.read_products_count()
	orders_count = Order.read_orders_count()
	total_revenue = Sales.read_sales_sum(Sales.amount)

	context = dict(
		product_sales_today=product_sales_today,
		commission_sales_today=commission_sales_today,
		total_revenue=total_revenue,
		shipping_sales_today=0,
		standard_shipping_sales_td=0,
		pickup_station_sales_td=0,
		vendors_count=vendors_count,
		customer_count=customer_count,
		products_count=products_count,
		orders_count=orders_count
	)

	return render_template('dashboard.html',**context)

@customer_care.route('/orders' ,methods=["GET"])
@login_required
@employee_login_required
def customer_care_orders():
	page = int(request.args.get("page", 1))
	orders = Order.read_all_orders()
	pagination = Paginate(orders, page,8)
	next_url = url_for(".customer_care_orders", page=pagination.next_page) if pagination.has_next else None
	prev_url = url_for(".customer_care_orders", page=pagination.previous_page) if pagination.has_previous else None
	return render_template(
		'orders/orders.html', 
		orders=orders,
		next_url = next_url,
		prev_url = prev_url,
		pagination=pagination,
		current_page = page
		)

@customer_care.route('/all-orders',methods=["GET"])
@login_required
@employee_login_required
def all_orders():
	state = request.args.get("state","need_preparing_orders")

	if state == "need_preparing_orders":
		page= "Need Preparing Orders"
		orders=Order.read_all_orders_filter(
			and_(
				Order.is_prepared == False,
				Order.is_terminated == False
			)
		)
	elif state == "pre_orders":
		page= "Pre Orders"
		orders=Order.read_all_orders_filter(
			and_(
				Order.is_prepared == False,
				Order.is_terminated == False,
				Order.pre_order == True
			)
		)
	elif state == "prepared_orders":
		page = "Prepared Orders"
		orders =Order.read_all_orders_filter(
			Order.is_prepared == True
		)

	elif state == "received_orders":
		page = "Recieved Orders"
		orders =Order.read_all_orders_filter(
			Order.customer_received == True
		)

	elif state == "need_transporting":
		page = "Need Transporting"
		orders = Order.read_all_orders_filter(
			Order.customer_received == False,
			Order.is_prepared == True,
			Order.is_terminated == False
		)


			
	return render_template(
		'orders/all_orders_base_1.html',
		orders=orders,
		page = page,
		state = state
		)

@customer_care.route('/cancelled-orders',methods=["GET"])
@login_required
@employee_login_required
def cancelled_orders():
	orders_terminated= Order.read_all_orders_filter(
		Order.is_terminated == True
	)
	return render_template('orders/cancelled_orders.html',orders_terminated=orders_terminated)

@customer_care.route('/customer-care-order-detail/<order_id>',methods=["GET", "POST"])
@login_required
@employee_login_required
def customer_care_order_detail(order_id):
	form = ReasonForm()
	order = Order.read_order(id=int(order_id))
	cart_items_sum = Cart.customer_order_items_total(order.id)
	courier_districts = Courier.read_courier_districts()
	order_return_form = OrderReturnsForm()
	order_return_form.order_ref.data = order.id

	order_products = []
	order_return_form.order_products.choices = order_products
	timezone = pytz.timezone("Africa/Kampala")
	_date = timezone.localize(order.pre_order_time)
	order_date = _date.astimezone(timezone).strftime("%a %b %d %H:%M:%S %Z %Y")
	for item in order.cart:
		order_products.append(
			(
				item.product_id, 
				f"{item.product_name},{item.quantity} @{item.unit_price}"
			)
		)

	if request.method == "POST":  
		Order.customer_care_register_order_sales( 
			data = request.json,
			order = order
		)
		return jsonify()

	return render_template(
		'orders/order/order_detail.html',
		order_date=order_date,
		order=order,
		cart_items_sum=cart_items_sum,
		districts=courier_districts,
		form=form,
		order_return_form=order_return_form
		)

@customer_care.route('/couriers',methods=["GET"])
@login_required
@employee_login_required 
def couriers():
	couriers = Courier.read_couriers()
	return render_template('courier.html', couriers=couriers)

@customer_care.route('/courier_detail/<int:courier_id>',methods=["GET"])
@login_required
@employee_login_required
def courier_details(courier_id):
	courier = Courier.read_courier(id=courier_id) 
	orders = Order.read_all_orders_delivery_details_filter(
		DeliveryDetails.courier_id == courier_id
	)
	return render_template('courier_detail.html', courier=courier,orders=orders, order_count=len(orders))


@customer_care.route('/custcare-shops/<string:shop_state>',methods=["GET"])
@login_required
@employee_login_required
def custcare_shops(shop_state):
	if shop_state == "all":
		restuarants = Resturant.read_all_rests()

	return render_template('restaurants/customer_care_restaurants.html',restuarants=restuarants, shop_state=shop_state)


@customer_care.route('/custcare-shop-detail/<int:shop_id>/<string:state>',methods=["GET"])
@login_required
@employee_login_required
def shop_detail(shop_id, state):
	restuarant  = Resturant.read_restaurant(id=shop_id)
	if state == "all_products":
		products = restuarant.read_all_rest_products

	elif state == "approved":
		products = restuarant.read_all_approved_products

	elif state == "not_approved":
		products = restuarant.read_all_non_approved_products

	elif state == "suspended":
		products = restuarant.read_all_suspended_products

	return render_template(
		'restaurants/restaurant/restuarant_details.html',
		restuarant=restuarant, 
		shop_id=shop_id, 
		products=products,
		state=state
		)

@customer_care.route("/account_settings", methods=["GET", "POST"])
@login_required
@employee_login_required
def account_settings():
	account_settings_form = AccountSettingsForm()
	password_change_form = ChangePasswordForm()
	user = StaffAccounts.read_user(id=current_user.id)
	current_tab = request.args.get("tab", "personal")
	if request.method == "GET":
		account_settings_form = AccountSettingsForm(obj=current_user)

	if account_settings_form.validate_on_submit():
		user.update_employee_details(
			email = account_settings_form.email.data.strip(),
			name = account_settings_form.name.data.strip(),
			contact = account_settings_form.contact.data.strip(),
			address = account_settings_form.address.data.strip()
		)
		flash("Updated your details successfully", "success")
		return redirect(url_for(".account_settings"))

	elif password_change_form.validate_on_submit():
		if user.verify_password(password_change_form.current_password.data):
			user.hash_password(password_change_form.new_password.data)
			session.commit()
			flash("Password changed successfully, please try to log in with new password","success")
			return redirect(url_for(".account_settings", current_tab="password"))
		else:
			flash("Current password is incorrect","danger")
			return redirect(url_for(".account_settings", current_tab="password"))

	context = dict(
		account_settings_form=account_settings_form,
		password_change_form=password_change_form,
		current_tab=current_tab
	)
	return render_template("customer_care_account_settings.html",**context)

@customer_care.route('/district_couriers/<string:district>', methods=["GET"])
@login_required
@employee_login_required
def get_district_couriers(district):
	couriers = Courier.read_district_couriers(district)
	couriers = [i.serialize() for i in couriers]

	

	return jsonify(couriers=couriers)

@customer_care.route("/terminate_order/<int:order_id>", methods=["POST"])
@login_required
@employee_login_required
def terminate_order(order_id):
	form = ReasonForm()
	order = Order.read_order(id=order_id)
	if order.is_terminated  and order.termination_reason:
		flash("Order already terminated", "danger")
		return redirect(url_for(".customer_care_order_detail",order_id=order_id))
		
	if order.is_paid:
		flash("Cannot terminate already paid order, items have to be returned and customer compensated", "danger")
		return redirect(url_for(".customer_care_order_detail",order_id=order_id))

	if form.validate_on_submit() and order:
		if order.customer_care_terminate_order(form.reason.data):
			flash("Order terminated successfully", "success")
		else:
			flash("Failed to terminate order", "danger")
	else:
		flash("Failed to terminate order", "danger")

	return redirect(url_for(".customer_care_order_detail",order_id=order_id))

@customer_care.route('/customer-care-add-product', methods=["GET", "POST"])
@login_required
@employee_login_required
def add_product():
	form = AddProductForm()
	brands = Brand.read_all_bandss_filter_by("brand_id","name")
	if request.method == "GET":
		form.restaurant.choices = Resturant.read_all_restaurants_filter_by("id","business_name")
		form.brand.choices = brands
		form.sub_cat.choices = SubCategory.read_all_subcategories_filter_by("sub_category_id","name")
		form.price.data = 0
		form.buying_price.data = 0
		form.selling_price.data = 0
		form.served_with.data = "none"
		form.commission_fee.data = 0.0
		form.headsup.data = "clickEat"

	if form.validate_on_submit():
		try:
			product_picture = save_picture(form.product_picture.data,None, "static/product_images", 500,500)
			price = form.price.data
			rest_id = form.restaurant.data
			brand_name = [brand for brand in brands if brand[0] == form.brand.data][0][1]
			if(Products()(
				name=form.name.data,
				product_picture=product_picture,
				description=form.description.data,
				price=form.price.data,
				resturant_id=form.restaurant.data,
				brand=brand_name,
				sub_category_id=form.sub_cat.data,
				buying_price=form.buying_price.data,
				selling_price=form.selling_price.data,
				served_with=form.served_with.data,
				commission_fee=form.commission_fee.data,
				headsup=form.headsup.data
			)):
				flash("Product added successfully","success")
				return redirect(url_for("customer_care.add_product"))
				
		except Exception as e:
			print("Error while trying to save product: ", e)
			session.rollback()
			flash("Error while trying to save product","danger")

	
	return render_template('restaurants/restaurant/product/add_product.html',form=form)

@customer_care.route('/custcare-shop-product/<int:product_id>',methods=["GET","POST"])
@login_required
@employee_login_required
def rest_product_detail(product_id):
	product = Products.read_product(product_id)
	top_selling_status = TopSellingProducts.read_top_most_selling_product(product_id)
	comments = Comments.product_comments(product_id)
	product_rating = Rate.read_product_rate(product_id)
	restuarant  = Resturant.read_restaurant(id=product.resturant_id)
	form = ProductsVerificationForm()
	promotional_price_form = SetPromotionForm()
	suspend_form = SuspendProductForm()
	suspend_form.product_id.data = product_id

	if request.method == "GET":
		form = ProductsVerificationForm(obj=product)
		form.sub_category.choices = SubCategory.read_all_subcategories_filter_by(
			"sub_category_id","name",
			category_id= product.sub_category.category_id)

	# form.category.choices = Category.read_all_categories_by_attr("category_id","name")

	if form.validate_on_submit():
		if form.product_picture.data:
			try:
				product_pic = save_picture(form.product_picture.data,product.product_picture, "static/product_images", 500,500)
				# product.sub_category_id = form.sub_category.data
				product.name = form.name.data
				product.product_picture = product_pic
				product.price = form.price.data
				product.description = form.description.data
				product.product = form.price.data
				product.buying_price = form.buying_price.data
				product.selling_price = form.selling_price.data
				product.served_with = form.served_with.data
				product.commission_fee = form.commission_fee.data
				product.headsup = form.headsup.data
				product.free_delivery = form.free_delivery.data
				session.commit()
				flash("Product updated successfully","success")
				return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
			except Exception as e:
				print("Customer care updating product error:",e)
				session.rollback()
				flash("Internal server error failed to update product.", "danger")
		else:
			try:
				# product.sub_category_id = form.sub_category.data
				product.name = form.name.data
				product.price = form.price.data
				product.description = form.description.data
				product.product = form.price.data
				product.buying_price = form.buying_price.data
				product.selling_price = form.selling_price.data
				product.served_with = form.served_with.data
				product.commission_fee = form.commission_fee.data
				product.headsup = form.headsup.data
				product.free_delivery = form.free_delivery.data
				session.commit()
				flash("Product updated successfully","success")
			except Exception as e:
				print("Customer care updating product error:",e)
				session.rollback()
				flash("Internal server error failed to update product.", "danger")
		return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
	

	return render_template(
		'restaurants/restaurant/product/product_details.html',
		shop=restuarant,
		product=product,
		product_rating=product_rating,
		comments=comments,
		form=form,
		promo_form=promotional_price_form,
		suspend_form=suspend_form,
		top_selling_status=top_selling_status
		)

@customer_care.route('/custcare-set-promotion/<int:product_id>',methods=["GET","POST"])
@login_required
@employee_login_required
def set_promotional_price(product_id):
	promotional_price_form = SetPromotionForm()
	if promotional_price_form.validate_on_submit():
		try:
			product = Products.read_product(product_id)
			product.promotional_price_set = True
			ProductDiscounts()(
				product_id=product_id,
				price=promotional_price_form.price.data,
				from_date=promotional_price_form.from_date.data,
				to_date=promotional_price_form.to_date.data,
				is_scheduled=True
			)
			flash("Product promotional price set successfully","success")
			return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
		except Exception as e:
			session.rollback()
			print("Error while retriving data: ", e)
			flash("Internal server error failed to update product.", "danger")


	return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))

@customer_care.route('/custcare-remove-promotional-price/<int:product_id>',methods=["GET","POST"])
@login_required
@employee_login_required	
def remove_promotion_price(product_id):
	suspend_form = SuspendProductForm()
	if suspend_form.validate_on_submit():
		try:
			if ProductDiscounts.remove_promotion_price(product_id):
				flash("Product promotional price removed successfully","success")
				return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
			else:
				flash("Product promotional price was not removed successfully","danger")
				return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
		except Exception as e:
			session.rollback()
			print("Error while retriving data: ", e)
			flash("Internal server error failed to update product.", "danger")

	return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))

@customer_care.route('/custcare-suspend-product/<int:product_id>',methods=["GET","POST"])
@login_required
@employee_login_required
def suspend_product(product_id):
	suspend_form = SuspendProductForm()
	if suspend_form.validate_on_submit():
		try:
			product = Products.read_product(product_id)
			product.suspend = True
			session.commit()
			flash("Product suspended successfully","success")
			return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
		except Exception as e:
			session.rollback()
			print("Error while retriving data: ", e)
			flash("Internal server error failed to update product.", "danger")

	return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))


@customer_care.route('/custcare-remove-product-suspension/<int:product_id>',methods=["GET","POST"])
@login_required
@employee_login_required	
def remove_product_suspension(product_id):
	suspend_form = SuspendProductForm()
	if suspend_form.validate_on_submit():
		try:
			product = Products.read_product(product_id)
			product.suspend = False
			session.commit()
			flash("Product suspension removed successfully","success")
			return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
		except Exception as e:
			session.rollback()
			print("Error while retriving data: ", e)
			flash("Internal server error failed to update product.", "danger")

	return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))

@customer_care.route('/custcare-approve-product/<int:product_id>',methods=["GET","POST"])
@login_required
@employee_login_required	
def approve_product(product_id):
	suspend_form = SuspendProductForm()
	if suspend_form.validate_on_submit():
		try:
			product = Products.read_product(product_id)
			product.approved = True
			session.commit()
			flash("Product approved successfully","success")
			return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
		except Exception as e:
			session.rollback()
			print("Error while retriving data: ", e)
			flash("Internal server error failed to update product.", "danger") 

	return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))

@customer_care.route('/customer_care-add-to-top-selling-products/<int:product_id>', methods=["GET","POST"])
@login_required
@employee_login_required
def addToTopSelling(product_id):
	suspend_form = SuspendProductForm()
	if suspend_form.validate_on_submit():
		try:
			if TopSellingProducts()(product_id=product_id):
				flash("Product added to top most selling products successfully!!", "success")
				return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
			else:
				flash("Product already added to Top most selling", "danger")
				return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
		except Exception as e:
			session.rollback()
			print("Error while retriving data: ", e)
			flash("Internal server error failed to update product.", "danger") 

@customer_care.route('/customer_care-delete-from-top-selling-products/<int:product_id>', methods=["GET","POST"])
@login_required
@employee_login_required
def deleteFromTopSelling(product_id):
	suspend_form = SuspendProductForm()
	if suspend_form.validate_on_submit():
		try:
			if(TopSellingProducts.delete_pdt_from_top_selling(product_id)):
				flash("Product was removed successfully!!", "success")
				return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
			else:
				flash("Error while trying to delete product from top selling", "danger")
				return redirect(url_for("customer_care.rest_product_detail",product_id=product_id))
		except Exception as e:
			session.rollback()
			print("Error while retriving data: ", e)
			flash("Internal server error failed to update product.", "danger") 



import PIL
from random import randint
from werkzeug.utils import secure_filename
import os
from Application import app
from Application.helpers.generators import ReferenceGenerator
def save_picture(picture,previous_pic,directory,x,y):
	try:
		if previous_pic:
			try:
				file_path = os.path.join(os.path.join(app.root_path,directory), previous_pic)
				if os.path.isfile(file_path):
					os.remove(file_path)
					print("successfully deleted product image!!!!!!!!!!!!!!")
			except Exception as e:
				print("Error while deleting previous product picture: ", e)

		f_name, f_ext = os.path.splitext(picture.filename)
		f_name = f_name.replace(" ","")
		if len(f_name) > 10:
			f_name = f_name[:10]
		picture_fn = secure_filename("".join([f_name,ReferenceGenerator().unique_filename(),".jpg"]))
		picture_path = os.path.join(app.root_path, directory , picture_fn)
		image = PIL.Image.open(picture)
		image = image.convert("RGB")
		image = image.resize((x, y), PIL.Image.ANTIALIAS)
		image.save(picture_path, "jpeg", quality=85)
		return picture_fn
	except Exception as e:
		raise Exception("Failed to save image: ",e)