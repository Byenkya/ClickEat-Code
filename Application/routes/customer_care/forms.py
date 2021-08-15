from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField,
HiddenField, RadioField, BooleanField, SelectField, FloatField)
from wtforms.fields.html5 import DateField, IntegerField, SearchField
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

class CustomSelectField(SelectField):
    def pre_validate(self, form):
        if self.validate_choice:
            if self.data != "" or self.data != None:
                return True
            else:
                raise ValueError(self.gettext("Not a valid choice"))

class ProductsVerificationForm(FlaskForm):
    # category = SelectField("Category", coerce=int, validators=[InputRequired("Category is needed"), DataRequired()])
    sub_category = CustomSelectField("Sub Category", coerce=int, validators=[InputRequired("Sub Category is needed"), DataRequired()])
    name = StringField("Name", validators=[InputRequired(), DataRequired()])
    product_picture = FileField('Product Picture', validators=[FileAllowed(['jpg', 'png'])])
    description = TextAreaField('Description',render_kw=dict(placeholder="talk about your product in a few words"), validators=[ InputRequired(),DataRequired(), Length(min=10, max=500, message="description should be between 10 to 500 characters.")])
    price = IntegerField('Price', render_kw=dict(min=0), validators=[ InputRequired(), NumberRange(min=0)])
    buying_price = IntegerField('Buying Price', render_kw=dict(min=0), validators=[ InputRequired(), NumberRange(min=0)])
    selling_price = IntegerField('Selling Price', render_kw=dict(min=0), validators=[ InputRequired(), NumberRange(min=0)])
    served_with =  TextAreaField('Served With',render_kw=dict(placeholder="additional items added to the main product"), validators=[ InputRequired(),DataRequired(), Length(min=1, max=500, message="description should be between 10 to 500 characters and separated with commas")])
    commission_fee = FloatField("Commission Fee", validators=[InputRequired("Commission fee needed"),NumberRange(min=0.0)])
    headsup =  StringField("Delivery Time", render_kw=dict(placeholder="e.g 30-40 MINS"),validators=[InputRequired(), DataRequired()])
    free_delivery = BooleanField("Free Delivery")
    submit = SubmitField("UPDATE")

class AddProductForm(FlaskForm):
    restaurant = CustomSelectField("Restaurant", coerce=int, validators=[InputRequired("Restaurant is needed"), DataRequired()])
    brand = CustomSelectField("Brand", coerce=int, validators=[InputRequired("Brand needed"), DataRequired()])
    sub_cat = CustomSelectField("Sub Category", coerce=int, validators=[InputRequired("Sub Category is needed"), DataRequired()])
    name = StringField("Name", validators=[InputRequired(), DataRequired()])
    description = TextAreaField('Description',render_kw=dict(placeholder="talk about your product in a few words"), validators=[ InputRequired(),DataRequired(), Length(min=10, max=500, message="description should be between 10 to 500 characters.")])
    price = IntegerField('Price', render_kw=dict(min=0), validators=[ InputRequired(), NumberRange(min=0)])
    buying_price = IntegerField('Buying Price', render_kw=dict(min=0), validators=[ InputRequired(), NumberRange(min=0)])
    selling_price = IntegerField('Selling Price', render_kw=dict(min=0), validators=[ InputRequired(), NumberRange(min=0)])
    served_with =  TextAreaField('Served With',render_kw=dict(placeholder="additional items added to the main product"), validators=[ InputRequired(),DataRequired(), Length(min=1, max=500, message="description should be between 10 to 500 characters and separated with commas")])
    commission_fee = FloatField("Commission Fee", validators=[InputRequired("Commission fee needed"),NumberRange(min=0.0)])
    headsup =  StringField("Delivery Time", render_kw=dict(placeholder="e.g 30-40 MINS"),validators=[InputRequired(), DataRequired()])
    product_picture = FileField('Product Picture', validators=[DataRequired(),FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField("SAVE PRODUCT")


class SetPromotionForm(FlaskForm):
    price = IntegerField("Promotional Price",  render_kw=dict(min=0), validators=[InputRequired(), NumberRange(min=0)])
    from_date = DateField("From", validators=[DataRequired(), InputRequired()])
    to_date = DateField("To", validators=[DataRequired(), InputRequired()])
    save_price = SubmitField("Save Changes")

class SuspendProductForm(FlaskForm):
    product_id = IntegerField("Product ID",  render_kw=dict(min=0), validators=[InputRequired(), NumberRange(min=0)])
    save = SubmitField("Save Changes")