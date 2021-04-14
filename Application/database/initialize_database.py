from passlib.context import CryptContext
from .sqlalchemy_imports import (declarative_base, scoped_session, sessionmaker, create_engine)
from Application import app

pwd_context = CryptContext(  
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000  
)


path = app.config.get("DATABASE_URI")
engine = create_engine(path, pool_recycle=3600, isolation_level="READ COMMITTED")
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = session.query_property()