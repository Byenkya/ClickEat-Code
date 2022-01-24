from flask_wtf import FlaskForm
from wtforms import *
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Email, EqualTo
from wtforms.widgets import HiddenInput, Select, TextArea
from Application.database.models import Customer, CustomerAddress
from Application.database.initialize_database import session
from Application.utils import join_telephone
# from Application.API.resources.Places.places import arua_district_places
from Application.database.models import PlacePrices

arua_district_places = PlacePrices.read_place_prices()

def unique_update_email(form, field):
    if Customer.query.filter(Customer.id!=form.id.data).filter_by(email=field.data).first():
        raise ValidationError(f"A user with email '{field.data}' already exists.")


def unique_update_telephone(form, field):
    if Customer.query.filter(Customer.id!=form.id.data).filter_by(contact=field.data).first():
        raise ValidationError(f"A user with telephone '{field.data}' already exists.")


class UpdateCustomerForm(FlaskForm):
    id = IntegerField(widget=HiddenInput(), validators=[DataRequired()])
    name = StringField("Your Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), unique_update_email])
    telephone = StringField("Telephone", validators=[DataRequired(), unique_update_telephone])
    
    def __init__(self, customer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if customer:
            self.customer = customer
            self.id.data = customer.id
            self.name.data = customer.name
            self.email.data = customer.email
            self.telephone.data = customer.contact


class UpdatePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[InputRequired("Enter password")])
    new_password = PasswordField("New Password", validators=[InputRequired("Enter password")])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired("Enter password"), EqualTo("new_password")])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ChangeCustomerAddressForm(FlaskForm):
    address = IntegerField("Select address", validators=[InputRequired()])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_address(form, field):
        address = session.query(CustomerAddress).filter_by(id=field.data).first()
        if address:
            form.address.data = address
        else:
            raise ValidationError("Invalid address")


class CreateCustomerAddressForm(FlaskForm):
    village = SelectField("Village", validators=[InputRequired()])
    description = TextField("Describe your exact location", widget=TextArea())
    is_default = BooleanField("Set as default address")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.village.choices = [(place["village"], place["village"]) for place in arua_district_places]

    def validate_village(form, field):
        matches = list(filter(lambda each: each["village"]==field.data, arua_district_places))
        if matches:
            form.village.data = matches[0]
        else:
            raise ValidationError(f"Invalid village")