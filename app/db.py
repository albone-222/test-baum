from sqlalchemy.engine import create_engine
# from sqlalchemy import sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .schemas import settings


class Base(DeclarativeBase):
    pass

engine = create_engine(str(settings.db.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
