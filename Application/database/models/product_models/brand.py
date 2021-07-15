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

    @classmethod
    def read_all_bandss_filter_by(cls,*args, **kwargs)->list:
        """
            returns tuple objects
            tuples are made of attributes specified as args
        """
        query = session.query(*[getattr(cls,i) for i in args]).filter_by(**kwargs).all()
        if len(args) == 1 and query:
            query = [i[0] for i in query]
        return query

