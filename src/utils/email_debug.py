"""
Versão de debug para testar configurações de email SMTP
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.settings import settings

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_smtp_connection():
    """Testa a conexão SMTP com diferentes configurações"""

    # Configurações para testar
    configs = [
        {
            "name": "Gmail SMTP (TLS)",
            "server": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            "use_ssl": False,
        },
        {
            "name": "Gmail SMTP (SSL)",
            "server": "smtp.gmail.com",
            "port": 465,
            "use_tls": False,
            "use_ssl": True,
        },
    ]

    # Credenciais carregadas das variáveis de ambiente
    email = settings.SMTP_SENDER_EMAIL
    password = settings.SMTP_SENDER_PASSWORD

    for config in configs:
        print(f"\n=== Testando {config['name']} ===")

        try:
            if config["use_ssl"]:
                server = smtplib.SMTP_SSL(config["server"], config["port"])
            else:
                server = smtplib.SMTP(config["server"], config["port"])
                if config["use_tls"]:
                    server.starttls()

            # Habilita debug
            server.set_debuglevel(1)

            # Tenta fazer login
            server.login(email, password)

            print(f"✅ Sucesso com {config['name']}")
            server.quit()
            return config

        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Erro de autenticação com {config['name']}: {e}")
        except Exception as e:
            print(f"❌ Erro com {config['name']}: {e}")

    return None


def send_test_email_with_config(config, recipient="test@example.com"):
    """Envia um email de teste com a configuração que funcionou"""

    # Credenciais carregadas das variáveis de ambiente
    email = settings.SMTP_SENDER_EMAIL
    password = settings.SMTP_SENDER_PASSWORD

    try:
        # Conecta
        if config["use_ssl"]:
            server = smtplib.SMTP_SSL(config["server"], config["port"])
        else:
            server = smtplib.SMTP(config["server"], config["port"])
            if config["use_tls"]:
                server.starttls()

        # Login
        server.login(email, password)

        # Cria mensagem
        msg = MIMEMultipart()
        msg["From"] = email
        msg["To"] = recipient
        msg["Subject"] = "Teste de Email - CIA App"

        body = """
        Este é um email de teste enviado pelo CIA App.
        
        Se você recebeu este email, a configuração está funcionando!
        
        Atenciosamente,
        CIA App
        """

        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Envia
        server.send_message(msg)
        server.quit()

        print(f"✅ Email de teste enviado com sucesso para {recipient}")
        return True

    except Exception as e:
        print(f"❌ Erro ao enviar email de teste: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Testando configurações SMTP...")

    # Testa conexões
    working_config = test_smtp_connection()

    if working_config:
        print(f"\n🎉 Configuração que funciona: {working_config['name']}")

        # Envia email de teste
        send_test_email_with_config(working_config)
    else:
        print("\n❌ Nenhuma configuração funcionou.")
        print("\n💡 Possíveis soluções:")
        print("1. Ative a verificação em 2 etapas e use uma senha de app")
        print("2. Ative 'Acesso de apps menos seguros'")
        print("3. Verifique se o email e senha estão corretos")
        print("4. Certifique-se de que a conta não está bloqueada")
