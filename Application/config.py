import os 

class BaseConfig:
    """ Base config class """
    DEBUG = True
    TESTING = False
    DATABASE_USER = os.environ["DATABASE_USER"]
    DATABASE_USER_PASSWORD = os.environ["DATABASE_USER_PASSWORD"]
    DATABASE_ADDRESS = os.environ["DATABASE_ADDRESS"]
    DATABASE_NAME = os.environ["DATABASE_NAME"]
    SQLALCHEMY_CONNECTOR = "mysql+pymysql://"
    DATABASE_URI = SQLALCHEMY_CONNECTOR+DATABASE_USER+":"+DATABASE_USER_PASSWORD+"@"+DATABASE_ADDRESS+"/"+DATABASE_NAME+"?charset=utf8mb4"
    # DATABASE_URI = 'sqlite:///database.db'
    FLASK_ADMIN_SWATCH = "slate"
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587   
    MAIL_USE_SSL =  False
    MAIL_USE_TLS = True
    MAIL_ASCII_ATTACHMENTS = True
    MAIL_DEFAULT_SENDER = os.environ["MAIL_DEFAULT_SENDER"]
    MAIL_USERNAME = os.environ["MAIL_USERNAME"]
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    # SERVER_NAME = "127.0.0.1:5000"
    # UPLOADED_RESTURANT_PICS = "Application/database/media/"

class ProductionConfig(BaseConfig):
    """ Production specific config """
    DEBUG = False
    TESTING = False
    SECRET_KEY = open("./Application/keys/app_secret_key.key").read()

class DevelopmentConfig(BaseConfig):
    """ Development environment specific config """
    TESTING = False
    SECRET_KEY = 'kdflkdnljdkdfdo28erbqu9fbiqie9wblkjalioe'


class CeleryConfig:
    broker_url = 'redis://localhost:6379/0'
    timezone = "Africa/Kampala"
    result_backend = 'redis://localhost:6379/0'
    accept_content = ["json", "pickle"]




