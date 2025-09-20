from sqlalchemy import ARRAY, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from src.models.base import Base


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    seats = Column(ARRAY(String(3)), nullable=False)
    user_id = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
