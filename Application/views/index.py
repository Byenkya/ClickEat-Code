from flask import Blueprint, render_template, redirect, flash, url_for, request
from Application.forms import SignupForm, LoginForm
from Application.utils import join_telephone
from Application.database.models import Customer
from Application.database.initialize_database import session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import timedelta


index_bp = Blueprint('index_bp', __name__, url_prefix='/', template_folder='../templates')


@index_bp.route('/')
def index():
	return render_template("index/index.html")


@index_bp.route('/signin-signup')
def signin_signup():
	next_ = request.args.get("next")
	signup_form = SignupForm(next_=next_)
	login_form = LoginForm(next_=next_)
	return render_template("signin_signup/signin-signup.html", show_login=True, signup_form=signup_form, login_form=login_form)


@index_bp.route('/customer/signup', methods=["POST"])
def signup():
	next_ = request.args.get("next")
	signup_form = SignupForm(next_=next_)
	if signup_form.validate_on_submit():
		data = signup_form.data
		name = data["name"]
		email = data["email"]
		telephone_code = data["telephone_code"]
		telephone = data["telephone"]
		password = data["password"]
		customer = Customer(name=name, email=email, contact=join_telephone(telephone_code, telephone), password=password)
		session.add(customer)
		session.commit()
		if customer:
			login_user(customer, duration=timedelta(1))
			flash("Your account has been created.", "success")
		else:
			flash("There was an error creating your account.", "danger")
		if data['next_']:
			return redirect(data['next_'])
		return redirect(url_for('index_bp.index'))
	login_form = LoginForm(next_=next_)
	return render_template("signin_signup/signin-signup.html", show_signup=True, signup_form=signup_form, login_form=login_form)



@index_bp.route('customer/login', methods=["POST"])
def login():
	next_ = request.args.get("next")
	login_form = LoginForm(next_=next_)
	login_form.validate_on_submit()
	if login_form.validate_on_submit():
		data = login_form.data
		username = data["username"]
		password = data["password"]
		customer = session.query(Customer).filter(Customer.email==username).first()
		if customer and customer.verify_password(password):
			login_user(customer, remember=True, duration=timedelta(1))
			session.close()
			print(">>>>>>>>>>>>>>>", data['next_'], current_user.is_authenticated)
			if data['next_']:
				return redirect(data['next_'])
			return redirect(url_for('index_bp.index'))
		else:
			flash("Incorrect Credentials", "danger")
	signup_form = SignupForm(next_=next_)
	return render_template("signin_signup/signin-signup.html", show_login=True, login_form=login_form, signup_form=signup_form)


@index_bp.route('customer/logout', methods=["GET"])
def logout():
	logout_user()
	return redirect(url_for('index_bp.index'))