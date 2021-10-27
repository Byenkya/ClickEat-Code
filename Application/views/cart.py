from flask import Blueprint, render_template, redirect, flash, url_for, request
from Application.forms import SignupForm, LoginForm
from Application.utils import join_telephone
from Application.database.models import Customer
from Application.database.initialize_database import session
from flask_login import login_user, logout_user, login_required, current_user


cart_bp = Blueprint('cart_bp', __name__, url_prefix='/cart', template_folder='../templates')


@cart_bp.route('/')
@login_required
def get_cart():
	print(">>>>>>>>>>>", current_user.is_authenticated)
	return render_template("cart/cart.html")