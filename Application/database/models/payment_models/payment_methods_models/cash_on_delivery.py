from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, String,ForeignKey, relationship, Enum
)

class CashOnDelivery(Base):
    __tablename__ = "cash_on_delivery"

    transaction_id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payment.payment_id"), index=True, nullable=False)
    payment = relationship("Payment", backref="cash_on_delivery")
    transaction_ref = Column(String(50), nullable=False)
    status  = Column(Enum("pending", "failed", "confirmed", "cancelled"), nullable=False)

    def __call__(self, **kwargs):
        try:
            self.payment_id = kwargs.get("payment_id")
            self.transaction_ref = kwargs.get("transaction_ref")
            self.status = "pending"

            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error whilst recording transaction: ", e)
            session.rollback()
            return False

    @classmethod
    def read_cash_on_delivery(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()
