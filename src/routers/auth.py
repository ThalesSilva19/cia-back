from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.routers.requests.forgot_password import ForgotPasswordRequest
from src.routers.requests.login import LoginRequest
from src.routers.requests.register import RegisterRequest
from src.routers.requests.reset_password import ResetPasswordRequest
from src.routers.responses.auth import AuthResponse, MeResponse
from src.settings import settings
from src.utils.email import EmailSender
from src.utils.hash import check_password_hash, hash_password
from src.utils.jwt import create_access_token, decode_access_token
from src.utils.password_reset import PasswordResetService

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


@router.get("/me", response_model=MeResponse)
async def get_me(authorization: str = Header(...)):
    """
    Retorna informações do usuário baseado no auth_token fornecido no header Authorization.
    """
    try:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization

        payload = decode_access_token(token)

        return MeResponse(
            user_id=payload["id"],
            user_name=payload["full_name"],
            user_scopes=payload["scopes"],
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except KeyError:
        raise HTTPException(status_code=401, detail="Token inválido")


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Envia email de recuperação de senha para o usuário.
    Por segurança, sempre retorna a mesma mensagem, independente se o usuário existe ou não.
    """
    # Verifica se o usuário existe (sem expor essa informação)
    user = db.query(User).filter(User.email == request.email).first()

    if user:
        # Gera token de recuperação
        reset_service = PasswordResetService(db)
        token = reset_service.create_reset_token(user.id)

        # Só envia o email se o usuário existir
        email_sender = EmailSender()

        # URL base para o frontend configurada nas variáveis de ambiente
        frontend_url = settings.FRONTEND_URL
        if not frontend_url.startswith(("http://", "https://")):
            frontend_url = f"http://{frontend_url}"
        reset_url = f"{frontend_url}/reset-password?token={token}"

        # Template do email de recuperação de senha
        subject = "Recuperação de Senha - CIA UFSCar"
        body = f"""
Olá {user.full_name},

Você solicitou a recuperação de senha para sua conta na CIA UFSCar.

Para redefinir sua senha, acesse o link abaixo:
{reset_url}

IMPORTANTE: Este link expira em 1 hora.

Se você não solicitou esta recuperação de senha, pode ignorar este email.

Atenciosamente,
Equipe CIA UFSCar
        """.strip()

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Recuperação de Senha - CIA UFSCar</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #2c3e50; text-align: center;">Recuperação de Senha - CIA UFSCar</h2>
    
    <p>Olá <strong>{user.full_name}</strong>,</p>
    
    <p>Você solicitou a recuperação de senha para sua conta na CIA UFSCar.</p>
    
    <p>Para redefinir sua senha, use um dos links abaixo:</p>
        
                            <!-- Botão simples e compatível -->
                            <table border="0" cellpadding="0" cellspacing="0" style="margin: 30px auto;">
                                <tr>
                                    <td align="center" style="background-color: #2c3e50; border-radius: 8px;">
                                        <a href="{reset_url}" style="display: inline-block; padding: 15px 35px; color: #ffffff; text-decoration: none; font-weight: bold; font-size: 16px; font-family: Arial, sans-serif;">
                                            Redefinir Senha
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Link direto como backup -->
                            <p style="text-align: center; margin: 20px 0;">
                                <a href="{reset_url}" style="color: #2c3e50; text-decoration: underline;">Clique aqui para redefinir sua senha</a>
                            </p>
        
    <p>Ou copie e cole este link no seu navegador:</p>
    <p style="word-break: break-all; background-color: #f5f5f5; padding: 10px; border-radius: 3px;">
        {reset_url}
    </p>
    
    <p style="color: #666; font-size: 14px;">Este link expira em 1 hora.</p>
    
    <p style="color: #666; font-size: 14px;">Se você não solicitou esta recuperação de senha, pode ignorar este email.</p>
    
    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
    
    <p style="color: #666; font-size: 12px;">
        Atenciosamente,<br>
        Equipe CIA UFSCar
    </p>
</body>
</html>
        """.strip()

        # Envia o email
        email_sender.send_email(
            subject=subject, body=body, html_body=html_body, recipient=request.email
        )

    # Sempre retorna a mesma resposta por segurança
    return {
        "message": "Se o email fornecido estiver cadastrado em nosso sistema, você receberá instruções para recuperar sua senha."
    }


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Redefine a senha do usuário usando um token de recuperação válido.
    """
    reset_service = PasswordResetService(db)

    # Valida o token
    user = reset_service.validate_reset_token(request.token)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Token inválido ou expirado. Solicite uma nova recuperação de senha.",
        )

    try:
        # Atualiza a senha do usuário
        user.password = hash_password(request.new_password)

        # Marca o token como usado
        reset_service.mark_token_as_used(request.token)

        # Limpa tokens expirados
        reset_service.cleanup_expired_tokens()

        db.commit()

        return {
            "message": "Senha redefinida com sucesso. Você pode fazer login com sua nova senha."
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor. Tente novamente mais tarde.",
        )
