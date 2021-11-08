from Application.database.sqlalchemy_imports import (
    Column, Integer, String, DateTime, Boolean, UserMixin, func
)

from Application.database.initialize_database import pwd_context, Base, session, app
from datetime import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,BadSignature,SignatureExpired)
from Application.flask_imports import _session
from Application.helpers.generators import TokenGenerator


class Customer(Base, UserMixin):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=True, unique=True)
    contact = Column(String(13), nullable=False, unique=True)
    second_contact = Column(String(13), nullable=True, unique=True)
    profile_picture = Column(String(50), default="click_eat.png")
    _password = Column(String(255), nullable=False)                                         
    date_of_registration = Column(DateTime, nullable=False, default=datetime.now())
    account_active = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return self.name

    def __call__(self, **kwargs):
        try:
            self.name = kwargs.get("name")
            self.email = kwargs.get("email")
            self.contact = kwargs.get("contact")
            self.second_contact = kwargs.get("second_contact")
            self.profile_picture = kwargs.get("profile_picture")
            self.password = kwargs.get("password")
            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Add customer Error: ", e)
            session.rollback()
            return False

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def change_password(self, old_password, new_password):
        if(self.verify_password(old_password)):
            new_password = pwd_context.hash(new_password)
            self._password = new_password
            session.commit()
            return True
        else:
            session.rollback()
            return False

    def update_customer(self, **kwargs):
        try:
            self.name = kwargs.get("name", self.name)
            self.email = kwargs.get("email", self.email)
            self.contact = kwargs.get("contact", self.contact)
            self.second_contact = kwargs.get("second_contact", self.second_contact)
            session.commit()
            return True

        except Exception as e:
            print("Update customer Error:", e)
            session.rollback()
            return False 

    def serializer(self):
        if self.cart:
            return {
                "customer_id": self.id,
                "names": self.name,
                "email": self.email,
                "contact": self.contact,
                "second_contact": self.second_contact,
                "date_of_reg": self.date_of_registration.strftime('%m/%d/%Y'),
                "account_active": self.account_active,
                "cart_size": int(self.cart[0].cart_total_quantity_or_item_count(self.id))
            }

        else:
            return {
                "customer_id": self.id,
                "names": self.name,
                "email": self.email,
                "contact": self.contact,
                "second_contact": self.second_contact,
                "date_of_reg": self.date_of_registration.strftime('%m/%d/%Y'),
                "account_active": self.account_active,
                "cart_size": 0
            }

    def delete_customer(self, id):
        try:
            self.query.filter_by(id=id).delete()
            session.commit()
        except:
            session.rollback()

    @classmethod
    def google_sign_in(cls, email):
        try:
            user = cls.query.filter_by(email=email).first()

            if user:
                token = TokenGenerator(user).generate_api_token()
                user = user.serializer()
                user["token"] = token
                return user
            else:
                return False
        except Exception as e:
            print("An error occured while saving customer google sigin details: ",e)

    @classmethod
    def check_user(cls,telephone,password):
        try:
            user = cls.query.filter_by(contact=telephone).first()
        
            if user and user.verify_password(password):
                token = TokenGenerator(user).generate_api_token()
                user = user.serializer()
                user["token"] = token
                return user
            elif not user:
                user = cls.query.filter_by(email=telephone).first()
                if user and user.verify_password(password):
                    token = TokenGenerator(user).generate_api_token()
                    user = user.serializer()
                    user["token"] = token
                    return user
            
            elif not user or not user.verify_password(password):
                return False

            else:
                return False
                
        except Exception as e:
            print(">>>>>>>>>>>>", e)
            session.rollback()

    @classmethod
    def read_customer_by_contact(cls, **kwargs):
        try:
            customer = cls.query.filter_by(contact=kwargs.get("telephone")).first()

            return customer
        except:
            session.rollback()

    @classmethod
    def read_customer(cls, **kwargs):
        try:
            customer = cls.query.filter_by(**kwargs).first()
            return customer
        except:
            session.rollback()

    @classmethod
    def read_customer_count(cls):
        try:
            return session.query(func.count(cls.id)).scalar()
        except:
            session.rollback()



            