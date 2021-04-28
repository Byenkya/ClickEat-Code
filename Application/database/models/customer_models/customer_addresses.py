from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import Integer, Column, String, Boolean, ForeignKey, relationship

class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    id = Column(Integer, primary_key=True)
    county = Column(String(50), nullable=False)
    sub_county = Column(String(50), nullable=False)
    village = Column(String(50), nullable=False)
    other_details = Column(String(500), nullable=False)
    is_default = Column(Boolean)
    customer_id = Column(Integer, ForeignKey("customer.id"), index=True, nullable=False)
    customer = relationship("Customer", backref="customer_addresses")

    def __call__(self, **kwargs):
        try:
            self.county = kwargs.get("county")
            self.sub_county = kwargs.get("sub_county")
            self.village = kwargs.get("village")
            self.other_details = kwargs.get("other_details")
            self.is_default = kwargs.get("is_default", self.is_default)
            self.customer_id = kwargs.get("customer_id")

            if self.is_default:
                self.query.filter_by(customer_id=self.customer_id).update({"is_default": False})
            
            if not self.query.filter_by(customer_id=self.customer_id).first():
                self.is_default = True

            session.add(self)
            session.commit()

            return True

        except Exception as e:
            print("Error whilst saving customer address: ", e)
            session.rollback()
            return None

    def serialize(self):
        return {
            "id": self.id,
            "county": self.county,
            "sub_county": self.sub_county,
            "village": self.village,
            "other_details": self.other_details,
            "is_default": self.is_default,
            "customer_id": self.customer_id
        }
    
    @classmethod
    def get_customer_addresses(cls, customer_id):
        try:
            customer_addresses = cls.query.filter_by(customer_id=customer_id).all()
            return [customer_address.serialize() for customer_address in customer_addresses]
        except:
            session.rollback()

    @classmethod
    def update_customer_address(cls, **kwargs):
        try:
            address = cls.query.filter_by(id=kwargs.get("address_id")).first()
            address.county = kwargs.get("county")
            address.sub_county = kwargs.get("sub_county")
            address.village = kwargs.get("village")
            address.other_details = kwargs.get("other_details")
            session.commit()
            return True
        except Exception as e:
            print("Error: >>>>>>>>>>>>>>>>", e)
            session.rollback()
            return False

    @classmethod
    def delete_customer_address(cls, id):
        try:
            session.query(cls).filter_by(id=id).delete()
            session.commit()
            return True
        except Exception as e:
            print("Error: >>>>>>>>>>>>>", e)
            session.rollback()
            return False
        
