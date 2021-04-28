from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import  Integer,Column, String

class HomeImages(Base):
    __tablename__ = "home_images"

    image_id = Column(Integer, primary_key=True)
    info_type = Column(String(100), nullable=False)
    image_name = Column(String(100), nullable=False)
    image_desc = Column(String(500), nullable=True)

    def serialize(self):
        return {
            "id": self.image_id,
            "info_type": self.info_type, 
            "image_name": self.image_name,
            "image_desc": self.image_desc
        }

    @classmethod
    def home_images(cls):
        try:
            images = cls.query.all()
            return [image.serialize() for image in images]

        except:
            session.rollback()

    @classmethod
    def read_image(cls, id):
        try:
            image = cls.query.filter_by(image_id=id).first()
            return image.serialize()
        except:
            session.rollback()

    @classmethod
    def delete_image(cls, id):
        try:
            image = cls.query.filter_by(image_id=id).first()
            if image:
                session.query(cls).filter_by(image_id=id).delete()
                session.commit()
                return True
            else:
                return False
        except:
            session.rollback()
