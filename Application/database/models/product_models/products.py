from Application.database.sqlalchemy_imports import (Column, Integer, String, ForeignKey, relationship, BigInteger,
func, Boolean, Float)
from Application.database.initialize_database import Base, session
from Application.utils import LazyLoader
from random import sample
from Application.flask_imports import jsonify
from Application.database.models import HomeImages
import math
from datetime import datetime
import pytz

ni_timezone = pytz.timezone('Africa/Nairobi')
timezone = pytz.timezone("Africa/Kampala")

#lazy loading dependencies.
brnd = LazyLoader("Application.database.models.product_models.brand")
pdtds = LazyLoader("Application.database.models.product_models.product_discounts")
subCat = LazyLoader("Application.database.models.product_models.subcategory")
cat = LazyLoader("Application.database.models.product_models.category")

# generators
def food_snacks_generator(data_list):
    _date = datetime.now(ni_timezone)
    current_time = _date.astimezone(timezone)
    for product in data_list:
        if product.resturant.approved:
            if product.resturant.favourite and product.approved and product.suspend != True:
                _start_date = ni_timezone.localize(product.resturant.operation_start_time)
                _end_date = ni_timezone.localize(product.resturant.operation_stop_time)
                operation_start_time = _start_date.astimezone(timezone)
                operation_stop_time = _end_date.astimezone(timezone)
                if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                    pdt = product.serialize()
                    pdt["available"] = True
                    yield pdt

                else:
                    yield product.serialize()

def drinks_generator(data_list):
    _date = datetime.now(ni_timezone)
    current_time = _date.astimezone(timezone)
    for product in data_list:
        if product.resturant.approved:
            if product.approved and product.suspend != True:
                _start_date = ni_timezone.localize(product.resturant.operation_start_time)
                _end_date = ni_timezone.localize(product.resturant.operation_stop_time)
                operation_start_time = _start_date.astimezone(timezone)
                operation_stop_time = _end_date.astimezone(timezone)
                if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                    pdt = product.serialize()
                    pdt["available"] = True
                    yield pdt
                else:
                    yield product.serialize()



