from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, String, Enum, relationship, ForeignKey, BigInteger
)

class MobileMoney(Base):
    __tablename__ = "mobile_money"

    transaction_id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payment.payment_id"), index=True, nullable=False)
    payment = relationship("Payment", backref="mobile_money")
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    amount = Column(BigInteger, nullable=False)
    contact = Column(String(13), nullable=False)
    status = Column(Enum("pending", "failed", "confirmed", "cancelled"), nullable=False)
    transaction_ref = Column(String(50), nullable=False)