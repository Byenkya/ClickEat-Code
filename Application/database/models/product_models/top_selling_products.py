from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import *
from Application.utils import LazyLoader
pdts = LazyLoader("Application.database.models.product_models.products")
from datetime import datetime
import pytz

class TopSellingProducts(Base):
    __tablename__ = "top_selling_products"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), index=True, nullable=False)
    products = relationship("Products", backref="top_selling_products")

    def __repr__(self):
        return str(self.product_id)

    def __call__(self, **kwargs):
        try:
            product = self.query.filter_by(product_id=kwargs.get("product_id")).first()
            if product:
                return False
            else:
                self.product_id = kwargs.get("product_id")
                session.add(self)
                session.commit()
                return True
        except Exception as e:
            print("Error while adding product to top most selling product: ", e)
            session.rollback()
            return False

    @classmethod
    def read_top_most_selling_product(cls, product_id):
        try:
            product = cls.query.filter_by(product_id=product_id).first()
            if product:
                return True
            else:
                return False
                
        except Exception as e:
            print("Error while reading top selling product", e)
            session.rollback()
            return False

    @classmethod
    def delete_pdt_from_top_selling(cls, product_id):
        try:
            cls.query.filter_by(product_id=product_id).delete()
            session.commit()
            return True
        except Exception as e:
            print("Error while deleting product from top selling product", e)
            session.rollback()
            return False

    @classmethod
    def read_all_top_discount_products(cls):
        try:
            timezone = pytz.timezone("Africa/Kampala")
            _date = timezone.localize(datetime.now())
            current_time = _date.astimezone(timezone)
            products = []
            top_discounts_ids = cls.query.all()

            if top_discounts_ids:
                for product in top_discounts_ids:
                    pdt = pdts.Products.read_product(id=product.product_id)
                    if pdt:
                        if pdt.approved and pdt.suspend != True:
                            start_date = timezone.localize(pdt.resturant.operation_start_time)
                            end_date = timezone.localize(pdt.resturant.operation_stop_time)
                            operation_start_time = start_date.astimezone(timezone)
                            operation_stop_time = end_date.astimezone(timezone)
                            if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                                try:
                                    pdt = pdt.serialize()
                                    pdt["available"] = True
                                    products.append(pdt)
                                except Exception as e:
                                    print(e)
                            else:
                                try:
                                    products.append(pdt.serialize())
                                except Exception as e:
                                    print(e)

                return products

            else:
                return None
        except Exception as e:
            session.rollback()
            print("Error While retriving records: ", e)