class Products(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    product_picture =  Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    price = Column(BigInteger, nullable=False)
    buying_price = Column(BigInteger, nullable=False, default=0)
    selling_price = Column(BigInteger, nullable=False, default=0)
    served_with = Column(String(1000), nullable=False, default="none")
    # promotional_price = Column(BigInteger, nullable=True)
    promotional_price_set = Column(Boolean, default=False, nullable=False)
    commission_fee = Column(Float, default=0.0)
    resturant_id = Column(Integer, ForeignKey("resturant.id"), nullable=True)
    resturant = relationship("Resturant", backref="products")
    brand_id = Column(Integer, ForeignKey("brand.brand_id"), index=True, nullable=False)
    brand = relationship("Brand", backref="products")
    sub_category_id = Column(Integer, ForeignKey("sub_category.sub_category_id"), index=True, nullable=False)
    sub_category = relationship("SubCategory", backref="products")
    approved = Column(Boolean, nullable=False, default=False)
    suspend = Column(Boolean, nullable=False, default=False)
    headsup = Column(String(100), nullable=False, default="clickEat") 
    free_delivery = Column(Boolean, nullable=False, default=False)

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

            self.buying_price = kwargs.get("buying_price",0)
            self.selling_price = kwargs.get("selling_price",0)
            self.served_with = kwargs.get("served_with", 'none')
            self.commission_fee = kwargs.get("commission_fee",0.0)
            self.headsup = kwargs.get("headsup","clickEat")

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
                "price": self.product_price,
                "resturant_id": self.resturant_id,
                "resturant": self.resturant.business_name,
                "brand_id": self.brand_id,
                "brand": self.brand.name,
                "sub_category_id": self.sub_category_id,
                "sub_category": self.sub_category.name,
                "promotional_price_set": self.promotional_price_set,
                "promotional_price": self.promotional_price,
                "headsup": self.headsup,
                "served_with": self.served_with,
                "free_delivery": self.free_delivery,
                "available": False
            }

    @property
    def product_price(self):
        if self.commission_fee != 0.0:
            product_price = self.commission_amount + self.price
            return product_price
        else:
            return self.price

    @property
    def promotional_price(self):
        if self.promotional_price_set:
            price = session.query(pdtds.ProductDiscounts).filter_by(product_id=self.product_id).first()
            return (price.price+self.commission_amount) if price else None
        else:
            return None 

    @property
    def commission_amount(self):
        commission_amount = ((self.commission_fee)/100)*self.price
        return math.ceil(commission_amount)

    @classmethod
    def read_products(cls):
        try:
            return cls.query.all()
        except:
            session.rollback()

    @classmethod
    def read_product(cls,id):
        try:
            product = cls.query.filter_by(product_id=id).first()
            if product:
                return product
        except:
            session.rollback()

    @classmethod
    def read_product_by_sub_cat(cls, sub_category_id):
        try:
            product = cls.query.filter_by(sub_category_id=sub_category_id).first() 
            if product.approved and product.suspend != True:
                return product
            else:
                return None
        except:
            session.rollback()


    @classmethod
    def read_products_based_on_sub_cat(cls, sub_category_id):
        try:
            return cls.query.filter_by(sub_category_id=sub_category_id).all()
        except:
            session.rollback()

    @classmethod
    def read_products_count(cls):
        try:
            return session.query(func.count(cls.product_id)).scalar()
        except:
            session.rollback()

    @classmethod  
    def home_products(cls):
        try:
            home_products = []
            home_products.append({"id":1,"title":"Favorite Food & Snacks", "products":sample(list(food_snacks_generator(cls.query.all())), 2)})
            home_products.append({"id":2,"title":"Drinks & Beverages", "products": sample(list(drinks_generator(cls.query.filter_by(sub_category_id=6).all())), 2) })

            return home_products

        except:
            session.rollback()




    @classmethod
    def read_all_products(cls, return_query=False, **kwargs):
        """
            if return_query is set to True, will return query object,
            otherwise returns list.
        """
        if return_query:
            try:
                return cls.query.filter_by(**kwargs).first()
            except:
                session.rollback()
        else:
            try:
                _date = datetime.now(ni_timezone)
                current_time = _date.astimezone(timezone)
                products_based_on_sub_cat_dict = {}
                product_based_on_sub_cat_list = []
                restaurant_products = [product for product in cls.query.filter_by(**kwargs).all()]

                for product in restaurant_products:
                    if product.resturant.approved:
                        _start_date = ni_timezone.localize(product.resturant.operation_start_time)
                        _end_date = ni_timezone.localize(product.resturant.operation_stop_time)
                        operation_start_time = _start_date.astimezone(timezone)
                        operation_stop_time = _end_date.astimezone(timezone)
                        if product.approved and product.suspend != True:
                            if f"{product.sub_category}" in products_based_on_sub_cat_dict:
                                if product not in products_based_on_sub_cat_dict[f"{product.sub_category}"]: #Avoid duplicates
                                    if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                                        pdt = product.serialize()
                                        pdt["available"] = True
                                        products_based_on_sub_cat_dict[f"{product.sub_category}"] += [pdt] #Add the product to this group
                                    else:
                                        products_based_on_sub_cat_dict[f"{product.sub_category}"] += [product.serialize()]
                            else:
                                if current_time.hour >= operation_start_time.hour and current_time.hour <= operation_stop_time.hour:
                                    pdt = product.serialize()
                                    pdt["available"] = True
                                    products_based_on_sub_cat_dict[f"{product.sub_category}"] = [pdt]
                                else:
                                    products_based_on_sub_cat_dict[f"{product.sub_category}"] = [product.serialize()]

                for sub_cat,products in products_based_on_sub_cat_dict.items():
                    banch = {"sub_category": sub_cat, "products": products}
                    product_based_on_sub_cat_list.append(banch)

                return product_based_on_sub_cat_list

            except:
                session.rollback()





        


