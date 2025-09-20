from fastapi import APIRouter, HTTPException

from src.settings import settings
from src.utils.email import send_email
from src.utils.email_debug import send_test_email_with_config, test_smtp_connection

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/send-hello")
async def send_hello_world():
    """
    Envia um email com 'Hello World' para o destinatário padrão.

    Returns:
        dict: Mensagem de sucesso ou erro
    """
    try:
        subject = "Hello World"
        body = "Hello World"

        success = send_email(subject=subject, body=body)

        if success:
            return {"message": "Email 'Hello World' enviado com sucesso!"}
        else:
            raise HTTPException(status_code=500, detail="Falha ao enviar o email")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro interno do servidor: {str(e)}"
        )


@router.get("/test-connection")
async def test_email_connection():
    """
    Testa a conexão SMTP para diagnosticar problemas de autenticação.

    Returns:
        dict: Resultado dos testes de conexão
    """
    try:
        working_config = test_smtp_connection()

        if working_config:
            return {
                "success": True,
                "message": f"Conexão bem-sucedida com {working_config['name']}",
                "config": working_config,
            }
        else:
            return {
                "success": False,
                "message": "Falha em todas as configurações testadas",
                "solutions": [
                    "1. Ative a verificação em 2 etapas e use uma senha de app",
                    "2. Ative 'Acesso de apps menos seguros' no Gmail",
                    "3. Verifique se o email e senha estão corretos",
                    "4. Certifique-se de que a conta não está bloqueada",
                ],
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao testar conexão: {str(e)}")


@router.post("/send-test")
async def send_test_email():
    """
    Envia um email de teste para verificar se tudo está funcionando.

    Returns:
        dict: Resultado do envio do email de teste
    """
    try:
        # Primeiro testa a conexão
        working_config = test_smtp_connection()

        if not working_config:
            raise HTTPException(
                status_code=400,
                detail="Nenhuma configuração SMTP funcionando. Use /test-connection para diagnosticar.",
            )

        # Envia email de teste
        success = send_test_email_with_config(working_config)

        if success:
            return {
                "success": True,
                "message": "Email de teste enviado com sucesso!",
                "config_used": working_config["name"],
            }
        else:
            raise HTTPException(
                status_code=500, detail="Falha ao enviar email de teste"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao enviar email de teste: {str(e)}"
        )


@router.post("/test-credentials")
async def test_credentials():
    """
    Testa as credenciais atuais sem enviar email.

    Returns:
        dict: Resultado do teste de credenciais
    """
    import smtplib

    try:
        # Credenciais carregadas das variáveis de ambiente
        email = settings.SMTP_SENDER_EMAIL
        password = settings.SMTP_SENDER_PASSWORD

        # Testa conexão SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        # Tenta fazer login
        server.login(email, password)
        server.quit()

        return {
            "success": True,
            "message": "Credenciais válidas! Login bem-sucedido.",
            "email": email,
            "password_length": len(password),
            "password_format": "App Password (16 chars with spaces)",
        }

    except smtplib.SMTPAuthenticationError as e:
        return {
            "success": False,
            "message": "Erro de autenticação",
            "error": str(e),
            "possible_causes": [
                "Senha de app incorreta ou incompleta",
                "Verificação em duas etapas não ativada",
                "Email incorreto",
                "Conta bloqueada ou suspensa",
            ],
        }
    except Exception as e:
        return {"success": False, "message": "Erro de conexão", "error": str(e)}
