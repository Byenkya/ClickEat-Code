from Application.database.initialize_database import Base, session
from Application.database.sqlalchemy_imports import (
    Column, String, Integer, ForeignKey, relationship, DateTime, desc
)
from datetime import datetime

class Comments(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True)
    comment = Column(String(500), nullable=False)
    date = Column(DateTime, default=datetime.now(), nullable=False)
    reply = Column(String(500))
    customer_id = Column(Integer, ForeignKey("customer.id"), index=True, nullable=False)
    customer = relationship("Customer", backref="comments")
    product_id = Column(Integer, ForeignKey("products.product_id"), index=True, nullable=False)
    products = relationship("Products", backref="comments")

    def __repr__(self):
        return str(self.id)

    def __call__(self, **kwargs):
        try:
            self.comment = kwargs.get("comment")
            self.customer_id = kwargs.get("customer_id")
            self.product_id = kwargs.get("product_id")
            session.add(self)
            session.commit()
            return True

        except Exception as e:
            print("Error whilst adding comment: ", e)
            session.rollback()
            return False

    def serialize(self):
        return {
            "product_id": self.product_id,
            "comment": self.comment,
            "date": self.date.strftime('%m/%d/%Y'),
            "reply": self.reply,
            "customerNames": self.customer.name
        }

    @classmethod
    def get_product_comments(cls, product_id):
        try:
            comments = cls.query.filter_by(product_id=product_id).order_by(desc(cls.date)).all()
            pdt_comments = (comment.serialize() for comment in comments)

            return pdt_comments
        except:
            session.rollback()

    @classmethod
    def product_comments(cls, product_id):
        try:
            comments = cls.query.filter_by(product_id=product_id).order_by(desc(cls.date)).all()

            return comments
        except:
            session.rollback()

        

















































