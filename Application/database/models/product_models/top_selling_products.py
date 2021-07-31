from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import *
from Application.utils import LazyLoader
pdts = LazyLoader("Application.database.models.product_models.products")


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
            products = []
            top_discounts_ids = cls.query.all()

            if top_discounts_ids:
                for product in top_discounts_ids:
                    pdt = pdts.Products.read_product(id=product.product_id)
                    if pdt:
                        if pdt.approved and pdt.suspend != True:
                            products.append(pdt)

                return [product.serialize() for product in products]

            else:
                return None
        except Exception as e:
            session.rollback()
            print("Error While retriving records: ", e)