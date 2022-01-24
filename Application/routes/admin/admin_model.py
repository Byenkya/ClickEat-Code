from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.form.upload import ImageUploadField, FileUploadField
from flask_admin.contrib.sqla.form import fields

from flask import flash
from Application import app
from Application.database import models as db
from Application.flask_imports import current_user
from Application.helpers.generators import ReferenceGenerator
from Application.database.initialize_database import session
from PIL import Image
import os

business_storage = os.path.join(
    app.root_path, 'static/business_profile_picture'
)

home_images_storage = os.path.join(
    app.root_path, 'static/home_images'
)

product_images = os.path.join(
    app.root_path, 'static/product_images'
)

courier_images = os.path.join(
    app.root_path, 'static/courier_images'
)

courier_doc_storage = os.path.join(
    app.root_path, 'static/courier_docs'
)

class CustomImageFileUpload(ImageUploadField):
    def generate_name(self, obj, file_data):
        new_name = ReferenceGenerator().unique_filename()
        name, ext = os.path.splitext(file_data.filename)
        if len(name) > 20:
            name = name[:20]
        
        filename = f"{name}-image-{new_name}.jpg"

        if not self.relative_path:
            return filename

        return urljoin(self.relative_path, filename)

class CustomFileUpload(FileUploadField):

    def generate_name(self, obj, file_data):
        new_name = ReferenceGenerator().unique_filename()
        name,ext = os.path.splitext(file_data.filename)
        filename = f"{name}-file-{new_name}{ext}"
        if len(name) > 20:
            name = name[:20]
        if not self.relative_path:
            return filename

        return urljoin(self.relative_path, filename)

class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and str(getattr(current_user, "account_type", None)) == "administrator"


## Customer Models 
class CustomerView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = True

    column_searchable_list = (
        "name", "email", "contact", "date_of_registration"
    )

    column_filters = ("name", "email", "contact", "date_of_registration")
    column_details_exclude_list = ("_password",)
    column_exclude_list = ("_password",)

    def scaffold_form(self):
        form_class = super(CustomerView, self).scaffold_form()

        return form_class


## Business Models
class ResturantView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = True

    column_searchable_list = ("business_name", "address", "email")
    column_filters = ("date_of_registration", "business_name", "email")

    def scaffold_form(self):
        form_class = super(ResturantView, self).scaffold_form()
        form_class.business_profile_picture = CustomImageFileUpload(
            label = "Resturant Profile Picture",
            base_path = business_storage,
            allowed_extensions = ["png", "jpg", "jpeg"],
            max_size = (250,250, True),
            url_relative_path="business_profile_picture/"
        )

        return form_class

## HomeImages Model
class HomeImagesView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = True

    column_searchable_list = ("image_name",)
    column_filters = ("image_name",)

    def scaffold_form(self):
        form_class = super(HomeImagesView, self).scaffold_form()
        form_class.image_name = CustomImageFileUpload(
            label = "Carousel Images",
            base_path = home_images_storage,
            allowed_extensions = ["png", "jpg", "jpeg"],
            max_size = (600,600, True),
            url_relative_path="home_images/"
        )

        return form_class


    def delete_model(self, form):
        image = db.HomeImages.read_image(form.image_id)
        if image:
            try:
                file_path = os.path.join(home_images_storage, image["image_name"])
                os.remove(file_path)
                db.HomeImages.delete_image(image["id"])
                flash("Image Deleted successfully!!")
            except Exception as e:
                flash(str(e))


## Order Models
class OrderView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_searchable_list = ("id", "order_date", "customer_id")
    column_filters = ("id", "order_date", "customer_id")

class DeliveryDetailsView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_searchable_list = ("id", "county", "sub_county")
    column_filters = ("id", "id", "courier_id", "customer_id")


## Product Models
class ProductsView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = True

    column_searchable_list = ("name",)
    column_filters = ("product_id", "name", "resturant_id", "brand_id", "sub_category_id")

    def scaffold_form(self):
        form_class = super(ProductsView, self).scaffold_form()
        form_class.product_picture = CustomImageFileUpload(
            label = "Product Image",
            base_path = product_images,
            allowed_extensions = ["png", "jpg", "jpeg"],
            max_size = (250,250, True),
            url_relative_path="product_images/"
        )

        return form_class

    # def update_model(self,form, model):
    #     product = db.Products.read_product(model.product_id)
    #     try:
    #         from random import randint      
    #         filename = form.product_picture.data
    #         file_path = os.path.join(product_images, model.product_picture)
    #         os.remove(file_path)
    #         new_image_name = "-".join(["clickEat",str(randint(1000000,10000000)),filename.filename])
    #         new_image_path = os.path.join(product_images, new_image_name)
    #         i = Image.open(filename)
    #         new_image =  i.resize((500,500))
    #         new_image.save(new_image_path)
    #         product.product_picture = new_image_name
    #         session.commit()
    #         flash("Product updated successfully!!")

    #     except Exception as e:
    #         flash(str(e))

