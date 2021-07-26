from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, BigInteger, ForeignKey, relationship, DateTime, func, extract, hybrid_property
)

from datetime import datetime

class Sales(Base):
    __tablename__ = "sales"

    sales_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), index=True, nullable=False)
    products = relationship("Products", backref="sales")
    quantity = Column(BigInteger, nullable=False)
    amount = Column(BigInteger, nullable=False)
    commision_amount = Column(BigInteger, nullable=False)
    date = Column(DateTime, default=datetime.now(), nullable=False)

    def __repr__(self):
        return str(self.product_id)

    def __call__(self, **kwargs):
        try:
            self.product_id = kwargs.get("product_id")
            self.quantity = kwargs.get("quantity")
            self.amount = kwargs.get("amount")
            self.commision_amount = kwargs.get("commission_amount",0)
            session.add(self)
            return True 

        except Exception as e:
            session.rollback()
            print("Error whilst adding a sale :", e)
            return False

    @classmethod
    def read_sales_sum(cls, attr, *args):
        sales_sum = session.query(func.sum(attr)).filter(*args).scalar()
        return sales_sum if sales_sum else 0

    @hybrid_property
    def sales_day(self):
        return self.date.day

    @sales_day.expression
    def sales_day(cls):
        return extract("day", cls.date)

    @hybrid_property
    def sales_month(self):
        return self.date.month

    @sales_month.expression
    def sales_month(cls):
        return extract("month", cls.date)

    @hybrid_property
    def sales_year(self):
        return self.date.year

    @sales_year.expression
    def sales_year(cls):
        return extract("year", cls.date)


    

    
