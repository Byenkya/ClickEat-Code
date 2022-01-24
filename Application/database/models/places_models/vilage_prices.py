from shutil import ExecError
from Application.database.sqlalchemy_imports import (
    Column, Integer, String,
)
from Application.database.initialize_database import Base, session

class PlacePrices(Base):
    __tablename__ = "place_prices"

    id = Column(Integer, primary_key=True)
    district_name = Column(String(100), nullable=False)
    parish_name  = Column(String(100), nullable=True, default='Arua city')
    sub_county_name = Column(String(100), nullable=False)
    village = Column(String(100), nullable=False)
    fee = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return self.village

    def __call__(self, **kwargs):
        try:
            self.district_name = kwargs.get("county_name")
            self.parish_name = kwargs.get("parish_name", "Arua city")
            self.sub_county_name = kwargs.get("sub_county_name")
            self.village = kwargs.get("village")
            self.fee = kwargs.get("fee")

            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Adding Place fee error: ", e)
            session.rollback()
            return False

    def serialize(self):
        return {
            "village": self.village,
            "fee": self.fee,
            "sub_county_name": self.sub_county_name,
            "county_name": self.district_name
        }

    @classmethod
    def read_place_prices(cls):
        try:
            return [place.serialize() for place in cls.query.all()]
        except Exception as e:
            print("Error Whilst retriving places: ", e)

