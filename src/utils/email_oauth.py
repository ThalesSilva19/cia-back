"""
Versão alternativa do email sender usando OAuth2 para Gmail.
Esta versão é mais segura que usar senhas de app.
"""

import base64
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from src.settings import settings

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações OAuth2 carregadas das variáveis de ambiente
CLIENT_ID = settings.GOOGLE_CLIENT_ID
CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
REDIRECT_URI = settings.GOOGLE_REDIRECT_URI
SCOPES = settings.GOOGLE_SCOPES


class OAuthEmailSender:
    def __init__(self):
        # Emails carregados das variáveis de ambiente
        self.sender_email = settings.SMTP_SENDER_EMAIL
        self.recipient_email = settings.SMTP_RECIPIENT_EMAIL
        self.service = None
        self._setup_oauth()

    def _setup_oauth(self):
        """Configura o OAuth2 para Gmail API"""
        try:
            # Carrega credenciais existentes se disponíveis
            creds = None
            token_file = "token.json"

            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)

            # Se não há credenciais válidas, faz o fluxo de autorização
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = Flow.from_client_config(
                        {
                            "web": {
                                "client_id": CLIENT_ID,
                                "client_secret": CLIENT_SECRET,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "redirect_uris": [REDIRECT_URI],
                            }
                        },
                        SCOPES,
                    )
                    flow.redirect_uri = REDIRECT_URI

                    # Gera URL de autorização
                    auth_url, _ = flow.authorization_url(prompt="consent")
                    print(f"Vá para esta URL para autorizar: {auth_url}")

                    # Solicita código de autorização
                    auth_code = input("Digite o código de autorização: ")
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials

                # Salva as credenciais para uso futuro
                with open(token_file, "w") as token:
                    token.write(creds.to_json())

            # Cria o serviço Gmail
            self.service = build("gmail", "v1", credentials=creds)
            logger.info("OAuth2 configurado com sucesso")

        except Exception as e:
            logger.error(f"Erro ao configurar OAuth2: {str(e)}")
            self.service = None

    def send_email(
        self,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        recipient: Optional[str] = None,
    ) -> bool:
        """
        Envia um email usando Gmail API com OAuth2.
        """
        if not self.service:
            logger.error("Serviço Gmail não configurado")
            return False

        try:
            to_email = recipient or self.recipient_email

            # Cria a mensagem
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to_email

            # Adiciona o corpo do email
            text_part = MIMEText(body, "plain", "utf-8")
            msg.attach(text_part)

            # Adiciona o corpo HTML se fornecido
            if html_body:
                html_part = MIMEText(html_body, "html", "utf-8")
                msg.attach(html_part)

            # Codifica a mensagem
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

            # Envia o email
            message = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            logger.info(
                f"Email enviado com sucesso para {to_email}. Message ID: {message['id']}"
            )
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False


# Instância global
oauth_email_sender = OAuthEmailSender()


def send_email_oauth(
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    recipient: Optional[str] = None,
) -> bool:
    """Função de conveniência para envio de email via OAuth2."""
    return oauth_email_sender.send_email(subject, body, html_body, recipient)
