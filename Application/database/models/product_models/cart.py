from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, String, Integer, BigInteger, Integer, DateTime, ForeignKey,
    relationship, Boolean, func, hybrid_property
) 
from Application.utils import LazyLoader
from datetime import datetime
from Application.flask_imports import Markup

#lazy loading dependency modules
shp = LazyLoader("Application.database.models.business_models")
pdts = LazyLoader("Application.database.models.product_models.products")

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    product_image = Column(String(50), nullable=False)
    product_name = Column(String(50), nullable=False)
    quantity = Column(BigInteger, nullable=False)
    unit_price = Column(BigInteger, nullable=False)
    commision_amount = Column(BigInteger, nullable=True)
    served_with = Column(String(1000), nullable=False, default="none")
    date = Column(DateTime, default=datetime.now(), nullable=False)
    is_ordered = Column(Boolean, default=False, nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.id"), index=True, nullable=False)
    customer = relationship("Customer", backref="cart")
    order_id = Column(Integer, ForeignKey("order.id"), index=True)
    order = relationship("Order", backref="cart")
    free_delivery = Column(Boolean, nullable=False, default=False)
    restaurant = Column(String(100), nullable=False, default="clickEat")

    def __repr__(self):
        return self.product_name

    def __call__(self, **kwargs):
        try:
            self.product_id = kwargs.get("product_id")
            self.customer_id = kwargs.get("customer_id")
            self.product_name = kwargs.get("product_name")
            self.product_image = kwargs.get("product_image")
            self.unit_price = kwargs.get("unit_price")
            self.quantity = kwargs.get("quantity")
            self.served_with = kwargs.get("served_with", "none")
            self.free_delivery = kwargs.get("free_delivery", False)
            self.restaurant = kwargs.get("restaurant", "clickEat")
            item_exists = self.query.filter_by(
                customer_id = self.customer_id,
                product_id = self.product_id,
                is_ordered = False
            ).first()
            if item_exists:
                item_exists.quantity += int(self.quantity)
                session.commit()
                # if item_exists.quantity > product.quantity:
                #     session.rollback()
                #     print("Product already exists on cart and quantity you are specifying is more than what is available.")
                #     return False
                # else:
                #     session.commit()
            else:
                session.add(self)
                session.commit()

            return True

        except Exception as e:
            print("Error While adding to Cart: ", e)
            session.rollback()
            return False

    def serialize(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_image": self.product_image,
            "unit_price": self.unit_price,
            "quantity": self.quantity,
            "served_with": self.served_with,
            "total": self.total,
            "total_quantity": int(self.cart_total_quantity_or_item_count(self.customer_id)),
            "cart_total_amount": int(self.cart_total_amount(self.customer_id)),
            "free_delivery": self.free_delivery,
            "restaurant": self.restaurant
        }

    @hybrid_property
    def total(self):
        return self.quantity * self.unit_price
        
    @classmethod
    def customer_order_items_total(cls, order_id):
        total = session.query(func.sum(cls.total))\
            .filter_by(
                order_id=order_id
                ).scalar()
        return total if total else 0

    @classmethod
    def read_customer_cart_items(cls, customer_id):
        try:
            cart_items = cls.query.filter_by(
                customer_id=customer_id,
                is_ordered=False
            ).all()

            return cls.update_cart_items_prices(cart_items)
        except:
            session.rollback()

    @classmethod
    def update_cart_items_prices(cls, cart_items):
        try:
            for item in cart_items:
                product = pdts.Products.read_all_products(return_query=True, product_id=item.product_id)
                if product.promotional_price_set:
                    if product.promotional_price:
                        item.unit_price = product.promotional_price
                    else:
                        item.unit_price = product.price
                else:
                    item.unit_price = product.price
            session.commit()

            customer_cart_items = {"cart_items": [cart_item.serialize() for cart_item in cart_items]}

            return customer_cart_items
        except:
            session.rollback()

    @classmethod
    def update_cart_item(cls, **kwargs):
        item = cls.query.filter_by(
                customer_id = kwargs.get("customer_id"),
                product_id = kwargs.get("product_id"),
                is_ordered = False
            ).first()

        if item:
            item.quantity = kwargs.get("quantity")
            session.commit()

            return cls.read_customer_cart_items(kwargs.get("customer_id"))

        else:
            return False


    @classmethod
    def cart_total_quantity_or_item_count(cls, customer_id):
        total = session.query(func.sum(cls.quantity))\
            .filter_by(
                customer_id=customer_id,
                is_ordered=False
            ).scalar()
        
        return total if total else 0

    @classmethod
    def cart_total_amount(cls, customer_id):
        total = session.query(func.sum(cls.total))\
            .filter_by(
                customer_id=customer_id,
                is_ordered=False
            ).scalar()
        
        return total if total else 0

    @classmethod
    def customer_order_items_total(cls, order_id):
        total = session.query(func.sum(cls.total))\
            .filter_by(
                order_id=order_id
                ).scalar()
        return total if total else 0

    @property
    def read_item_shop_details(self):
        shop_details = session.query(shp.Resturant.business_name, shp.Resturant.address, shp.Resturant.contact, shp.Resturant.second_contact).join(
            "products"
        ).filter(pdts.Products.product_id == self.product_id).first()
        shop_details = Markup(f"{shop_details[0]}.<br> <b>Location:</b> {shop_details[1]} <br><b>Contact: </b>{shop_details[2]}/ {shop_details[3]}") if shop_details else "Unkown"
        return shop_details


    @classmethod 
    def delete_cart_item(cls, id):
        try:
            product = cls.query.filter_by(product_id=id).first()
            cls.query.filter_by(product_id=id).delete()
            session.commit()
            return cls.read_customer_cart_items(product.customer_id)

        except Exception as e:
            print("Error whilst deleting cart item!!.", e)
            session.rollback()
            return False

































