from Application import celery, session
from Application.database.models import ProductDiscounts
from Application.database.models import Products
from datetime import datetime

class PromotionalPricesTasks:
    @classmethod
    @celery.task
    def check_promotional_prices(cls):
        start = datetime.now()
        product_discounts = ProductDiscounts.read_all()
        for product_discount in product_discounts:
            cls. parse_discount(product_discount)
        stop = datetime.now()
        
        time_taken = start - stop

        print("Ended checking promotional prices, time:",time_taken)

    @classmethod
    def parse_discount(cls, product_discount):
        current_date = datetime.now()
        if product_discount.to_date < current_date:
            ProductDiscounts.remove_promotion_price(product_discount.product_id)
