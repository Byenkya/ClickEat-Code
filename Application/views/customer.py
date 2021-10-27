from flask import Blueprint, render_template, redirect, flash, url_for, request
from Application.forms import SignupForm, LoginForm, CreateCustomerAddressForm, UpdateCustomerForm, UpdatePasswordForm
from Application.utils import join_telephone, attach_query_params
from Application.database.models import Customer, CustomerAddress
from Application.database.initialize_database import session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import timedelta


customer_bp = Blueprint('customer_bp', __name__, url_prefix='/customer', template_folder='../templates')


@customer_bp.route('/')
@login_required
def get_customer():
	update_customer_form = UpdateCustomerForm(customer=current_user)
	update_password_form = UpdatePasswordForm(customer=current_user)
	return render_template("customer/customer.html", update_customer_form=update_customer_form, update_password_form=update_password_form, show_profile=True)

@customer_bp.route('/customer/update', methods=["POST", "GET"])
@login_required
def update_customer():
	update_customer_form = UpdateCustomerForm()
	if update_customer_form.validate_on_submit():
		data = update_customer_form.data
		name = data["name"]
		email = data["email"]
		telephone = data["telephone"]
		customer = current_user
		customer.name = name
		customer.email = email
		customer.contact = telephone
		session.commit()
		session.close()
		flash("Profile updated", "success")
		return redirect(url_for('customer_bp.get_customer'))

	update_password_form = UpdatePasswordForm(customer=current_user)
	return render_template("customer/customer.html", update_customer_form=update_customer_form, update_password_form=update_password_form, show_profile=True)


@customer_bp.route('/customer/password/update', methods=["POST", "GET"])
@login_required
def update_password():
	update_password_form = UpdatePasswordForm()
	if update_password_form.validate_on_submit():
		data = update_password_form.data
		current_password = data["current_password"]
		new_password = data["new_password"]
		customer = current_user
		customer.change_password(current_password, new_password)
		flash("Password updated", "success")
		return redirect(url_for('customer_bp.get_customer'))

	update_customer_form = UpdateCustomerForm(customer=current_user)
	return render_template("customer/customer.html", update_customer_form=update_customer_form, update_password_form=update_password_form, show_password=True)



@customer_bp.route('/address/change', methods=["POST"])
@login_required
def change_customer_address():
	if current_user.is_authenticated:
		create_customer_address_form = CreateCustomerAddressForm()
		if create_customer_address_form.validate_on_submit():
			data = create_customer_address_form.data
			village = data["village"]
			other_details = data["description"]
			is_default = data["is_default"]
			CustomerAddress()(
				county=village["county_name"], 
				sub_county=village["sub_county_name"], 
				village=village["village"], 
				other_details=other_details, 
				is_default=is_default, 
				customer_id=current_user.id
				)
		return redirect(request.referrer)
	else:
		url = url_for('index_bp.signin_signup')
		return redirect(attach_query_params(url, {"referrer":url_for('checkout.checkout')}))


@customer_bp.route('/address/create')
@login_required
def create_customer_address():
	return render_template("customer/customer.html")