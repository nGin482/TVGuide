from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
import os


class Base(DeclarativeBase):
    pass

engine = create_engine(os.getenv('DB_URL'))