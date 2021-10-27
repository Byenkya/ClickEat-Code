from flask import Blueprint, render_template, redirect, flash, url_for, request
from Application.forms import SignupForm, LoginForm, ChangeCustomerAddressForm, CreateCustomerAddressForm, SelectPaymentForm
from Application.utils import join_telephone
from Application.database.models import Customer
from Application.database.initialize_database import session
from flask_login import login_user, logout_user, login_required, current_user


checkout_bp = Blueprint('checkout_bp', __name__, url_prefix='/checkout', template_folder='../templates')


@checkout_bp.route('/', methods=["POST", "GET"])
@login_required
def checkout():
	change_customer_address_form = ChangeCustomerAddressForm()
	create_customer_address_form = CreateCustomerAddressForm()
	select_payment_form = SelectPaymentForm()
	if change_customer_address_form.validate_on_submit():
		data = change_customer_address_form.data
		address = data["address"]
		return redirect(url_for('checkout.checkout_payment'))
	return render_template("checkout/checkout.html", change_customer_address_form=change_customer_address_form, create_customer_address_form=create_customer_address_form, select_payment_form=select_payment_form)