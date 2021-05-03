from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), DataRequired(),Email()])
    submit = SubmitField("Submit")

class NewPasswordForm(FlaskForm):
    new_password = PasswordField("Enter New Password",render_kw=dict(autocomplete="off"), validators=[InputRequired(), DataRequired()])
    confirm_password = PasswordField("Confirm Password",render_kw=dict(autocomplete="off"),validators=[EqualTo(fieldname="new_password", message="passwords are not equal")])
    save = SubmitField("Save Password")
