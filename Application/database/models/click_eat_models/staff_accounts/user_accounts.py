from Application.database.initialize_database import Base, session, pwd_context
from Application.database.sqlalchemy_imports import (
    Column, Integer, String, Boolean, ForeignKey, relationship
)
from Application.flask_imports import UserMixin

class StaffAccounts(Base, UserMixin):
    __tablename__ = "staff_accounts"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    contact = Column(String(13), nullable=False, unique=True)
    address = Column(String(255), nullable=False)
    account_active = Column(Boolean, default=True, nullable=False)
    account_type_id = Column(Integer, ForeignKey("account_type.id"), index=True, nullable=False)
    account_type = relationship("AccountType", backref="staff_accounts")

    # def __repr__(self):
    #     return self.username

    def __call__(self, **kwargs):
        try:
            self.username = kwargs.get("username")
            self.hash_password(kwargs.get("password"))
            self.email = kwargs.get("email")
            self.name = kwargs.get("name")
            self.contact = kwargs.get("contact")
            self.address = kwargs.get("address")
            self.account_type_id = kwargs.get("account_type_id")

            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error whilst adding user account: ", e)
            session.rollback()
            return False

    def update_employee_details(self, **kwargs):
        try:
            self.email = kwargs.get("email", self.email)
            self.name = kwargs.get("name", self.name)
            self.contact = kwargs.get("contact", self.contact)
            self.address = kwargs.get("address", self.address)
            session.commit()
        except Exception as e:
            session.rollback()
            raise Exception(f"Updating user error: {e}")

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    @property
    def is_employee(self):
        return True

    @classmethod
    def read_user(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def admin_exists(cls):
        return session.query(cls).join(
            "account_type"
        ).filter(
            AccountType.type_name == "administrator"
        ).first()

    def hash_password(self, password):
        self.password = pwd_context.hash(password)

class AccountType(Base):
    __tablename__ = "account_type"

    id = Column(Integer, primary_key=True)
    type_name = Column(String(50), nullable=False, unique=True)

    def __call__(self, **kwargs):
        try:
            self.type_name = kwargs.get("type_name")

            session.add(self)
            session.commit()
            return self

        except Exception as e:
            print("Error whilst adding account_type: ", e)
            session.rollback()
            return False

    def __repr__(self):
        return self.type_name

    def get_employee(self):
        return self.query.filter_by(type_name="Employee").first()