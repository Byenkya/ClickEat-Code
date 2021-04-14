from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, String, Boolean
)

class DeliveryMethods(Base):
    __tablename__ = "delivery_methods"

    id = Column(Integer, primary_key=True)
    method = Column(String(30), nullable=False)
    availability_period = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return self.id

    def __call__(self, **kwargs):
        try:
            self.method = kwargs.get("method")
            self.availability_period = kwargs.get("availability_period")

            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error whilst adding delivery method: ", e)
            session.rollback()
            return False