class ProductDiscountsView(CustomerView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = True

    column_searchable_list = ("product_id",)
    column_filters = ("price",)

    def scaffold_form(self):
        form_class = super(ProductDiscountsView, self).scaffold_form()

        return form_class

class TopSellingProductsView(CustomerView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = True

    column_searchable_list = ("product_id",)
    column_filters = ("product_id",)

    def scaffold_form(self):
        form_class = super(TopSellingProductsView, self).scaffold_form()

        return form_class

class CategoryView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = True

    column_searchable_list = ("category_id",)
    column_filters = ("name",)

    def scaffold_form(self):
        form_class = super(CategoryView, self).scaffold_form()

        return form_class

class SubCategoryView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = True

    column_searchable_list = ("sub_category_id",)
    column_filters = ("name", "category_id")

    def scaffold_form(self):
        form_class = super(SubCategoryView, self).scaffold_form()

        return form_class

class BrandView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = True

    column_searchable_list = ("brand_id",)
    column_filters = ("name",)

    def scaffold_form(self):
        form_class = super(BrandView, self).scaffold_form()

        return form_class

class CartView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = False

    column_searchable_list = ("id", "product_id", "product_name")
    column_filters = ("product_name", "customer_id")

class CommentsView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_searchable_list = ("date",)
    column_filters = ("date", "customer_id", "product_id")

class RateView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_searchable_list = ("rate",)
    column_filters = ("customer_id", "product_id")

class SalesView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_filters = ("product_id",)

class TrackProductsView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_filters = ("product_id",)


## Payment Models  
class PaymentMethodsView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = False
    can_create = True

    column_filters = ("id",)

class PaymentsView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_filters = ("payment_method_id",)

class CashOnDeliveryView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_filters = ("status",)

class CouponPayView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_filters = ("status",)

class MobileMoneyView(CustomModelView):
    can_delete = False
    can_view_details = True
    can_export = True
    can_create = False

    column_filters = ("status",)

## Click eat Models
class CourierView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = True

    column_filters = ("courier_name", "vehicle_type")

    def scaffold_form(self):
        form_class = super(CourierView, self).scaffold_form()
        form_class.agreement_letter = CustomFileUpload(
            label="Agreement Letter",
            base_path=courier_doc_storage,
            allowed_extensions=["png","jpg", "pdf"]
            )
        form_class.local_council_1_letter = CustomFileUpload(
            label="Local Council 1 Letter",
            base_path=courier_doc_storage,
            allowed_extensions=["png","jpg", "pdf"]
            )
        form_class.courier_pic = CustomImageFileUpload(
            label = "Courier Profile Picture",
            base_path = courier_images,
            allowed_extensions = ["png", "jpg", "jpeg"],
            max_size = (250,250, True),
            url_relative_path="product_images/"
        )

        return form_class

class DeliveryMethodsView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = True
    can_create = True

    column_filters = ("method", "is_available")

    def scaffold_form(self):
        form_class = super(DeliveryMethodsView, self).scaffold_form()

        return form_class

class PlacesView(CustomModelView):
    can_delete = True
    can_view_deatails = True
    can_export = True
    can_create = True

    column_filters = ("village",)

    def scaffold_form(self):
        form_class = super(PlacesView, self).scaffold_form()

        return form_class

class AccountTypeView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = False
    can_create = True

    column_filters = ("type_name",)

    def scaffold_form(self):
        form_class = super(AccountTypeView, self).scaffold_form()

        return form_class

class StaffAccountsView(CustomModelView):
    can_delete = True
    can_view_details = True
    can_export = False
    can_create = True

    column_exclude_list = ("password",)

    def scaffold_form(self):
        form_class = super(StaffAccountsView, self).scaffold_form()

        # form_class.password = fields.PasswordField(
        #     "Password"
        # )
        # form_class.new_password = fields.PasswordField(
        #     "New Password"
        # )
        # form_class.confirm_password = fields.PasswordField(
        #     "Confirm Password"
        # )

        return form_class

    def create_model(self, form):
        try:
            if form.account_type.data.type_name == "administrator" and \
                db.StaffAccounts.admin_exists():
                flash("Administrator user already exists", "danger")
                return False
            acc_type = db.AccountType().get_employee()
            if acc_type:
                db.StaffAccounts()(
                    username="ClickEat",
                    password=form.password.data,
                    email=form.email.data,
                    name=form.name.data,
                    contact=form.contact.data,
                    address=form.address.data,
                    account_type_id=acc_type.id
                    )

                flash("User created successfully!!.")
        except Exception as e:
            flash(str(e))

    def update_model(self, form, model):
        pass



































