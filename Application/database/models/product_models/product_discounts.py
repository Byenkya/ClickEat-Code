from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import *
from Application.utils import LazyLoader
pdts = LazyLoader("Application.database.models.product_models.products")

class ProductDiscounts(Base):
    __tablename__ = "product_discounts"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), index=True, nullable=False)
    products = relationship("Products", backref="product_discounts")
    price = Column(BigInteger, nullable=False)
    from_date = Column(Date)
    to_date = Column(Date)
    is_scheduled= Column(Boolean, nullable=False)

    @classmethod
    def read_all(cls):
        return session.query(cls).all()

    def __call__(self, **kwargs):
        try:
            self.product_id = kwargs.get("product_id")
            self.price = kwargs.get("price")
            self.from_date = kwargs.get("from_date")
            self.to_date = kwargs.get("to_date")
            self.is_scheduled = kwargs.get("is_scheduled")

            if self.is_scheduled:
                product_discount = self.read_product_discount(self.product_id)

                if product_discount:
                    kwargs["products_discount"] = product_discount
                    return self.update_promotional_price(**kwargs)
                else:
                    product = pdts.Products.read_product(self.product_id)
                    if product and product.price > self.price:
                        product.promotional_price_set = True
                        session.add(self)
                        session.commit()
                    else:
                        return False

                    return True
        except Exception as e:
            print("Adding product discount error: ", e)
            session.rollback()
            return False

    
    @classmethod
    def read_product_discount(cls, id):
        return cls.query.filter_by(product_id=id).first()

    def update_promotional_price(self, **kwargs):
        try:
            products_discount = kwargs.get("products_discount")

            product = pdts.Products().read_product(product_id=self.product_id)
            if product and product.price > self.price:
                product.promotional_price_set = True
                products_discount.price = self.price
                products_discount.is_fixed = self.is_fixed
                products_discount.from_date = self.from_date
                products_discount.to_date = self.to_date
                products_discount.is_scheduled = self.is_scheduled
                session.commit()

                return True

            else:
                return False
        
        except Exception as e:
            print("Updating Product discount Error: ", e)
            session.rollback()
            return False

    @classmethod
    def remove_promotion_price(cls, product_id):
        try:
            product = pdts.Products.read_product(product_id)
            if product and cls.query.filter_by(product_id=product_id).delete():
                product.promotional_price_set = False
                session.commit()
                return True
            else:
                return False

        except Exception as e:
            print("Removing product promotion price error: ", e)
            session.rollback()
            return False 


