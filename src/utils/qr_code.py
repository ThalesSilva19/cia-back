import base64
import hashlib
import io
import json

import qrcode


def generate_seat_qr_code(
    seat_code: str,
    status: str,
    is_half_price: bool = False,
    secret_key: str = "cia-seat-system",
) -> str:
    """
    Gera um QR code PNG para um assento específico.

    O QR code contém:
    - Código do assento (code)
    - Status do assento (status)
    - Se é meia entrada (is_half_price)
    - Hash único gerado com base no código, status, tipo e secret_key

    Args:
        seat_code: Código do assento (ex: "A1", "B5")
        status: Status do assento (ex: "available", "reserved")
        is_half_price: Se o assento é meia entrada
        secret_key: Chave secreta para gerar o hash único

    Returns:
        Base64 string do QR code PNG
    """
    # Gera um hash único usando o código do assento, status, tipo de ingresso e a chave secreta
    unique_hash = hashlib.sha256(
        f"{seat_code}{status}{is_half_price}{secret_key}".encode()
    ).hexdigest()[:16]

    # Monta os dados a serem codificados no QR code
    qr_data = {
        "seat_code": seat_code,
        "status": status,
        "is_half_price": is_half_price,
        "hash": unique_hash,
    }

    # Converte para JSON string
    qr_json = str(qr_data)

    # Gera o QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_json)
    qr.make(fit=True)

    # Cria a imagem do QR code
    img = qr.make_image(fill_color="black", back_color="white")

    # Converte para bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Retorna como base64
    return base64.b64encode(img_buffer.read()).decode("utf-8")


def validate_qr_code(qr_code_data: dict, secret_key: str = "cia-seat-system") -> bool:
    """
    Valida um QR code verificando o hash.

    Args:
        qr_code_data: Dicionário com os dados do QR code (seat_code, status, is_half_price, hash)
        secret_key: Chave secreta usada para gerar o hash

    Returns:
        True se o QR code for válido, False caso contrário
    """
    try:
        seat_code = qr_code_data.get("seat_code")
        status = qr_code_data.get("status")
        is_half_price = qr_code_data.get("is_half_price", False)
        hash_from_qr = qr_code_data.get("hash")

        if seat_code is None or status is None or hash_from_qr is None:
            return False

        # Recalcula o hash esperado incluindo is_half_price
        expected_hash = hashlib.sha256(
            f"{seat_code}{status}{is_half_price}{secret_key}".encode()
        ).hexdigest()[:16]

        return hash_from_qr == expected_hash
    except Exception:
        return False


def decode_qr_data(qr_string: str) -> dict | None:
    """
    Decodifica uma string de QR code JSON.

    Args:
        qr_string: String JSON do QR code

    Returns:
        Dicionário com os dados do QR code ou None se inválido
    """
    try:
        # Remove possíveis espaços ou caracteres extras
        qr_string = qr_string.strip()

        # Tenta parsear como JSON
        if qr_string.startswith("{") and qr_string.endswith("}"):
            return json.loads(qr_string)
        else:
            # Tenta converter string Python dict para dict real
            return eval(qr_string)
    except Exception:
        return None
