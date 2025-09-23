import datetime
import secrets

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from src.models.base import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(String(10), nullable=False, default="false")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    @staticmethod
    def generate_token() -> str:
        """Gera um token seguro para recuperação de senha"""
        return secrets.token_urlsafe(32)
