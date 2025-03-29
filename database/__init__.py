from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
import os


class Base(DeclarativeBase):
    pass

try:
    db_url = os.getenv("DB_URL")
    if db_url is not None:
        engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=1800)
    else:
        engine = None
except KeyError:
    engine = None
