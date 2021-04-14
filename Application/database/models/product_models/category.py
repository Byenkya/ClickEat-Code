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

    def read_categories(self):
        return session.query(self).all()

    

    