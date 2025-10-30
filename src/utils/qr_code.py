import base64
import hashlib
import io
import json
from urllib.parse import urlencode

import qrcode

from src.settings import settings


def generate_seat_qr_code(
    seat_code: str,
    status: str,
    is_half_price: bool = False,
    buyer_name: str = "",
    secret_key: str = "cia-seat-system",
) -> str:
    """
    Gera um QR code PNG para um assento específico com uma URL simplificada.

    Novo formato da URL:
    https://seu-dominio.com/qrcode/{HASH}?seat_code={CODIGO}

    Args:
        seat_code: Código do assento (ex: "A1", "B5")
        status: Status do assento (ex: "available", "reserved", "occupied")
        is_half_price: Se o assento é meia entrada
        buyer_name: Nome do comprador do assento
        secret_key: Chave secreta para gerar o hash único

    Returns:
        Base64 string do QR code PNG
    """
    # Gera um hash único usando o código do assento, status, tipo de ingresso e a chave secreta
    unique_hash = hashlib.sha256(
        f"{seat_code}{status}{is_half_price}{secret_key}".encode()
    ).hexdigest()[:16]

    # Monta os parâmetros mínimos da URL
    query_string = urlencode({"seat_code": seat_code})

    # Constrói a URL completa (hash no path e seat_code como query param)
    qr_url = f"{settings.QR_CODE_DOMAIN}/qrcode/{unique_hash}?{query_string}"

    # Gera o QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    # Cria a imagem do QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Converte para bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Retorna como base64
    return base64.b64encode(img_buffer.read()).decode("utf-8")


def validate_qr_code(
    hash: str,
    seat_code: str,
    is_half_price: bool,
    status: str,
    user_id: int,
    db,
    secret_key: str = "cia-seat-system",
) -> dict:
    """
    Valida um QR code verificando o hash e atualiza o status do assento para "used" se válido.

    Args:
        hash: Hash do QR code
        seat_code: Código do assento
        is_half_price: Se o ingresso é meia entrada
        status: Status do ingresso (deve ser "occupied")
        user_id: ID do usuário que comprou o ingresso
        db: Sessão do banco de dados (SQLAlchemy Session)
        secret_key: Chave secreta usada para gerar o hash

    Returns:
        Dicionário com informações do assento validado

    Raises:
        ValueError: Se o QR code for inválido ou o assento não atender aos requisitos
    """
    from src.models.seat import Seat

    try:
        # Valida parâmetros obrigatórios
        if not hash or not seat_code or status is None:
            raise ValueError(
                "Missing required parameters: hash, seat_code, and status are required."
            )

        # Recalcula o hash esperado incluindo is_half_price
        expected_hash = hashlib.sha256(
            f"{seat_code}{status}{is_half_price}{secret_key}".encode()
        ).hexdigest()[:16]

        # Verifica se o hash corresponde
        if hash != expected_hash:
            raise ValueError("Invalid QR code - hash verification failed.")

        # Busca o assento no banco de dados
        seat = db.query(Seat).filter(Seat.code == seat_code).with_for_update().first()
        if not seat:
            raise ValueError(f"Seat not found: {seat_code}")

        # Verifica se o assento pertence ao usuário
        if seat.user_id != user_id:
            raise ValueError(f"Seat does not belong to user {user_id}.")

        # Verifica se o assento está no status correto (occupied)
        if seat.status != "occupied":
            raise ValueError(
                f"Cannot validate seat with status '{seat.status}'. Expected 'occupied'."
            )

        # Verifica se o status do QR code é 'occupied'
        if status != "occupied":
            raise ValueError(f"QR code status is '{status}'. Expected 'occupied'.")

        # Verifica se o tipo de ingresso do QR code corresponde ao do banco
        if seat.is_half_price != is_half_price:
            raise ValueError(
                f"QR code ticket type mismatch. Expected '{'Meia' if seat.is_half_price else 'Inteira'}', got '{'Meia' if is_half_price else 'Inteira'}'."
            )

        # Atualiza o assento para 'used'
        seat.status = "used"
        db.commit()

        return {
            "success": True,
            "seat_code": seat.code,
            "previous_status": "occupied",
            "new_status": "used",
            "is_half_price": seat.is_half_price,
        }
    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error validating QR code: {str(e)}")


def decode_qr_data(qr_string: str) -> dict | None:
    """
    Decodifica uma string de QR code (URL ou JSON para compatibilidade).

    Suporta dois formatos:
    1. URL: https://seu-dominio.com/qrcode/{HASH}?buyer_name=...&seat_code=...&is_half_price=...&status=...
    2. JSON (legado): {"seat_code": "...", "status": "...", ...}

    Args:
        qr_string: String com URL ou JSON do QR code

    Returns:
        Dicionário com os dados do QR code ou None se inválido
    """
    try:
        # Remove possíveis espaços ou caracteres extras
        qr_string = qr_string.strip()

        # Tenta parsear como URL primeiro
        if qr_string.startswith("http://") or qr_string.startswith("https://"):
            from urllib.parse import parse_qs, unquote, urlparse

            parsed_url = urlparse(qr_string)
            query_params = parse_qs(parsed_url.query)

            # Extrai o hash do caminho (último segmento antes dos query params)
            path_parts = parsed_url.path.strip("/").split("/")
            hash_value = path_parts[-1] if path_parts else None

            # Extrai os parâmetros da query
            buyer_name = unquote(query_params.get("buyer_name", [""])[0])
            seat_code = query_params.get("seat_code", [""])[0]
            is_half_price_str = query_params.get("is_half_price", ["false"])[0].lower()
            status = query_params.get("status", [""])[0]

            # Converte is_half_price para boolean
            is_half_price = is_half_price_str == "true"

            return {
                "hash": hash_value,
                "buyer_name": buyer_name,
                "seat_code": seat_code,
                "is_half_price": is_half_price,
                "status": status,
            }

        # Compatibilidade: tenta parsear como JSON (formato antigo)
        if qr_string.startswith("{") and qr_string.endswith("}"):
            try:
                return json.loads(qr_string)
            except json.JSONDecodeError:
                # Tenta converter string Python dict para dict real (não recomendado, mas mantido para compatibilidade)
                try:
                    return eval(qr_string)
                except Exception:
                    return None

        return None
    except Exception:
        return None
