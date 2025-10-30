from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.seat import Seat
from src.models.user import User
from src.utils.auth import get_current_user
from src.utils.qr_code import decode_qr_data, validate_qr_code

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
    qr_code_string: str,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    """
    Valida um QR code na entrada do evento e marca o assento como usado.

    Recebe o QR code escaneado, valida o hash, verifica se o assento está 'occupied'
    e o muda para 'used'.

    Args:
        qr_code_string: String contendo os dados do QR code (JSON ou dict string)
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
        # Decodifica os dados do QR code
        qr_data = decode_qr_data(qr_code_string)
        if not qr_data:
            raise HTTPException(status_code=400, detail="Invalid QR code format.")

        # Valida o hash do QR code
        if not validate_qr_code(qr_data):
            raise HTTPException(
                status_code=400, detail="Invalid QR code - hash verification failed."
            )

        seat_code = qr_data.get("seat_code")
        status_from_qr = qr_data.get("status")
        is_half_price_from_qr = qr_data.get("is_half_price", False)

        # Verifica se o assento existe
        seat = db.query(Seat).filter(Seat.code == seat_code).with_for_update().first()
        if not seat:
            raise HTTPException(status_code=404, detail=f"Seat not found: {seat_code}")

        # Verifica se o assento está no status correto (occupied)
        if seat.status != "occupied":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot validate seat with status '{seat.status}'. Expected 'occupied'.",
            )

        # Verifica se o status do QR code é 'occupied'
        if status_from_qr != "occupied":
            raise HTTPException(
                status_code=400,
                detail=f"QR code status is '{status_from_qr}'. Expected 'occupied'.",
            )

        # Verifica se o tipo de ingresso do QR code corresponde ao do banco
        if seat.is_half_price != is_half_price_from_qr:
            raise HTTPException(
                status_code=400,
                detail=f"QR code ticket type mismatch. Expected '{'Meia' if seat.is_half_price else 'Inteira'}', got '{'Meia' if is_half_price_from_qr else 'Inteira'}'.",
            )

        # Atualiza o assento para 'used'
        seat.status = "used"
        db.commit()

        # Busca informações do usuário se existir
        user_info = None
        if seat.user_id:
            db_user = db.query(User).filter(User.id == seat.user_id).first()
            if db_user:
                user_info = {"name": db_user.full_name, "email": db_user.email}

        return {
            "message": "QR code validated successfully.",
            "seat_code": seat.code,
            "previous_status": "occupied",
            "new_status": "used",
            "user_info": user_info,
            "is_half_price": seat.is_half_price,
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
