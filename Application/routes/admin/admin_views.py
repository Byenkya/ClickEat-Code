from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.menu import MenuLink

from Application.database import models as db
from Application.database.initialize_database import session
from Application.database.sqlalchemy_imports import func
from .forms import LoginForm
from Application.flask_imports import (
    _session, current_user, flash, login_user, logout_user, redirect
)


class LoginView(BaseView):
    @expose("/", methods=["GET", "POST"])
    def loginView(self):
        form = LoginForm()
        if current_user.is_authenticated and getattr(current_user, "account", None) == "administrator":
            return redirect(self.get_url("admin.index"))

        if form.validate_on_submit():
            user = db.StaffAccounts.read_user(username=form.username.data)
            if user and user.verify_password(form.password.data):
                login_user(user)
                _session["account_type"] = "administrator"
                return redirect(self.get_url("admin.index"))
            else:
                flash("Username or Password is incorrect", "danger")
                return redirect(self.get_url(".loginView"))

        return self.render("admin/login.html", form=form)
    
    def is_visible(self):
        return False

class LogoutView(BaseView):
    @expose("/", methods=["GET"])
    def logout(self):
        logout_user()
        _session.pop("account_type")

        return redirect(self.get_url("loginview.loginView"))
    
    def is_accessible(self):
        return current_user.is_authenticated and str(getattr(current_user, "account_type", None)) == "administrator"

    def is_visible(self):
        return True


class AdminHomeView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and str(getattr(current_user, "account_type", None)) == "administrator"

    @expose("/")
    def index(self):
        customer_number = session.query(func.count(db.Customer.id)).scalar()
        resturant_number = session.query(func.count(db.Resturant.id)).scalar()
        sales_amount = session.query(func.count(db.Sales.amount)).scalar()
        products_sold = session.query(func.sum(db.Sales.quantity)).scalar()

        if customer_number is None:
            customer_number = 0

        if resturant_number is None:
            resturant_number = 0

        if sales_amount is None:
            sales_amount = 0

        if products_sold is None:
            products_sold = 0

        return self.render(
            "admin/index.html",
            customer_number=customer_number,
            resturant_number=resturant_number,
            sales_amount=sales_amount,
            products_sold=products_sold
        )
        















































