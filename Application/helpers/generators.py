import uuid
import jwt
from time import time

from jwt import ExpiredSignature
from Application.utils.lazy_loader import LazyLoader
from Application.flask_imports import _session

class ReferenceGenerator:
    def __init__(self, text=None):
        self.unique_id = self.generate_unique_reference() if text == None else text

    @classmethod
    def char_selection(cls, text, selection):
        try:
            return text[selection:]
        except Exception as e:
            print(e)
            raise

    def pattern1(self, value):
        return "ClickEat-{}-{}-{}-{}".format(
            value[0],
            value[1:4],
            value[4:7], 
            value[7:10]
        )

    @property
    def simple_version(self):
        return self.pattern1(self.char_selection(self.unique_id, -10))

    def unique_filename(self):
        return self.char_selection(self.unique_id, -10)

    def generate_unique_reference(self):
        ref = uuid.UUID(
            version=4,
            is_safe = uuid.SafeUUID.safe,
            fields = (
                uuid.uuid4().time_low,
                uuid.uuid4().time_mid, 
                uuid.uuid4().time_hi_version, 
                uuid.uuid4().clock_seq_hi_variant, 
                uuid.uuid4().clock_seq_low, 
                uuid.uuid4().node
            )
        )

        return str(ref.int)

def generate_tuple_list(*args):
    _list = []
    for item in args:
        _list.append((item, item))
    return _list


app_pkg = LazyLoader("Application")
mdl = LazyLoader("Application.database.models")
class TokenGenerator:
    def __init__(self, user=None):
        self.user = user

    def generate_api_token(self, expire_sec=3600):
        payload = dict(
            token_number=self.user.id,
            exp=time()+expire_sec
        )

        token = jwt.encode(
            payload = payload,
            key = app_pkg.app.config["SECRET_KEY"],
            algorithm="HS256"
        ).decode("utf-8")

        return token

    def verify_password_token(self,token):
        try:
            data = jwt.decode(
                jwt=token,
                key=app_pkg.app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
            user_type = data["user"]
            user_id = data["password_reset"]

            if user_type == 'customer':
                self.user = mdl.Customer.read_customer(id=user_id)
            elif user_type == 'clickeat_employee':
                self.user = mdl.StaffAccounts.read_user(id=user_id)
        except:
            self.user = None

    def verify_api_token(self, token):
        try:
            data = jwt.decode(
                jwt=token,
                key=app_pkg.app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
            user_id = data["token_number"]
            self.user = mdl.Customer.read_customer(id=user_id)
        except ExpiredSignature:
            try:
                data = jwt.decode(
                    jwt=token,
                    key=app_pkg.app.config["SECRET_KEY"],
                    algorithms=["HS256"],
                    verify=False,
                )
                user_id = data["token_number"]
                self.user = mdl.Customer.read_customer(id=user_id)
                _session["new_token"] = self.generate_api_token()
            except Exception:
                self.user = None
        except Exception as e:
            self.user = None
        return self.user
    
    def generate_password_reset_token(self,expire_sec=600):
        payload = dict(
            password_reset=self.user.id,
            user=self.user.__class__.__name__.lower(),
            exp=time()+expire_sec
        )
        token = jwt.encode(
            payload=payload,
            key=app_pkg.app.config["SECRET_KEY"],
            algorithm="HS256"
        ).decode("utf-8")
        return token
