from flask import Blueprint, render_template, redirect, flash, url_for, request
from Application.forms import SignupForm, LoginForm
from Application.utils import join_telephone
from Application.database.models import Customer
from Application.database.initialize_database import session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import timedelta


order_bp = Blueprint('order_bp', __name__, url_prefix='/', template_folder='../templates')


@order_bp.route('/')
def get_orders():
	return render_template("order/orders.html")