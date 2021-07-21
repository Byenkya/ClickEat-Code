from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, String, DateTime, ForeignKey, relationship
)

from datetime import datetime

class DeliveryDetails(Base):
    __tablename__ = "delivery_details"

    id = Column(Integer, primary_key=True)
    county = Column(String(50), nullable=False)
    sub_county = Column(String(50), nullable=False)
    village = Column(String(50), nullable=False)
    other_details = Column(String(500), nullable=False)
    courier_id = Column(Integer, ForeignKey("courier.id"), index=True, nullable=True)
    courier = relationship("Courier", backref="delivery_details")
    customer_id = Column(Integer, ForeignKey("customer.id"), index=True, nullable=False)
    customer = relationship("Customer", backref="delivery_details")
    order_id = Column(Integer, ForeignKey("order.id"), index=True, nullable=False)
    order = relationship("Order",uselist=False, backref="delivery_details")
    date = Column(DateTime, default=datetime.now())  

    def __call__(self, **kwargs):
        try:
            self.county = kwargs.get("county")
            self.sub_county = kwargs.get("sub_county")
            self.village = kwargs.get("village")
            self.other_details = kwargs.get("other_details")
            self.order_id = kwargs.get("order_id")
            self.customer_id = kwargs.get("customer_id")

            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error whilst recording delivery details: ", e)
            session.rollback()
            return False

    @classmethod
    def assign_courier(cls, courier_id, order_id):
        order = cls.query.filter_by(
            order_id = order_id
            ).first()
        order.courier_id = courier_id
        session.commit()

    @classmethod
    def get_order_delivery_address(cls, order_id):
        return cls.query.filter_by( order_id=order_id).first()




















































