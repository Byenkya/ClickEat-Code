from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, String, Integer, relationship, ForeignKey
    )

class SubCategory(Base):
    __tablename__ = "sub_category"

    sub_category_id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("category.category_id"), index=True, nullable=False)
    category = relationship("Category", backref="sub_category")

    def __repr__(self):
        return self.name
    
    def __call__(self, name, category):
        try:
            self.name = name
            self.category = category
            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Adding subcategory error: ", e)
            session.rollback()
            return False

    def serialize(self):
        return {
            "sub_category_id": self.sub_category_id,
            "name": self.name,
            "category_id": self.category_id
        }

    @classmethod
    def read_sub_cat(cls):
        try:
            return [sub.serialize() for sub in cls.query.all()]
        except:
            session.rollback()
        
    @classmethod
    def read_drink_sub_categories(cls):
        try:
            return session.query(cls).join(cls.category).filter_by(name="Drinks").all()
        except:
            session.rollback()

    
