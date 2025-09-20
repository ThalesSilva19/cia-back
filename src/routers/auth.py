from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.routers.requests.login import LoginRequest
from src.routers.requests.register import RegisterRequest
from src.routers.responses.auth import AuthResponse
from src.utils.hash import check_password_hash, hash_password
from src.utils.jwt import create_access_token

router = APIRouter()


@router.post("/login")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not check_password_hash(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(user)
    return AuthResponse(access_token=access_token)


@router.post("/register")
async def register(
    request: RegisterRequest, db: Session = Depends(get_db)
) -> AuthResponse:
    user = User(
        full_name=request.full_name,
        email=request.email,
        password=hash_password(request.password),
        phone_number=request.phone_number,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token = create_access_token(user)
    return AuthResponse(access_token=access_token)
