from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField,
HiddenField, RadioField, BooleanField, SelectField, IntegerField)
from wtforms.validators import InputRequired, DataRequired, Length, NumberRange, ValidationError, EqualTo
from Application.helpers.generators import generate_tuple_list
from Application.flask_imports import current_user

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("Enter username"), DataRequired()])
    password = PasswordField("Password", validators=[InputRequired("Enter password"), DataRequired()])
    submit = SubmitField("Login")

class ReasonForm(FlaskForm):
    reason = TextAreaField("Reason", validators=[InputRequired(), DataRequired(), Length(max=500, message="Please do not exceed 500 characters.")])
    submit_request = SubmitField("Submit")

compensation_options = [
    "refund", "swap"
]
compensation_options = generate_tuple_list(*compensation_options)

class OrderReturnsForm(FlaskForm):
    order_ref = HiddenField(validators=[DataRequired(), InputRequired()])
    order_products = RadioField("Products",coerce=int, validators=[DataRequired(), InputRequired("Select products returned")])
    has_warranty = BooleanField("Product has a warranty")
    compensation_options = SelectField("Compensation method", coerce=str,choices=compensation_options, validators=[DataRequired(), InputRequired()])
    unit_price = IntegerField("Unit Price", render_kw=dict(readonly="readonly"), validators=[NumberRange(min=0)])
    quantity =IntegerField("Quantity", validators=[NumberRange(min=0)])
    total_amount = IntegerField("Total", render_kw=dict(readonly="readonly"), validators=[NumberRange(min=0)])
    return_reason = TextAreaField("Return reason",render_kw=dict(rows=3), validators=[DataRequired(), InputRequired()])
    submit_return = SubmitField("Submit")

    def validate_total_amount(self, total_amount):
        if total_amount.data != (self.unit_price.data*self.quantity.data):
            raise ValidationError("Total should equal to unit price x quantity")

class AccountSettingsForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired(), DataRequired()])
    email = StringField("Email", validators=[InputRequired(), DataRequired()])
    contact = StringField("Contact", validators=[InputRequired(), DataRequired()])
    address = TextAreaField("Address", validators=[InputRequired(), DataRequired()])
    submit_changes = SubmitField("Update")

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Enter Current Password", validators=[InputRequired(), DataRequired()])
    new_password = PasswordField("Enter New Password", validators=[InputRequired(), DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[EqualTo("new_password")])
    submit_password = SubmitField("Update")

    def validate_current_password(self, current_password):
        if not current_user.verify_password(current_password.data):
            raise ValidationError("current password is incorrect")