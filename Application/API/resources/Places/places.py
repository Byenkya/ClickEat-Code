from flask_restful import Resource 

arua_district_places = {
    "district": "Arua",
    "counties": [
        {
            "county_name": "Ayivu(Arua City)",
            "details": [
                {
                    "sub_county_name": "Oluko",
                    "villages": [
                        {"village": "Abira", "fee":3000}, 
                        {"village": "Abirici", "fee":3000},
                        {"village": "Asava", "fee":3000},
                        {"village": "Awindiri", "fee":1500},
                        {"village": "Ayibiri", "fee":4000},
                        {"village": "Ceford", "fee":2000},
                        {"village": "Euata", "fee":2000},
                        {"village": "Jokiva", "fee":4000},
                        {"village": "Kumara", "fee":4000},
                        {"village": "Kumera", "fee":4000},
                        {"village": "Muni NTC", "fee":3000},
                        {"village": "Muni Site", "fee": 3000},
                        {"village": "Muni University", "fee":2000},
                        {"village": "Oleva", "fee":4000},
                        {"village": "Palwal", "fee":3000},
                        {"village": "Ragem", "fee":2000}
                    ]
                },

                {
                    "sub_county_name": "Adumi",
                    "villages": [
                        {"village": "Uzu", "fee":4000},
                        {"village": "Panduru", "fee":5000}, 
                        {"village": "Pajulu", "fee":5000}, 
                        {"village": "Nyiovura", "fee":5000}, 
                        {"village": "Nyio", "fee":4000}, 
                        {"village": "Mite", "fee":4000}, 
                        {"village": "Etori", "fee":4000},
                        {"village": "Adumi", "fee":4000}
                    ]
                },

                {
                    "sub_county_name": "Pajulu",
                    "villages": [
                        {"village": "Ajiriva", "fee":4000},
                        {"village": "Ambeko", "fee":4000},
                        {"village": "Ediofe", "fee": 2000},
                        {"village": "Ekarakafe", "fee":4000},
                        {"village": "Okaliba", "fee":4000},
                        {"village": "Onialeku", "fee":4000},
                        {"village": "Ouva", "fee":4000},
                        {"village": "Ozuvu", "fee":4000},
                        {"village": "Surusoni", "fee":4000}
                    ] 
                }
            ]
        },

        {
            "county_name": "Arua Municipality(Arua Central Division)",
            "details": [
                {
                    "sub_county_name": "Oli River", 
                    "villages": [
                        {"village": "Abia", "fee":1500},
                        {"village": "Azia", "fee":1500},
                        {"village": "Andalafu", "fee":1000},
                        {"village": "Baruku Central A", "fee":2000},
                        {"village": "Baruku Central B", "fee":2000},
                        {"village": "Kebir", "fee":1000},
                        {"village": "Muru", "fee":2000},
                        {"village": "Obolokofuku East", "fee":2000},
                        {"village": "Ojulua", "fee":2000},
                        {"village": "Oluodri", "fee":3000},
                        {"village": "Osu", "fee":2000},
                        {"village": "Oyooze", "fee":2000},
                        {"village": "Prisons", "fee":1000},
                        {"village": "Upper Bibia A", "fee":1000},
                        {"village": "Upper Bibia B", "fee":1000}           
                        
                    ]
                },
                {
                    "sub_county_name": "Arua Hill",
                    "villages": [
                        {"village": "Anyafio Central", "fee":3000},
                        {"village": "Anyafio East", "fee":3000},
                        {"village": "Anyafio East", "fee":3000},
                        {"village": "Arua Academy", "fee":2000},
                        {"village": "Arua Hill", "fee":2000},
                        {"village": "Awindiri Ward", "fee":2000},
                        {"village": "Awudele Crescent", "fee":3000},
                        {"village": "Bazaar South", "fee":4000},
                        {"village": "Chongaloya", "fee":4000},
                        {"village": "Ewavio", "fee":2000},
                        {"village": "Junior Quaters", "fee":2000},
                        {"village": "Niva", "fee":1000},
                        {"village": "Nsambia North", "fee":2000},
                        {"village": "Nsambia South", "fee":2000},
                        {"village": "Mvara S.S", "fee":2000},
                        {"village": "Zambia", "fee":4000}
                    ]
                },

                {
                    "sub_county_name": "Dadamu",
                    "villages": [
                        {"village": "Airfield", "fee":2000},
                        {"village": "Asuru", "fee":3000},
                        {"village": "Madi", "fee":3000},
                        {"village": "Mvara Central", "fee":2000},
                        {"village": "Ndiriba", "fee":3000},
                        {"village": "Obolokofuku Central", "fee":3000},
                        {"village": "Obolokofuku East", "fee":3000},
                        {"village": "Obolokofuku West", "fee":3000},
                        {"village": "Oli A", "fee":1000},
                        {"village": "Oli B", "fee":1000},
                        {"village": "Oli C", "fee":1000},
                        {"village": "Oli D", "fee":1000},
                        {"village": "Ondoriku", "fee":2000},
                        {"village": "Tanganyika Central", "fee":2000},

                    ]
                }
            ]
        }
    ]
}

class PlacesApi(Resource):
    def get(self):
        return arua_district_places