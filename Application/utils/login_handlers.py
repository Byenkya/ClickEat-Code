from functools import wraps
from Application.flask_imports import abort, current_user, redirect, url_for

def employee_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not getattr(current_user, "is_employee",None):
            abort(403)
        return func(*args, **kwargs)
    return decorated_view

def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not getattr(current_user, "account",None):
            abort(403)
        if getattr(current_user, "account") != "Administrator":
            abort(403)
        return func(*args, **kwargs)
    return decorated_view