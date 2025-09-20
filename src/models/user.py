import datetime

from sqlalchemy import Column, DateTime, Integer, String

from src.models.base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(11), index=True, nullable=False)
    password = Column(String(255), nullable=False)
    scopes = Column(String, nullable=False, server_default="default")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
