from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("Enter Username")])
    password = PasswordField("Password", validators=[InputRequired("Enter password")])
    submit = SubmitField("Login")