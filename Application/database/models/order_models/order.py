from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, Integer, String, Boolean, BigInteger, DateTime, 
    ForeignKey, relationship, func, lazyload, desc, and_
)
from Application.flask_imports import current_app, flash, abort, jsonify
from Application.utils import LazyLoader
from Application.utils.email import order_cancelled_email, order_placed_email, order_receipt_email, customer_care_email
from Application.helpers import ReferenceGenerator

from datetime import datetime

#lazy laoding of dependencies
customer = LazyLoader("Application.database.models.customer_models.customer")
customer_addresses = LazyLoader("Application.database.models.customer_models.customer_addresses")
pym = LazyLoader("Application.database.models.payment_models")
pdts = LazyLoader("Application.database.models.product_models")
delivery_detials = LazyLoader("Application.database.models.order_models.delivery_details")
sales = LazyLoader("Application.database.models.product_models.sales")
cart = LazyLoader("Application.database.models.product_models.cart")


#click_mysql_password = 5FJc_?]-JSCsOMfDCcU1xhJGTsiSN^pr

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True)   
    order_ref = Column(String(50), unique=True, nullable=False)
    order_ref_simple_version = Column(String(50), unique=True,nullable=False)
    order_date = Column(DateTime, default=datetime.now(), nullable=False)
    delivery_contact = Column(String(13), unique=False, nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)
    is_prepared = Column(Boolean, default=False, nullable=False)
    is_terminated = Column(Boolean, default=False, nullable=False)
    termination_reason = Column(String(500))
    customer_received = Column(Boolean, default=False, nullable=False)
    delivery_fee = Column(BigInteger, default=0)
    customer_id = Column(Integer, ForeignKey("customer.id"), index=True, nullable=False)
    customer = relationship("Customer", backref="orders")
    pre_order = Column(Boolean, default=False, nullable=False)
    pre_order_time = Column(DateTime, default=datetime(2021,1,30,00,00,00), nullable=False)

    def __repr__(self):
        return self.order_ref_simple_version

    def __call__(self, **kwargs):
        try:
            self.order_ref = kwargs.get("order_ref")
            self.customer_id = kwargs.get("customer_id")
            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error whilst adding order record: ", e)
            session.rollback()
            return False

    def serialize(self):
        return {
            "id": self.id,
            "order_ref": self.order_ref,
            "order_ref_simple_version": self.order_ref_simple_version,
            "order_date": self.order_date.strftime('%m/%d/%Y'),
            "is_paid": self.is_paid,
            "is_prepared": self.is_prepared,
            "is_terminated": self.is_terminated,
            "termination_reason": self.termination_reason,
            "customer_received": self.customer_received,
            "delivery_fee": self.delivery_fee,
            "order_items": [item.serialize() for item in self.cart]
        }

    @property
    def delivery_address(self):
        try:
            return delivery_detials.DeliveryDetails.get_order_delivery_address(self.id)
        except:
            session.rollback()
    @property
    def read_order_total_amount(self):
        return cart.Cart.customer_order_items_total(self.id)

    @classmethod
    def customer_order_count(cls, customer_id):
        try:
            count = session.query(func.count(cls.id)).filter_by(
                is_paid = True,
                is_terminated = False
            ).scalar()

            return count
        except:
            session.rollback()

    @classmethod
    def read_order(cls, **kwargs):
        try:
            return cls.query.filter_by(**kwargs).options(lazyload("*")).first()
        except:
            session.rollback()

    @classmethod
    def read_customer_orders(cls, customer_id):
        try:
            customer_orders = cls.query.filter_by(customer_id=customer_id).order_by(desc(cls.order_date)).all()
            return [item.serialize() for item in customer_orders]

        except:
            session.rollback()


    @classmethod
    def customer_order_exists(cls, customer_id):
        try:
            return session.query(cls).filter_by(customer_id=customer_id,is_paid=False,is_terminated=False).first()
        except:
            session.rollback()
        

    @classmethod
    def delete_order(self, id):
        try:
            self.query.filter_by(id=id).delete()
            session.commit()
        except:
            session.rollback()

    @classmethod
    def read_orders_count(cls):
        try:
            return session.query(func.count(cls.id)).filter_by(is_paid=False,is_terminated=False).scalar()
        except:
            session.rollback()

    @classmethod
    def read_all_orders(cls):
        try:
            return cls.query.order_by(Order.id.desc())
        except:
            session.rollback()

    @property
    def read_cart_items_total_amount(self):
        try:
            return pdts.Cart.customer_order_items_total(self.id)
        except:
            session.rollback()

    @classmethod
    def read_all_orders_filter(cls, *args):
        try:
            return cls.query.filter(
                *args
            ).order_by(Order.id.desc()).all()
        except:
            session.rollback()

    @classmethod
    def read_all_orders_delivery_details_filter(cls, *args):
        try:
            return session.query(cls).join(cls.delivery_details)\
                .filter(
                    *args
                ).order_by(cls.id.desc()).options(
                    lazyload("*")).all()
        except:
            session.rollback()

    @classmethod
    def read_orders_not_prepared_count(cls):
        try:
            return session.query(func.count(cls.id))\
                .filter(
                    and_(
                        cls.is_prepared==False,
                        cls.is_terminated == False
                        )
                    ).scalar()
        except:
            session.rollback()


    def customer_care_terminate_order(self, reason):
        try:
            self.is_terminated = True
            self.termination_reason = reason
            cash_on_delivery = pym.CashOnDelivery.read_cash_on_delivery(payment_id=self.payment[0].payment_id)

            if cash_on_delivery:
                cash_on_delivery.status = "cancelled"

            if self.customer.email:
                mail_ = order_cancelled_email
                mail_.recipients = [self.customer.email]
                mail_.text = "We have cancelled the following order:{order}, because of the following reason: \n{reason}".format(order=self.order_ref_simple_version, reason=reason)
                mail_.send()
                session.commit()
                return True
                
            else:
                session.commit()
                return True
        except Exception as e:
            session.rollback()
            print("Terminating order error: ", e)
            return False

    @classmethod
    def terminate_order(cls, **kwargs):
        try:
            order = cls.read_order(
                customer_id=kwargs.get("customer_id"),
                is_paid=False,
                is_prepared=False,
                is_terminated=False,
                customer_received=False
            )

            if order:
                order.is_terminated = True
                order.termination_reason = kwargs.get("reason")
                cash_on_delivery = pym.CashOnDelivery.read_cash_on_delivery(payment_id=order.payment[0].payment_id)

                if cash_on_delivery:
                    cash_on_delivery.status = "cancelled"

                if order.customer.email:
                    mail_ = order_cancelled_email
                    mail_.recipients = [order.customer.email]
                    mail_.text = "You have cancelled the following order:{order}, because of this reason: \n{reason}".format(order=order.order_ref_simple_version, reason=kwargs.get("reason"))
                    mail_.send()
                    session.commit()
                    return True
                    
                else:
                    session.commit()
                    return True
            else:
                return False

        except Exception as e:
            print("Terminating order error: ", e)
            session.rollback()
            return False  

    @classmethod
    def place_customer_order(cls, **kwargs):
        with current_app.app_context():
            try:
                method = kwargs.get("payment_method")
                customer_id = kwargs.get("customer_id")
                delivery_contact = kwargs.get("delivery_contact")
                delivery_fee = kwargs.get("delivery_fee")
                pre_order = kwargs.get("pre_order")
                pre_order_time = kwargs.get("pre_order_time")
                county=kwargs.get("county"),
                sub_county=kwargs.get("sub_county"),
                village=kwargs.get("village"),
                other_details=kwargs.get("other_details"),
                customer_object = customer.Customer.read_customer(id=customer_id)
                payment_method = pym.PaymentMethods.read_method(method=method)

                if payment_method:
                    new_ref = ReferenceGenerator()
                    order_ref = new_ref.unique_id
                    order_ref_simple_version = new_ref.simple_version

                    order_ = Order(
                                    order_ref=order_ref,
                                    order_ref_simple_version=order_ref_simple_version,
                                    delivery_contact=delivery_contact,
                                    delivery_fee=delivery_fee,
                                    customer_id=customer_id,
                                    pre_order=pre_order,
                                    pre_order_time=pre_order_time
                                )

                    items = session.query(pdts.Cart).filter_by(customer_id=customer_id, is_ordered=False).all()

                    for item in items:
                        item.is_ordered = True  
                        item.order = order_

                    delivery = delivery_detials.DeliveryDetails(
                        county=county,
                        sub_county=sub_county,
                        village=village,
                        other_details=other_details,
                        customer_id=customer_id,
                        order=order_
                    )
                    session.add(delivery)

                    payment = pym.Payment(
                        payment_method_id = payment_method.id,
                        order = order_
                    )

                    session.add(payment)   
                    if payment_method.method == "Cash on delivery":
                        cash_on_delivery = pym.CashOnDelivery(payment=payment, transaction_ref=order_ref, status="pending")
                        session.add(cash_on_delivery)
                    
                    else:
                        session.rollback()  
                        return False

                    #customer_care email
                    cart_items_total = []
                    items_str = ""
                    item_string = ""
                    for i in items:
                        item = i.serialize()
                        item_string = f"<li>Item: {item['product_name']} from {item['restaurant']} Quantity: {item['quantity']} <b>SubTotal: {'{:,} Ugx'.format(item['total'])}</b></li>"
                        items_str+=item_string
                        cart_items_total.append(item['total'])
                    total = items[0].serialize()
                    items_total = sum(cart_items_total)
                    subject_customer_care = """
                                            <html>
                                                <p>The following customer: <b>{customer_name}</b> has placed an order with the following details:</p>
                                                <p>Order Reference: {order_ref}</p>
                                                <p>Order Date: {order_date}</p>
                                                <p>Contact: {contact}</p>
                                                <hr>
                                                <ul style='list-style-type: none;display: block;width: 100%;padding: 0px 10px;overflow: hidden;'>    
                                                    {items_str}
                                                </ul>
                                                <hr>
                                                <p>Items Total: {total}</p>
                                                <hr>
                                        
                                                <p>Payment Method: <b>{payment_method}</b></p>
                                                <p>Delivery Price: <b>{delivery_fee}</b></p>
                                                <p>Total: <b>{order_total}</b></p>
                                                <hr>
                                                <p>Delivery Address: {delivery_address}</p>
                                            </html>
                    """.format(
                                        customer_name=customer_object.name,
                                        order_ref=order_ref_simple_version, 
                                        order_date="{: %d/%m/%Y}".format(datetime.now()),
                                        contact=customer_object.contact,
                                        items_str=items_str,
                                        total='{:,} Ugx'.format(items_total),
                                        payment_method=payment_method.method,
                                        delivery_fee='{:,} Ugx'.format(delivery_fee),
                                        order_total='{:,} Ugx'.format(delivery_fee+items_total),
                                        delivery_address=f"<br>County: {county}<br>,Sub County: {sub_county}<br>,Village: {village}<br>,Other_details: {other_details}<br>"
                    )
                    customer_care_mail_ = customer_care_email
                    customer_care_mail_.recipients = ["tayebwaian0@gmail.com", "willbrodmutesi@gmail.com", "imutyaba11@gmail.com"]
                    # customer_care_mail_.context = dict(
                    #     customer_name=customer_object.name,
                    #     customer_contact=customer_object.contact,
                    #     order_ref=order_ref_simple_version,
                    #     order_date="{: %d/%m/%Y}".format(datetime.now()),
                    #     items=[i.serialize() for i in items],
                    #     delivery_method="Home delivery",
                    #     delivery_fee=delivery_fee,
                    #     payment_method=payment_method.method,
                    #     delivery_address= f"County: {county}\n,Sub County: {sub_county}\n,Village: {village}\n,Other_details: {other_details}"
                    # )
                    customer_care_mail_.text = subject_customer_care
                    customer_care_mail_.send()

                    if customer_object.email:
                        subject_customer = """
                                        <html>
                                            <p>Written by: customercare.clickeat@gmail.com<br>
                                                <b>Office Address:</b><br>
                                                Afra Road,<br>
                                                Near Hindu Temple,<br>
                                                Room 08,<br>
                                                Arua City, Uganda.
                                            </p>
                                            <p>You have successfully made an order for the following items.</p>
                                            <p>Order Reference: <b>{order_ref}</b></p>
                                            <p>Order Date: <b>{order_date}</b></p>
                                            <hr>
                                            <ul style='list-style-type: none;display: block;width: 100%;padding: 0px 10px;overflow: hidden;'>
                                                {items_str}
                                            </ul>
                                            <hr>
                                            <p>Items Total: <b>{total}</b></p>
                                            <hr>
                                            <p>Payment Method: <b>{payment_method}</b></p>
                                            <p>Delivery Price: <b>{delivery_fee}</b></p>
                                            <p>Total: <b>{order_total}</b></p>
                                            <p>Delivery Address: {delivery_address}</p>
                                            <hr>
                                            <p>You have received this email because you are a registered customer of ClickEat.</p>
                                            <p>For any help please contact us on: <b>0785857000/0777758880</b></p>
                                        </html>
                        """.format(
                                        order_ref=order_ref_simple_version, 
                                        order_date="{: %d/%m/%Y}".format(datetime.now()),
                                        items_str=items_str,
                                        total='{:,} Ugx'.format(items_total),
                                        payment_method=payment_method.method,
                                        delivery_fee='{:,} Ugx'.format(delivery_fee),
                                        order_total='{:,} Ugx'.format(delivery_fee+items_total),
                                        delivery_address=f"<br>County: {county}<br>,Sub County: {sub_county}<br>,Village: {village}<br>,Other_details: {other_details}<br>"
                        )
                        mail_ = order_placed_email
                        mail_.recipients = [customer_object.email]
                        mail_.text = subject_customer
                        # mail_.context = dict(
                        #     customer_name=customer_object.name,
                        #     customer_contact=customer_object.contact,
                        #     order_ref=order_ref_simple_version,
                        #     order_date="{: %d/%m/%Y}".format(datetime.now()),
                        #     items=[i.serialize() for i in items],
                        #     delivery_method="Home delivery",
                        #     delivery_fee=delivery_fee,
                        #     payment_method=payment_method.method,
                        #     delivery_address= f"County: {county}\n,Sub County: {sub_county}\n,Village: {village}\n,Other_details: {other_details}"
                        # )
                        # mail_.text = "You have placed the following order with reference number: {order_ref_simple_version}".format(
                        #     order_ref_simple_version=order_ref_simple_version
                        # )
                        mail_.send()
                        session.commit()
                        return True
                    
                    else:
                        session.commit()
                        return True

                else:
                    print("No payment method")
                    return False
                        
            except Exception as e:
                print("Placing Order Error: ", e)
                session.rollback()
                return False


    @classmethod
    def customer_care_register_order_sales(cls, **kwargs):
        with current_app.app_context():
            try:
                order =  kwargs.get("order")
                data  = kwargs.get("data")

                if "order_id" not in data:
                        abort(403)
                if int(data["order_id"]) != int(order.id):
                    abort(403)

                if "customer_received" in data:
                    if order.is_prepared == False:
                        flash("Order has to first be prepared", "danger")
                        return jsonify()
                    if order.is_paid == False:
                        flash("Order has to first be paid", "danger")
                        return jsonify()
                    if data["customer_received"] == True and order.customer_received == False:
                        order.customer_received = True
                        session.commit()
                        flash("Order status 'Customer received' has been set", "success")
                    else:
                        flash("Order status 'Customer received' was already set","info")

                elif "is_prepared" in data:
                    if data["is_prepared"] == True and order.is_prepared == False:
                        order.is_prepared = True
                        session.commit()
                        flash("Order status 'Prepared' has been set", "success")
                    else:
                        flash("Order status 'Prepared' was already set", "info")   

                elif "courier_id" in data:
                    if order.is_prepared == False:
                        flash("Order has to be first prepared", "danger")
                        return jsonify()
                    delivery_detials.DeliveryDetails.assign_courier(int(data["courier_id"]),int(order.id))
                    flash("Courier has been set for this order successfully", "success") 

                elif "is_paid" in data:
                    if order.is_prepared == False:
                        flash("Order has to first  be prepared", "danger")
                        return jsonify()
                    if data["is_paid"] == True and order.is_paid == False:
                        order.is_paid = True
                        cash_on_delivery = pym.CashOnDelivery.read_cash_on_delivery(payment_id=order.payment[0].payment_id)
                        delivery_details = order.delivery_details[0]
                        if delivery_details.courier_id == None:
                            flash("Order paid can only be set when courier has been set.", "danger")
                            session.rollback()
                            return jsonify()
                        if not cash_on_delivery:
                            flash("Order paid can only be set for cash on delivery items.", "danger")
                            session.rollback()
                            return jsonify()
                        else:
                            cash_on_delivery.status = "confirmed"
                        for pdt_ in order.cart:
                            product = session.query(pdts.Products).filter_by(product_id=pdt_.product_id).first()
                            if product:
                                sales.Sales()(
                                    product_id=pdt_.product_id,
                                    quantity=pdt_.quantity,
                                    amount=pdt_.total,
                                    commission_amount=product.commission_amount if product.commission_amount else 0
                                    )
                        if order.customer.email:
                            items = order.cart
                            cart_items_total = []
                            items_str = ""
                            item_string = ""
                            for i in items:
                                item = i.serialize()
                                item_string = f"<li>Item: {item['product_name']} from {item['restaurant']} Quantity: {item['quantity']} <b>SubTotal: {'{:,} Ugx'.format(item['total'])}</b></li>"
                                items_str+=item_string
                                cart_items_total.append(item['total'])
                            total = items[0].serialize()
                            items_total = sum(cart_items_total)
                            subject_customer = """
                                        <html>
                                            <p>Written by customercare.clickeat@gmail.com<br>
                                                Office Address:<br>
                                                Afra Road,<br>
                                                Near Hindu Temple,<br>
                                                Room 08,<br>
                                                Arua City, Uganda.
                                            </p>
                                            <p>Dear <b>{user_name}</b></p>,
                                            <p>You have made a payment for the following items.</p>
                                            <p>Order Reference: <b>{order_ref}</b></p>
                                            <p>Order Date: {order_date}</p>
                                            <hr>
                                            <ul style='list-style-type: none;display: block;width: 100%;padding: 0px 10px;overflow: hidden;'>
                                                {items_str}
                                            </ul>
                                            <hr>
                                            <p>Items Total: <b>{total}</b></p>
                                            <p>Payment Method: {payment_method}</p>
                                            <p>Delivery Price: {delivery_fee}</p>
                                            <p>Total: {order_total}</p>
                                            <p>Status: <b>Paid</b></p>
                                            <hr>

                                            <p><b>Thank you for buying on ClickEat, please come gain :)</b></p>
                                            <p>You have received this email because you are a member of ClickEat.</p>
                                            <p>For any help please contact us by clicking 0785857000/0777758880</p>
                                        </html>
                            """.format(
                                            user_name=order.customer.name,
                                            order_ref=order.order_ref_simple_version, 
                                            order_date="{: %d/%m/%Y}".format(order.order_date),
                                            items_str=items_str,
                                            total='{:,} Ugx'.format(items_total),
                                            payment_method=order.payment[0].payment_method.serialize(),
                                            delivery_fee='{:,} Ugx'.format(order.delivery_fee),
                                            order_total='{:,} Ugx'.format(order.delivery_fee+items_total)
                            )
                            mail_  = order_receipt_email
                            mail_.recipients = [order.customer.email]
                            mail_.text = subject_customer
                            # mail_.context = dict(
                            #     items = [i.serialize() for i in order.cart],
                            #     order_ref = order.order_ref_simple_version,
                            #     order_date="{: %d/%m/%Y}".format(order.order_date),
                            #     user_name = order.customer.name,
                            #     delivery_fees = order.delivery_fee,
                            #     payment_method = order.payment[0].payment_method.serialize(),
                            #     customer_received = order.customer_received
                            # )
                            mail_.send()
                            session.commit()
                            flash("Order status has been set to paid", "success")

                        else:
                            session.commit()
                            flash("Order status has been set to paid", "success")
                    else:
                        session.rollback()
                        flash("Order status already set to paid", "info")        
            except Exception as e:
                session.rollback()
                print("Updating Order statuses error: ",e)
                flash(f"Error: {e}","danger")


                
        
