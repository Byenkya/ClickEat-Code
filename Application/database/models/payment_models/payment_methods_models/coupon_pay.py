from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, String, ForeignKey, relationship, Enum
)

class CouponPayment(Base):
    __tablename__ = "coupon_payment"

    transaction_id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payment.payment_id"), index=True, nullable=False)
    payment = relationship("Payment", backref="coupon_payment")
    transaction_ref = Column(String(50), nullable=False)
    status = Column(Enum("pending", "failed", "confirmed", "cancelled"), nullable=False)

    def __repr__(self):
        return self.transaction_id

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