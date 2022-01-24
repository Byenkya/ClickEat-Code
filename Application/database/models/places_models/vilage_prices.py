from shutil import ExecError
from Application.database.sqlalchemy_imports import (
    Column, Integer, String,
)
from Application.database.initialize_database import Base, session

arua_district_places = [
    {"village": "Abira", "fee":4000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"}, 
    {"village": "Abirici", "fee":4000,"sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Asava", "fee":4000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Awindiri", "fee":2000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Ayibiri", "fee":5000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Ceford", "fee":2000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Euata", "fee":2000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Jokiva", "fee":2000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Kumara", "fee":2000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Kumera", "fee":2000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Muni NTC", "fee":3000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Muni Site", "fee": 3000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Muni University", "fee":3000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Oleva", "fee":4000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Palwal", "fee":3000, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Ragem", "fee":2500, "sub_county_name": "Oluko", "county_name":"Ayivu(Arua City)"},
    {"village": "Uzu", "fee":4000, "sub_county_name": "Adumi", "county_name":"Ayivu(Arua City)"},
    {"village": "Panduru", "fee":5000, "sub_county_name": "Adumi", "county_name":"Ayivu(Arua City)"}, 
    {"village": "Junior Quaters", "fee":2000, "sub_county_name": "Adumi", "county_name":"Ayivu(Arua City)"}, 
    {"village": "Nyiovura", "fee":4000, "sub_county_name": "Adumi", "county_name":"Ayivu(Arua City)"}, 
    {"village": "Nyio", "fee":4000, "sub_county_name": "Adumi", "county_name":"Ayivu(Arua City)"}, 
    {"village": "Komite", "fee":4000, "sub_county_name": "Adumi", "county_name":"Ayivu(Arua City)"}, 
    {"village": "Etori", "fee":4000, "sub_county_name": "Adumi", "county_name":"Ayivu(Arua City)"},
    {"village": "Adumi", "fee":4000, "sub_county_name": "Adumi", "county_name":"Ayivu(Arua City)"},
    {"village": "Ajiriva", "fee":4000, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Ambeko", "fee":4000, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Ediofe(Yitia)", "fee": 1000, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Ediofe(Ewanyapa)", "fee": 1500, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Ediofe(Terego Alengo)", "fee": 1500, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Ekarakafe", "fee":10000, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Okaliba", "fee":2000, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Onialeku", "fee":1000, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Ouva", "fee":4000, "sub_county_name": "Arua Hill", "county_name":"Ayivu(Arua City)"},
    {"village": "MUBS", "fee":1500, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Onzivu", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Ozuvu", "fee":4000, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Surusoni", "fee":4000, "sub_county_name": "Pajulu", "county_name":"Ayivu(Arua City)"},
    {"village": "Abia", "fee":2000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Azia", "fee":2000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Andalafu", "fee":1000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Baruku Central A", "fee":2000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Baruku Central B", "fee":2000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Kebir", "fee":1000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Muru", "fee":2000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Obolokofuku East", "fee":2000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Ojulua", "fee":2000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Oluodri", "fee":3000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Osu", "fee":2000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Oyooze", "fee":2000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Prisons", "fee":1000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Upper Bibia A", "fee":1000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Upper Bibia B", "fee":1000, "sub_county_name": "Oli River", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Anyafio Central", "fee":3000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Anyafio East", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Arua Academy", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Arua Hill", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Awindiri Ward", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Awudele Crescent", "fee":1000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Bazaar South", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Chongaloya", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Ewavio", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Junior Quaters", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Niva", "fee":1000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Nsambia North", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Nsambia South", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Mvara S.S", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Zambia", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Airfield", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Asuru", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Madi Quater", "fee":3000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Mvara Central", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Ndiriba", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Obolokofuku Central", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Obolokofuku East", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Obolokofuku West", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Oli A", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Oli B", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Oli C", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Oli D", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Ondoriku", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Tanganyika Central", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Near Heritage Courts", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "UNHCR (Weather Head Park Lane)", "fee":1000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Mvara Trading Center", "fee":2000, "sub_county_name": "Arua Hill", "county_name":"Arua Municipality(Arua Central Division)"},
    {"village": "Ociba Coast", "fee":2000, "sub_county_name": "Dadamu", "county_name":"Arua Municipality(Arua Central Division)"}
]

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


def save_places():
    try:
        for place in arua_district_places:
            place = PlacePrices(
                district_name=place['county_name'],
                parish_name='Arua city',
                sub_county_name=place['sub_county_name'],
                village=place['village'],
                fee=place['fee']
            )
            session.add(place)
        
        session.commit()
        print("Data saved successfully!!!!")

    except Exception as e:
        print("Error while saving places in the database: ", e)