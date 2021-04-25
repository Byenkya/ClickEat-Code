from Application.database.sqlalchemy_imports import (Column, Integer, String, ForeignKey, relationship, BigInteger,
func)
from Application.database.initialize_database import Base, session
from Application.utils import LazyLoader
from random import sample
from Application.flask_imports import jsonify
from Application.database.models import HomeImages

#lazy loading dependencies.
brnd = LazyLoader("Application.database.models.product_models.brand")

class Products(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    product_picture =  Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    price = Column(BigInteger, nullable=False)
    promotional_price = Column(BigInteger, nullable=True)
    resturant_id = Column(Integer, ForeignKey("resturant.id"), nullable=True)
    resturant = relationship("Resturant", backref="products")
    brand_id = Column(Integer, ForeignKey("brand.brand_id"), index=True, nullable=False)
    brand = relationship("Brand", backref="products")
    sub_category_id = Column(Integer, ForeignKey("sub_category.sub_category_id"), index=True, nullable=False)
    sub_category = relationship("SubCategory", backref="products")

    def __repr__(self):
        return str(self.name)

    def __call__(self, **kwargs):
        try:
            self.name = kwargs.get("name")
            self.product_picture = kwargs.get("product_picture")
            self.description = kwargs.get("description")
            self.price = kwargs.get("price")
            self.resturant_id = kwargs.get("resturant_id")
            brand_name = kwargs.get("brand")
            self.sub_category_id = kwargs.get("sub_category_id")
            brand_exists = brnd.Brand.read_brand_filter(
                brnd.Brand.name.like(
                    "%{}%".format(brand_name)
                )
            )
            if brand_exists:
                self.brand = brand_exists
            else:
                brand = brnd.Brand(name=brand_name)
                self.brand = brand

            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error while adding product: ", e)
            session.rollback()
            return False

    def serialize(self):
        return {
                "product_id": self.product_id,
                "name": self.name,
                "product_picture": self.product_picture,
                "description": self.description,
                "price": self.price,
                "resturant_id": self.resturant_id,
                "resturant": self.resturant.business_name,
                "brand_id": self.brand_id,
                "brand": self.brand.name,
                "sub_category_id": self.sub_category_id,
                "sub_category": self.sub_category.name
            }

    @classmethod
    def read_product(cls,id):
        product = cls.query.filter_by(product_id=id).first()
        if product:
            return product

    @classmethod
    def read_product_by_sub_cat(cls, sub_category_id):
        return cls.query.filter_by(sub_category_id=sub_category_id).first() 

    @classmethod
    def read_products_based_on_sub_cat(cls, sub_category_id):
        return cls.query.filter_by(sub_category_id=sub_category_id).all()

    @classmethod
    def read_products_count(cls):
        return session.query(func.count(cls.product_id)).scalar()

    @classmethod
    def home_products(cls):
        #home products
        home_products = []
        products = sample([product.serialize() for product in cls.query.all() if product.resturant.favourite], 4)
        drinks = sample([product.serialize() for product in cls.query.filter_by(sub_category_id=6).all()], 4)

        home_products.append({"id":1,"title":"Favorite Food & Snacks", "products":products})
        home_products.append({"id":2,"title":"Most Selling Drinks", "products":drinks })

        return home_products



    @classmethod
    def read_all_products(cls, return_query=False, **kwargs):
        """
            if return_query is set to True, will return query object,
            otherwise returns list.
        """
        if return_query:
            return cls.query.filter_by(**kwargs).first()
        else:
            products_based_on_sub_cat_dict = {}
            product_based_on_sub_cat_list = []
            restaurant_products = cls.query.filter_by(**kwargs).all()

            for product in restaurant_products:
                if f"{product.sub_category}" in products_based_on_sub_cat_dict:
                    if product not in products_based_on_sub_cat_dict[f"{product.sub_category}"]: #Avoid duplicates
                        products_based_on_sub_cat_dict[f"{product.sub_category}"] += [product.serialize()] #Add the product to is group

                else:
                    products_based_on_sub_cat_dict[f"{product.sub_category}"] = [product.serialize()]

            for sub_cat,products in products_based_on_sub_cat_dict.items():
                banch = {"sub_category": sub_cat, "products": products}
                product_based_on_sub_cat_list.append(banch)


            return product_based_on_sub_cat_list





        


