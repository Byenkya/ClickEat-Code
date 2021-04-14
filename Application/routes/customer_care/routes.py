from Application.flask_imports import (
    Blueprint, login_user, _session, url_for,redirect,render_template,flash,
    login_required, logout_user, request, current_user, jsonify
    )

from Application.database.models import (StaffAccounts, Customer,
Resturant, Products, Order, DeliveryMethods, Cart, Courier, DeliveryDetails,
Courier, Sales)

from .forms import LoginForm, ReasonForm, OrderReturnsForm, AccountSettingsForm, ChangePasswordForm
from Application.utils import employee_login_required, Paginate, DateUtil
from Application.database.sqlalchemy_imports import and_
from Application.database.initialize_database import session

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
	customer_count = Customer.read_customer_count()
	vendors_count = Resturant.read_restaurants_count()
	products_count = Products.read_products_count()
	orders_count = Order.read_orders_count()
	total_revenue = Sales.read_sales_sum(Sales.amount)

	context = dict(
		product_sales_today=product_sales_today,
		commission_sales_today=0,
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
	next_url = url_for(".customer_care", page=pagination.next_page) if pagination.has_next else None
	prev_url = url_for(".customer_care", page=pagination.previous_page) if pagination.has_previous else None
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
	return render_template('courier_detail.html', courier=courier,orders=orders)


@customer_care.route('/custcare-shops/<string:shop_state>',methods=["GET"])
@login_required
@employee_login_required
def custcare_shops(shop_state):
	if shop_state == "all":
		restuarants = Resturant.read_restaurants()

	return render_template('restaurants/customer_care_restaurants.html',restuarants=restuarants, shop_state=shop_state)


@customer_care.route('/custcare-shop-detail/<int:shop_id>',methods=["GET"])
@login_required
@employee_login_required
def shop_detail(shop_id):
	restuarant  = Resturant.read_restaurant(id=shop_id)
	return render_template('restaurants/restaurant/restuarant_details.html',restuarant=restuarant)

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