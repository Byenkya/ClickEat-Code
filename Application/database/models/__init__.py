from Application.flask_imports import _session
from Application.database.sqlalchemy_imports import event

from .business_models import *
from .customer_models import *
from .click_eat_models import *
from .order_models import *
from .product_models import *
from .payment_models import *

def load_user(user_id):
    if _session.get("account_type") == "administrator":
        return StaffAccounts.query.get(user_id)
    
    elif _session.get("account_type") == "Employee":
        return StaffAccounts.query.get(user_id)
