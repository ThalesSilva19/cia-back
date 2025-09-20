from datetime import datetime, timedelta

import jwt

from src.models.user import User
from src.settings import settings


def create_access_token(user: User) -> str:
    payload = {
        "id": user.id,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "email": user.email,
        "scopes": user.scopes,
        "exp": datetime.utcnow() + timedelta(hours=6),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado")
    except jwt.InvalidTokenError:
        raise ValueError("Token invalido")
