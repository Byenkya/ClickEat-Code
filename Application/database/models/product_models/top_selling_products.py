from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import *
from Application.utils import LazyLoader
pdts = LazyLoader("Application.database.models.product_models.products")


class TopSellingProducts(Base):
    __tablename__ = "top_selling_products"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), index=True, nullable=False)
    products = relationship("Products", backref="top_selling_products")

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