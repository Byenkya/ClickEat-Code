from flask_wtf import FlaskForm
from wtforms import *
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, DataRequired, Email, EqualTo
from wtforms.widgets import HiddenInput, Select
from Application.database.models import Customer
from Application.utils import join_telephone


telephone_code_choices = [("256", "+256")]

# validators
def unique_create_email(form, field):
    if Customer.query.filter_by(email=field.data).first():
        raise ValidationError(f"A user with email '{field.data}' already exists.")

# validators
def unique_update_email(form, field):
    if Customer.query.filter(Customer.id!=form.id.data).filter_by(email=field.data).first():
        raise ValidationError(f"A user with email '{field.data}' already exists.")

def unique_create_telephone(form, field):
    telephone_code = form.data.get("telephone_code")
    if Customer.query.filter_by(contact=join_telephone(telephone_code, field.data)).first():
        raise ValidationError(f"A user with telephone '{field.data}' already exists.")

def unique_update_telephone(form, field):
    if Customer.query.filter(Customer.id!=form.id.data).filter_by(contact=field.data).first():
        raise ValidationError(f"A user with telephone '{field.data}' already exists.")

def validate_telephone(form, field):
    telephone_code = form.data.get("telephone_code")
    telephone = field.data
    if not (telephone_code and telephone):
        raise ValidationError(f"Invalid Telephone.")


class LoginForm(FlaskForm):
    username = StringField("Email", validators=[InputRequired("Enter email"), Email()])
    password = PasswordField("Password", validators=[InputRequired("Enter password")])
    next_ = StringField(widget=HiddenInput())
    submit = SubmitField("Login")

    def __init__(self, next_=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if next_:
            self.next_.data = next_ 


class SignupForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), unique_create_email])
    telephone_code = SelectField(choices=telephone_code_choices)
    telephone = IntegerField("Telephone", validators=[DataRequired(), validate_telephone, unique_create_telephone])
    password = PasswordField("Password", validators=[InputRequired("Enter password")])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired("Enter password"), EqualTo("password")])
    next_ = StringField(widget=HiddenInput())

    def __init__(self, next_=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if next_:
            self.next_.data = next_