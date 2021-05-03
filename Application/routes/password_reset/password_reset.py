from Application.database.models import Customer, Resturant, StaffAccounts
from Application.database.initialize_database import session
from Application.flask_imports import *
from Application.helpers.generators import TokenGenerator
from Application.utils.email import reset_email

from .forms import ForgotPasswordForm, NewPasswordForm

password_reset = Blueprint("password_reset",__name__,url_prefix="/password_reset",template_folder="templates/")

@password_reset.route("/forgot_password/<string:user_type>", methods=["GET", "POST"])
def forgot_password(user_type):
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        if user_type == "customer":
            user = Customer.read_customer(email=form.email.data.strip())
        else:
            flash("Failed to send password reset.", "danger")
            return redirect(url_for(".forgot_password", user_type=user_type))

        if user is not None:
            token_gen = TokenGenerator(user=user)
            token = token_gen.generate_password_reset_token()
            mail_ = reset_email
            mail_.context = dict(
                user_name=user.name,
                token=token
            )
            mail_.recipients = [user.email]
            mail_.send()

        flash("If you provided a right email, check your email inbox for password reset link.", "success")
        return redirect(url_for(".forgot_password", user_type=user_type))

    context = dict(form=form, user_type=user_type)
    return render_template("reset.html", **context)

@password_reset.route("/new_password/<string:token>", methods=["GET", "POST"])
def set_new_password(token):
    form = NewPasswordForm()
    if form.validate_on_submit():
        token_gen = TokenGenerator()
        token_gen.verify_password_token(token)
        user = token_gen.user
        if user != None:
            user.password = form.new_password.data
            session.commit()
            mail_  = general_email
            mail_.context = dict(
                user_name=user.name,
                text = "Your password has been reset successfully."
            )
            mail_.title= "Password Reset"
            mail_.recipients = [user.email]
            mail_.send()
            flash("Your new password has been reset. Please try to log in with the new password.", "success")
        else:
            flash("Please request a new password reset. Either this link is invalid or expired.", "danger")
    context = dict(form=form,token=token)
    return render_template("new_password.html",**context)