from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, String, DateTime, Boolean, func
)
from Application.utils import LazyLoader
from datetime import datetime

dd = LazyLoader("Application.database.models.order_models.delivery_details")

class Courier(Base):
    __tablename__ = "courier"

    id = Column(Integer, primary_key=True)
    courier_name = Column(String(100), nullable=False)
    driver_license_number = Column(String(30), unique=True, nullable=False)
    contact = Column(String(13), unique=True, nullable=False)
    second_contact = Column(String(13), unique=True, nullable=False)
    email = Column(String(30), nullable=False)
    address = Column(String(500), nullable=False)
    district = Column(String(50), nullable=False)
    vehicle_type = Column(String(20), nullable=False)
    vehicle_license_plate_number = Column(String(20), nullable=False)
    courier_pic = Column(String(50), nullable=False)
    local_council_1_letter = Column(String(50), nullable=False)
    agreement_letter = Column(String(50), nullable=False)
    national_id_number = Column(String(20), nullable=False)
    registration_date = Column(DateTime, default=datetime.now(), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return self.id

    def __call__(self, **kwargs):
        try:
            self.courier_name = kwargs.get("courier_name")
            self.driver_license_number = kwargs.get("driver_license_number")
            self.contact = kwargs.get("contact")
            self.second_contact = kwargs.get("second_contact")
            self.email = kwargs.get("email")
            self.address = kwargs.get("address")
            self.district = kwargs.get("district")
            self.vehicle_type = kwargs.get("vehicle_type")
            self.vehicle_license_plate_number = kwargs.get("vehicle_license_plate_number")
            self.courier_pic = kwargs.get("courier_pic")
            self.local_council_1_letter = kwargs.get("local_council_1_letter")
            self.agreement_letter = kwargs.get("agreement_letter")
            self.national_id_number = kwargs.get("national_id_number")

            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error whilst adding courier: ", e)
            session.rollback()
            return False

    def serialize(self):
        return {
            "courier_id": self.id,
            "courier_name": self.courier_name,
            "driver_license_number": self.driver_license_number,
            "vehicle_reg": self.vehicle_license_plate_number,
            "vehicle_type": self.vehicle_type,
            "contact": self.contact,
            "email": self.email,
            "address": self.address,
            "NIN": self.national_id_number
        }

    @classmethod
    def read_courier(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def read_courier_districts(cls):
        return session.query(cls.district).group_by(cls.district).all()

    @classmethod
    def read_district_couriers(cls, district):
        return cls.query.filter_by(district=district,is_available=True).all()

    @classmethod
    def read_couriers(cls):
        return cls.query.all()

    @property
    def deliveries_count(self):
        count = session.query(func.count(dd.DeliveryDetails.id))\
            .filter(dd.DeliveryDetails.courier_id == self.id).scalar()


        return count if count else 0
