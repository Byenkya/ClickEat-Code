from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import Column, Integer, String
from Application.utils import LazyLoader

#lazy loading dependency models.

class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.name

    def __call__(self, name):
        try:
            self.name = name
            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Adding Category error: ", e)
            session.rollback()
            return False

    def read_category(self, id):
        return session.query(self).filter_by(category_id=id).first()

    @classmethod
    def read_categories(cls):
        return session.query(cls).all()

    @classmethod
    def read_all_categories_by_attr(cls,*args)->list:
        query = session.query(*[getattr(cls, i) for i in args]).all()
        if len(args) == 1 and query:
            query = [i[0] for i in query]
        return query

    

    