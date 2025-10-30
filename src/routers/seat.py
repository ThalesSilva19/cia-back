import json

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.seat import Seat
from src.models.transaction import Transaction
from src.routers.requests.seat import (
    SeatPreReserveRequest,
    SeatReserveRequest,
)
from src.routers.responses.seat import SeatResponse
from src.settings import settings
from src.utils.auth import get_current_user
from src.utils.email import EmailSender
from src.utils.qr_code import generate_seat_qr_code

router = APIRouter(prefix="/seats")


@router.get("/", response_model=list[SeatResponse])
async def get_seats(
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    _ = get_current_user(authorization)
    seats = db.query(Seat).all()
    return [
        SeatResponse(
            code=seat.code,
            status=seat.status,
            qr_code=None,  # QR codes só para assentos do usuário em /seats/user
        )
        for seat in seats
    ]


@router.get("/user", response_model=list[SeatResponse])
async def get_user_seats(
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    user = get_current_user(authorization)
    seats = db.query(Seat).filter(Seat.user_id == user["id"]).all()
    return [
        SeatResponse(
            code=seat.code,
            status=seat.status,
            qr_code=generate_seat_qr_code(seat.code, seat.status, seat.is_half_price)
            if seat.status == "occupied"
            else None,
        )
        for seat in seats
    ]


@router.get("/user/pre-reserved", response_model=list[SeatResponse])
async def get_user_pre_reserved_seats(
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    """
    Retorna todos os assentos pré-reservados do usuário autenticado.
    """
    user = get_current_user(authorization)
    pre_reserved_seats = (
        db.query(Seat)
        .filter(Seat.user_id == user["id"], Seat.status == "pre-reserved")
        .all()
    )
    return [
        SeatResponse(
            code=seat.code,
            status=seat.status,
            qr_code=None,  # Não gera QR para pre-reserved
        )
        for seat in pre_reserved_seats
    ]


@router.post("/reserve")
async def reserve_seats(
    request: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    user = get_current_user(authorization)

    # Parse da string JSON para lista de objetos
    try:
        request_data = json.loads(request)
        if not isinstance(request_data, list):
            raise HTTPException(
                status_code=400, detail="Request deve ser uma lista de assentos"
            )

        # Valida e converte para objetos SeatReserveRequest
        seat_requests = []
        for item in request_data:
            if not isinstance(item, dict):
                raise HTTPException(
                    status_code=400, detail="Cada item deve ser um objeto"
                )
            if "seat_code" not in item or "is_half_price" not in item:
                raise HTTPException(
                    status_code=400,
                    detail="Cada item deve ter seat_code e is_half_price",
                )
            seat_requests.append(SeatReserveRequest(**item))

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato JSON inválido")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Erro ao processar dados: {str(e)}"
        )

    seat_map = {
        seat_req.seat_code: seat_req.is_half_price for seat_req in seat_requests
    }
    seat_codes = list(seat_map.keys())

    try:
        seats = db.query(Seat).filter(Seat.code.in_(seat_codes)).with_for_update().all()

        if len(seats) != len(seat_codes):
            found_codes = {seat.code for seat in seats}
            not_found = [code for code in seat_codes if code not in found_codes]
            raise HTTPException(
                status_code=404, detail=f"Seat(s) not found: {', '.join(not_found)}"
            )

        not_pre_reserved = [
            seat.code for seat in seats if seat.status != "pre-reserved"
        ]
        if not_pre_reserved:
            raise HTTPException(
                status_code=400,
                detail=f"Seats are not pre-reserved: {', '.join(not_pre_reserved)}",
            )

        not_owned = [seat.code for seat in seats if seat.user_id != user["id"]]
        if not_owned:
            raise HTTPException(
                status_code=403,
                detail=f"User does not own these pre-reserved seats: {', '.join(not_owned)}",
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

        # Calcula o valor total (assumindo preços fixos)
        full_price = 50.0  # Preço cheio
        half_price = 25.0  # Meia entrada

        total_value = 0.0
        for seat in seats:
            if seat.is_half_price:
                total_value += half_price
            else:
                total_value += full_price

        # Valida o arquivo
        if not file.filename:
            raise HTTPException(status_code=400, detail="Arquivo é obrigatório")

        # Valida o tipo de arquivo
        allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".gif"}
        file_extension = "." + file.filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Tipo de arquivo não suportado. Use PDF ou imagens (JPG, PNG, GIF)",
            )

        # Lê o conteúdo do arquivo
        file_content = await file.read()

        # Envia email com comprovante
        email_sender = EmailSender()
        subject = f"Comprovantes {user['full_name']} - R$ {total_value:.2f}"

        # Conta ingressos por tipo
        full_price_count = sum(1 for seat in seats if not seat.is_half_price)
        half_price_count = sum(1 for seat in seats if seat.is_half_price)

        # Lista detalhada dos ingressos
        seat_details = []
        for seat in seats:
            seat_type = "Meia entrada" if seat.is_half_price else "Inteira"
            seat_price = half_price if seat.is_half_price else full_price
            seat_details.append(f"  - {seat.code}: {seat_type} (R$ {seat_price:.2f})")

        # Corpo do email melhorado
        body = f"""
Nova reserva de ingressos recebida!

DADOS DO COMPRADOR:
- Nome: {user["full_name"]}
- Email: {user["email"]}
- Data da reserva: {transaction.created_at.strftime("%d/%m/%Y às %H:%M")}

DETALHES DA RESERVA:
- Total de ingressos: {len(seat_codes)}
  * Inteira: {full_price_count} ingressos
  * Meia entrada: {half_price_count} ingressos

LISTA DE INGRESSOS:
{chr(10).join(seat_details)}

VALOR TOTAL: R$ {total_value:.2f}

COMPROVANTE: Em anexo ({file.filename})

---
Este email foi enviado automaticamente pelo sistema de reservas.
        """.strip()

        # Log para debug
        print(f"📧 Enviando email para: {settings.SMTP_SENDER_EMAIL}")
        print(f"📧 Assunto: {subject}")
        print(f"📧 Arquivo: {file.filename}")

        # Envia o email com anexo
        email_sent = email_sender.send_email_with_attachment(
            subject=subject,
            body=body,
            recipient=settings.SMTP_SENDER_EMAIL,  # Email para si mesmo
            attachment_content=file_content,
            attachment_filename=file.filename,
            attachment_type=file.content_type or "application/octet-stream",
        )

        if email_sent:
            print("✅ Email enviado com sucesso!")
        else:
            print("❌ Falha ao enviar email!")
            raise HTTPException(
                status_code=500, detail="Erro ao enviar email com comprovante"
            )

        return {"message": "Seats reserved successfully and receipt sent via email."}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error during reservation: {str(e)}"
        )


@router.post("/pre-reserve")
async def pre_reserve_seats(
    request: list[SeatPreReserveRequest],
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    user = get_current_user(authorization)
    seat_codes = [seat_req.seat_code for seat_req in request]

    try:
        seats = db.query(Seat).filter(Seat.code.in_(seat_codes)).with_for_update().all()

        if len(seats) != len(seat_codes):
            found_codes = {seat.code for seat in seats}
            not_found = [code for code in seat_codes if code not in found_codes]
            raise HTTPException(
                status_code=404, detail=f"Seat(s) not found: {', '.join(not_found)}"
            )

        # Verifica assentos indisponíveis, mas permite que o usuário interaja com seus próprios assentos pre-reserved
        unavailable = []
        for seat in seats:
            if seat.status == "available":
                continue  # Assento disponível, pode ser pré-reservado
            elif seat.status == "pre-reserved" and seat.user_id == user["id"]:
                continue  # Assento pré-reservado pelo próprio usuário, pode interagir novamente
            elif seat.status == "reserved":
                unavailable.append(
                    seat.code
                )  # Assento já reservado, não pode ser alterado
            elif seat.status == "occupied":
                unavailable.append(seat.code)  # Assento ocupado, não pode ser alterado
            elif seat.status == "pre-reserved" and seat.user_id != user["id"]:
                unavailable.append(seat.code)  # Assento pré-reservado por outro usuário

        if unavailable:
            raise HTTPException(
                status_code=400,
                detail=f"Seats not available or reserved by other users: {', '.join(unavailable)}",
            )

        # Limpa todas as pré-reservas antigas do usuário que não estão na nova lista
        old_pre_reserved_seats = (
            db.query(Seat)
            .filter(
                Seat.status == "pre-reserved",
                Seat.user_id == user["id"],
                ~Seat.code.in_(seat_codes),
            )
            .with_for_update()
            .all()
        )

        for old_seat in old_pre_reserved_seats:
            old_seat.status = "available"
            old_seat.user_id = None
            old_seat.is_half_price = (
                False  # Limpa também a configuração de meia-entrada
            )

        # Aplica as novas pré-reservas
        for seat in seats:
            seat.status = "pre-reserved"
            seat.user_id = user["id"]

        transaction = Transaction(
            seats=seat_codes,
            user_id=user["id"],
        )
        db.add(transaction)
        db.commit()
        return {"message": "Seats pre-reserved successfully."}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error during pre-reservation: {str(e)}"
        )
