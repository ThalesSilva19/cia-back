from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.seat import Seat
from src.models.transaction import Transaction
from src.routers.requests.seat import SeatRequest
from src.utils.auth import get_current_user

router = APIRouter(prefix="/seats")


@router.get("/")
async def get_seats(
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    _ = get_current_user(authorization)
    seats = db.query(Seat).all()
    # TODO: Add return type to return only the status and code
    return seats


@router.get("/user")
async def get_user_seats(
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    user = get_current_user(authorization)
    seats = db.query(Seat).filter(Seat.user_id == user["id"]).all()
    return seats


@router.post("/reserve")
async def reserve_seats(
    request: list[SeatRequest],
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    user = get_current_user(authorization)
    seat_map = {seat_req.seat_code: seat_req.is_half_price for seat_req in request}
    seat_codes = list(seat_map.keys())

    try:
        seats = db.query(Seat).filter(Seat.code.in_(seat_codes)).with_for_update().all()

        if len(seats) != len(seat_codes):
            found_codes = {seat.code for seat in seats}
            not_found = [code for code in seat_codes if code not in found_codes]
            raise HTTPException(
                status_code=404, detail=f"Seat(s) not found: {', '.join(not_found)}"
            )

        unavailable = [seat.code for seat in seats if seat.status != "available"]
        if unavailable:
            raise HTTPException(
                status_code=400,
                detail=f"Seats not available or already reserved: {', '.join(unavailable)}",
            )

        for seat in seats:
            seat.status = "reserved"
            seat.user_id = user["id"]
            seat.is_half_price = seat_map[seat.code]

        transaction = Transaction(
            seats=seat_codes,
            user_id=user["id"],
        )
        db.add(transaction)
        db.commit()
        return {"message": "Seats reserved successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error during reservation: {str(e)}"
        )
