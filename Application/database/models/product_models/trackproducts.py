from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, BigInteger, DateTime, ForeignKey, relationship
)
from datetime import datetime
#from Application.utils import LazyLoader

class TrackProducts(Base):
    __tablename__ = "trackprodcuts"

    id = Column(Integer, primary_key=True)
    quantity = Column(BigInteger, nullable=False)
    date = Column(DateTime, default=datetime.now, nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"),index=True, nullable=False)
    product = relationship("Products", backref="trackproducts")

    def __repr__(self):
        """ String representation """
        return self.product_id

    def __call__(self, **kwargs):
        try:
            self.quantity = kwargs.get("quantity")
            self.product_id = kwargs.get("product_id")
            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error whilst adding tracking product detail: ", e)
            session.rollback()
            return False
