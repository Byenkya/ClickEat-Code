from Application.database.sqlalchemy_imports import (
    Column, Integer, String, Boolean, DateTime, func, Enum
)

from Application.database.initialize_database import Base, session, pwd_context
from datetime import datetime

#lazy loading i.e some data will be intialized when its actually needed.

class Resturant(Base):
    __tablename__ = "resturant"

    id = Column(Integer, primary_key=True)
    business_name = Column(String(100), nullable=False)
    business_profile_picture = Column(String(100), nullable=False)
    deals_in = Column(Enum("drinks", "food", "Vegetables$Fruits"))
    address = Column(String(255), nullable=False)
    email = Column(String(50), nullable=False)
    contact = Column(String(13), unique=True, nullable=False)
    second_contact = Column(String(13), unique=True, nullable=False)
    location = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    admin_names = Column(String(50), unique=True, nullable=False)
    admin_username = Column(String(50), unique=True, nullable=False)
    admin_email = Column(String(50), nullable=False)
    admin_telephone = Column(String(13), unique=True, nullable=False)
    date_of_registration = Column(DateTime, default=datetime.now(), nullable=False)
    favourite = Column(Boolean, nullable=False, default=False)
    approved = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return self.business_name

    def __call__(self, **kwargs):
        try:
            self.business_name = kwargs.get("business_name")
            self.business_profile_picture = kwargs.get("business_profile_picture")
            self.address = kwargs.get("address")
            self.email = kwargs.get("email")
            self.contact = kwargs.get("contact")
            self.second_contact = kwargs.get("second_contact")
            self.location = kwargs.get("location")
            self.description = kwargs.get("description")
            self.admin_names = kwargs.get("admin_names")
            self.admin_username = kwargs.get("admin_user")
            self.admin_email = kwargs.get("admin_email")
            self.admin_telephone = kwargs.get("admin_telephone")

            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Adding resturant error: ", e)
            session.rollback()
            return False

    def serialize(self):
        return {
            "id": self.id,
            "business_name": self.business_name,
            "business_profile_picture": self.business_profile_picture,
            "address": self.address,
            "email": self.email,
            "contact": self.contact,
            "second_contact": self.second_contact,
            "location": self.location,
            "description": self.description,
            "admin_names": self.admin_names,
            "admin_username": self.admin_username,
            "admin_email": self.admin_email,
            "admin_telephone": self.admin_telephone
        }

    @classmethod
    def read_restaurant(cls, id):
        try:
            return cls.query.filter_by(id=id).first()
        except:
            session.rollback()

    @classmethod
    def read_restaurants(cls):
        try:
            food = cls.query.filter_by(deals_in="food").all()
            fruits_veggie = cls.query.filter_by(deals_in="").all()
            return food + fruits_veggie
        except:
            session.rollback()

    @classmethod
    def read_restaurants_count(cls):
        try:
            return session.query(func.count(cls.id)).scalar()
        except:
            session.rollback()


    
