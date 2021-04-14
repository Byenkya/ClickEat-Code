from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import Column, Integer, String

class Brand(Base):
    __tablename__ = "brand"

    brand_id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

    def __call__(self, name):
        try:
            self.name = name
            session.add(self)
            session.commit()

        except Exception as e:
            print("Adding brand error: ", e)
            session.rollback()
            raise

    @classmethod
    def read_brand(cls, **kwargs):
        return session.query(cls).filter_by(**kwargs).first()

    @classmethod
    def read_brand_filter(cls, *args):
        return session.query(cls).filter(*args).first()

