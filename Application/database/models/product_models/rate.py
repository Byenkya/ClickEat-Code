from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, BigInteger, ForeignKey, relationship, func
)

class Rate(Base):
    __tablename__ = "rate"

    id = Column(Integer, primary_key=True)
    rate = Column(BigInteger, nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.id"), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), index=True, nullable=False)
    customer = relationship("Customer", backref="rate")
    products = relationship("Products", backref="rate")

    def __repr__(self):
        return str(self.product_id)

    def __call__(self, **kwargs):
        try:
            self.rate = kwargs.get("rate")
            self.customer_id = kwargs.get("customer_id")
            self.product_id = kwargs.get("product_id")
            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error while rating a product :", e)
            session.rollback()
            return False

    @classmethod
    def read_product_rate(cls, product_id):
        try:
            pdt_ratings = session.query(func.count(cls.rate), cls.rate)\
                .group_by(cls.rate).filter_by(product_id=product_id).all()

            numerator = 0
            denomenator = 0

            for rate in pdt_ratings:
                denomenator += rate[0]

                if rate[1] == 5:
                    numerator += rate[0] * 100

                elif rate[1] == 4:
                    numerator += rate[0] * 80

                elif rate[1] == 3:
                    numerator += rate[0] * 60

                elif rate[1] == 2:
                    numerator += rate[0] * 40

                elif rate[1] == 1:
                    numerator += rate[0] * 20

            if pdt_ratings:
                return int(((numerator/denomenator)/100) * 5)
            else:
                return 0
        except:
            session.rollback()






















