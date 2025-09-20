from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.base import Base
from src.models.seat import Seat
from src.models.transaction import Transaction
from src.models.user import User
from src.settings import settings

# Create engine using settings
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Import all models to ensure they are registered with Base.metadata
__all__ = ["Base", "User", "Seat", "Transaction"]
