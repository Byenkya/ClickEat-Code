from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Integer, String, Column, Boolean
)

class PaymentMethods(Base):
    __tablename__ = "payments_methods"

    id = Column(Integer, primary_key=True)
    method = Column(String(20), nullable=False, unique=True)
    is_available = Column(Boolean, nullable=False)

    def __repr__(self):
        return self.method

    @classmethod
    def read_method(cls, **kwargs):
        _method = cls.query.filter_by(**kwargs).first()
        return _method

    @classmethod
    def read_all_methods(cls, **kwargs):
        return cls.query.fliter_by(**kwargs).all()

    def serialize(self):
        return {
            "id": self.id,
            "method": self.method,
            "is_available": self.is_available
        }

    