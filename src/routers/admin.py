from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.seat import Seat
from src.models.user import User
from src.utils.auth import get_current_user

router = APIRouter(prefix="/admin")


@router.get("/pending-seats")
async def get_pending_seats(
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    user = get_current_user(authorization)
    if "admin" not in user.get("scopes", ""):
        raise HTTPException(
            status_code=403, detail="User does not have admin privileges."
        )

    reserved_seats = (
        db.query(User.full_name, Seat.code, Seat.is_half_price)
        .join(User, User.id == Seat.user_id)
        .filter(Seat.status == "reserved")
        .all()
    )

    users_dict = {}
    for full_name, code, is_half_price in reserved_seats:
        if full_name not in users_dict:
            users_dict[full_name] = []
        users_dict[full_name].append({"code": code, "is_half_price": is_half_price})

    result = [
        {"user_name": user_name, "seats": seats}
        for user_name, seats in users_dict.items()
    ]
    return result


@router.post("/approve-seat")
async def approve_seat(
    seat_code: str,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    user = get_current_user(authorization)
    if "admin" not in user.get("scopes", ""):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403, detail="User does not have admin privileges."
        )

    try:
        seat = db.query(Seat).filter(Seat.code == seat_code).with_for_update().first()
        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found.")

        seat.status = "occupied"
        db.commit()
        return {"message": "Seat occupied successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/reprove-seat")
async def reprove_seat(
    seat_code: str,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    user = get_current_user(authorization)
    if "admin" not in user.get("scopes", ""):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403, detail="User does not have admin privileges."
        )

    try:
        seat = db.query(Seat).filter(Seat.code == seat_code).with_for_update().first()
        if not seat:
            raise HTTPException(status_code=404, detail="Seat not found.")

        seat.status = "available"
        seat.user_id = None
        db.commit()
        return {"message": "Seat approved successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
