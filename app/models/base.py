from sqlalchemy import Column, DateTime
from uuid import uuid4
import datetime
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy_utils import UUIDType

Base = declarative_base()

class ModelBase(Base):
    __abstract__ = True

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    created_date = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
