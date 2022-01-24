from flask_wtf import FlaskForm
from wtforms import *
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Email, EqualTo
from wtforms.widgets import HiddenInput, Select
from Application.database.models import Customer, CustomerAddress
from Application.database.initialize_database import session
from Application.utils import join_telephone
from Application.database.models import PlacePrices

arua_district_places = PlacePrices.read_place_prices()



payment_methods = [
	(1, "Cash on delivery"),
	(2, "Mobile Money"),
]

class SelectPaymentForm(FlaskForm):
    payment = RadioField("Payment method", validators=[DataRequired()], coerce=int, choices=payment_methods)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_payment(form, field):
    	data = dict(payment_methods).get(field.data)
    	if data:
    		form.payment.data = data
    	else:
    		raise ValidationError(f"Invalid payment method.")