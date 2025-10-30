from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.seat import Seat
from src.models.user import User
from src.utils.auth import get_current_user
from src.utils.qr_code import validate_qr_code

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
        db.query(User.full_name, Seat.code, Seat.is_half_price, Seat.status)
        .join(User, User.id == Seat.user_id)
        .filter(Seat.status.in_(["reserved", "occupied", "used"]))
        .all()
    )

    users_dict = {}
    for full_name, code, is_half_price, status in reserved_seats:
        if full_name not in users_dict:
            users_dict[full_name] = []
        users_dict[full_name].append(
            {"code": code, "is_half_price": is_half_price, "status": status}
        )

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


@router.post("/validate-qr-code")
async def validate_qr_code_entry(
    hash_value: str,
    seat_code: str,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    """
    Valida a entrada do evento e marca o assento como usado.

    Recebe o hash do QR code e o código do assento, valida o hash, verifica se o
    assento está em status 'occupied' e muda para 'used'.

    Args:
        hash_value: Hash contido no QR code
        seat_code: Código do assento
        db: Sessão do banco de dados
        authorization: Header de autorização

    Returns:
        Mensagem de sucesso com informações do assento

    Raises:
        HTTPException: Se não for admin, QR code inválido, assento não encontrado ou já usado
    """
    user = get_current_user(authorization)
    if "admin" not in user.get("scopes", ""):
        raise HTTPException(
            status_code=403, detail="User does not have admin privileges."
        )

    try:
        # Verifica se o assento existe
        seat = db.query(Seat).filter(Seat.code == seat_code).with_for_update().first()
        if not seat:
            raise HTTPException(status_code=404, detail=f"Seat not found: {seat_code}")

        if not seat.user_id:
            raise HTTPException(
                status_code=400,
                detail=f"Seat {seat_code} does not have an associated user.",
            )

        # Verifica se o assento está em status 'occupied'
        if seat.status != "occupied":
            raise HTTPException(
                status_code=400,
                detail=f"Seat {seat_code} must be in 'occupied' status to be validated.",
            )

        # Valida o QR code e atualiza o status para "used"
        try:
            validation_result = validate_qr_code(
                hash=hash_value,
                seat_code=seat_code,
                is_half_price=bool(seat.is_half_price),
                status="occupied",
                user_id=seat.user_id,
                db=db,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Busca informações do usuário
        user_info = None
        db_user = db.query(User).filter(User.id == seat.user_id).first()
        if db_user:
            user_info = {"name": db_user.full_name, "email": db_user.email}

        return {
            "message": "QR code validated successfully.",
            "seat_code": validation_result["seat_code"],
            "previous_status": validation_result["previous_status"],
            "new_status": validation_result["new_status"],
            "user_info": user_info,
            "is_half_price": validation_result["is_half_price"],
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
