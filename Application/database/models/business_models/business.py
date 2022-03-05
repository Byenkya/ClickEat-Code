from Application.database.sqlalchemy_imports import (
    Column, Integer, String, Boolean, DateTime, func, Enum, BigInteger, Float
)

from Application.database.initialize_database import Base, session, pwd_context
from datetime import datetime
from Application.utils import LazyLoader

#lazy loading i.e some data will be intialized when its actually needed.
pdts = LazyLoader("Application.database.models.product_models.products")

def rest_generator(data_list):
    for restaurant in data_list:
        if restaurant.deals_in != "drinks":
            if restaurant.approved:
                yield restaurant


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
    operation_start_time = Column(DateTime, default=datetime.now(), nullable=False)
    operation_stop_time = Column(DateTime, default=datetime.now(), nullable=False)
    #standard_delivery_fee = Column(Float, nullable=False, default=0.0)

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
        start_hour = ""
        start_mins = ""
        stop_hour = ""
        stop_mins = ""
        if len(str(self.operation_start_time.hour)) == 1:
            start_hour = "0" + str(self.operation_start_time.hour) 
        else:
            start_hour = self.operation_start_time.hour

        if len(str(self.operation_start_time.minute)) == 1:
            start_mins = "0" + str(self.operation_start_time.minute) 
        else:
            start_mins = self.operation_start_time.minute

        if len(str(self.operation_stop_time.hour)) == 1:
            stop_hour = "0" + str(self.operation_stop_time.hour) 
        else:
            stop_hour = self.operation_stop_time.hour

        if len(str(self.operation_stop_time.minute)) == 1:
            stop_mins = "0" + str(self.operation_stop_time.minute)
        else:
            stop_mins = self.operation_stop_time.minute

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
            "admin_telephone": self.admin_telephone,
            "operation_start_time": "{hour}:{minute} AM".format(hour=start_hour,minute=start_mins),
            "operation_stop_time": "{hour}:{minute} PM".format(hour=stop_hour,minute=stop_mins),
            "operational_status": False
        }

    @property
    def read_rest_total_products_count(self):
        total = session.query(func.count(pdts.Products.product_id))\
            .filter(pdts.Products.resturant_id==self.id).scalar()  
        return total if total else 0

    @property
    def approved_products_count(self):
        total = session.query(func.count(pdts.Products.product_id))\
            .filter(pdts.Products.resturant_id==self.id, pdts.Products.approved==True).scalar()  
        return total if total else 0
    
    @property
    def not_approved_products_count(self):
        total = session.query(func.count(pdts.Products.product_id))\
                .filter(pdts.Products.resturant_id==self.id, pdts.Products.approved==False).scalar()
        return total if total else 0

    @property
    def suspended_products_count(self):
        total = session.query(func.count(pdts.Products.product_id))\
                .filter(pdts.Products.resturant_id==self.id, pdts.Products.suspend==True).scalar()
        return total if total else 0

    @property
    def read_all_rest_products(self):
        products = session.query(pdts.Products).filter_by(resturant_id=self.id).all()
        return products

    @property
    def read_all_approved_products(self):
        products = session.query(pdts.Products).filter(pdts.Products.resturant_id==self.id, pdts.Products.approved==True).all()
        return products

    @property
    def read_all_non_approved_products(self):
        products = session.query(pdts.Products).filter(pdts.Products.resturant_id==self.id, pdts.Products.approved==False).all()
        return products

    @property
    def read_all_suspended_products(self):
        products = session.query(pdts.Products).filter(pdts.Products.resturant_id==self.id, pdts.Products.suspend==True).all()
        return products

    @classmethod
    def read_restaurant(cls, id):
        try:
            return cls.query.filter_by(id=id).first()
        except:
            session.rollback()

    @classmethod
    def read_restaurants(cls):
        try:
            # rest = []
            # restaurants = cls.query.all()
            # for restaurant in restaurants:
            #     if restaurant.deals_in != "drinks":
            #         if restaurant.approved:
            #             rest.append(restaurant)
            return list(rest_generator(cls.query.all()))
        except:
            session.rollback()

    @classmethod
    def read_all_rests(cls):
        try:
            return cls.query.all()
        except Exception as e:
            session.rollback()

    @classmethod
    def read_restaurants_count(cls):
        try:
            return session.query(func.count(cls.id)).scalar()
        except:
            session.rollback()

    @classmethod
    def read_all_restaurants_filter_by(cls,*args, **kwargs)->list:
        """
            returns tuple objects
            tuples are made of attributes specified as args
        """
        query = session.query(*[getattr(cls,i) for i in args]).filter_by(**kwargs).all()
        if len(args) == 1 and query:
            query = [i[0] for i in query]
        return query




    
