from flask_login import LoginManager
from flask_wtf import CSRFProtect
from redis import Redis
from celery import Celery
from flask_mail import Mail

redis = Redis()
celery = Celery()
mail = Mail()

login_manager = LoginManager()
login_manager.session_protection = "strong"
csrf = CSRFProtect()