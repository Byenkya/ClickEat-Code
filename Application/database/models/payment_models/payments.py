from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, DateTime, ForeignKey, relationship
)

from datetime import datetime

class Payment(Base):
    __tablename__ = "payment"   

    payment_id = Column(Integer, primary_key=True)
    payment_date = Column(DateTime, default=datetime.now(), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payments_methods.id"), index=True, nullable=False)
    payment_method = relationship("PaymentMethods", backref="payment")
    order_id = Column(Integer, ForeignKey("order.id"), index=True, nullable=False)
    order = relationship("Order", uselist=False, backref="payment")  

    def __call__(self, **kwargs):  
        try:
            self.payment_method_id = kwargs.get("payment_method_id")
            self.order_id = kwargs.get("order_id")

            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error whilst adding payment record: ", e)
            session.rollback()
            return False