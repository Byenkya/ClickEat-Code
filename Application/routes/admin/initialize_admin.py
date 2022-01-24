import warnings

from flask_admin import Admin
from Application.routes.admin import admin_model as admin_models
from Application.routes.admin import admin_views as ad_views
from Application.database import models as db
from Application import app
from Application.database.initialize_database import session

admin = Admin(template_mode="bootstrap3")

with warnings.catch_warnings():  
    warnings.filterwarnings("ignore", "Fields missing from ruleset", UserWarning)

    admin.add_view(ad_views.LoginView(name="login_view", url="/login"))

    admin.add_view(admin_models.CustomerView(db.Customer, session, category="Customers"))

    admin.add_view(admin_models.ResturantView(db.Resturant, session, category="Resturants"))

    admin.add_view(admin_models.OrderView(db.Order, session, category="Order"))
    admin.add_view(admin_models.DeliveryDetailsView(db.DeliveryDetails, session, category="Order"))

    admin.add_view(admin_models.ProductsView(db.Products, session, category="Products"))
    admin.add_view(admin_models.CategoryView(db.Category, session, category="Products"))
    admin.add_view(admin_models.SubCategoryView(db.SubCategory, session, category="Products"))
    admin.add_view(admin_models.BrandView(db.Brand, session, category="Products"))
    admin.add_view(admin_models.CartView(db.Cart, session, category="Products"))
    admin.add_view(admin_models.ProductDiscountsView(db.ProductDiscounts, session, category="Products"))
    admin.add_view(admin_models.TopSellingProductsView(db.TopSellingProducts, session, category="Products"))
    admin.add_view(admin_models.CommentsView(db.Comments, session, category="Products"))
    admin.add_view(admin_models.RateView(db.Rate, session, category="Products"))
    admin.add_view(admin_models.SalesView(db.Sales, session, category="Products"))
    admin.add_view(admin_models.TrackProductsView(db.TrackProducts, session, category="Products"))

    admin.add_view(admin_models.PaymentsView(db.Payment, session, category="Payments"))
    admin.add_view(admin_models.CashOnDeliveryView(db.CashOnDelivery, session, category="Payments"))
    admin.add_view(admin_models.MobileMoneyView(db.MobileMoney, session, category="Payments"))
    admin.add_view(admin_models.PaymentMethodsView(db.PaymentMethods, session, category="Payments")) 

    admin.add_view(admin_models.CourierView(db.Courier, session, category="Click_Eat"))
    admin.add_view(admin_models.DeliveryMethodsView(db.DeliveryMethods, session, category="Click_Eat"))
    admin.add_view(admin_models.AccountTypeView(db.AccountType, session, category="Click_Eat"))
    admin.add_view(admin_models.StaffAccountsView(db.StaffAccounts, session, category="Click_Eat"))
    admin.add_view(admin_models.HomeImagesView(db.HomeImages, session, category="Click_Eat"))
    admin.add_view(admin_models.PlacesView(db.PlacePrices, session, category="Click_Eat"))

    admin.add_view(ad_views.LogoutView(name="logout", url="/logout"))



