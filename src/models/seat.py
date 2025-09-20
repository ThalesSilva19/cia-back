import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from src.models.base import Base


class Seat(Base):
    __tablename__ = "seat"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    code = Column(String(3), unique=True, index=True, nullable=False)
    status = Column(String(20), nullable=False, default="available")
    is_half_price = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
