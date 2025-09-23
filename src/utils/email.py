import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from src.settings import settings

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        # Configurações carregadas das variáveis de ambiente
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SMTP_SENDER_EMAIL
        self.sender_password = settings.SMTP_SENDER_PASSWORD
        self.recipient_email = settings.SMTP_RECIPIENT_EMAIL

    def send_email(
        self,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        recipient: Optional[str] = None,
    ) -> bool:
        """
        Envia um email usando Gmail SMTP.

        Args:
            subject (str): Assunto do email
            body (str): Corpo do email em texto simples
            html_body (str, optional): Corpo do email em HTML
            recipient (str, optional): Email do destinatário. Se não fornecido, usa o padrão hardcoded

        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """
        try:
            # Usa o destinatário fornecido ou o padrão hardcoded
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

            # Conecta ao servidor SMTP do Gmail
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Habilita criptografia TLS

            # Faz login
            server.login(self.sender_email, self.sender_password)

            # Envia o email
            server.send_message(msg)
            server.quit()

            logger.info(f"Email enviado com sucesso para {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Erro de autenticação: Verifique o email e senha")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error("Destinatário recusado pelo servidor")
            return False
        except smtplib.SMTPServerDisconnected:
            logger.error("Conexão com o servidor SMTP foi perdida")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False

    def send_welcome_email(self, user_name: str) -> bool:
        """
        Envia um email de boas-vindas.

        Args:
            user_name (str): Nome do usuário

        Returns:
            bool: True se o email foi enviado com sucesso
        """
        subject = "Bem-vindo ao CIA App!"

        body = f"""
        Olá {user_name},
        
        Seja bem-vindo ao CIA App! Estamos felizes em tê-lo conosco.
        
        Este é um email automático de boas-vindas.
        
        Atenciosamente,
        Equipe CIA App
        """

        html_body = f"""
        <html>
        <body>
            <h2>Bem-vindo ao CIA App!</h2>
            <p>Olá <strong>{user_name}</strong>,</p>
            <p>Seja bem-vindo ao CIA App! Estamos felizes em tê-lo conosco.</p>
            <p>Este é um email automático de boas-vindas.</p>
            <br>
            <p>Atenciosamente,<br>Equipe CIA App</p>
        </body>
        </html>
        """

        return self.send_email(subject, body, html_body)

    def send_notification_email(self, title: str, message: str) -> bool:
        """
        Envia um email de notificação.

        Args:
            title (str): Título da notificação
            message (str): Mensagem da notificação

        Returns:
            bool: True se o email foi enviado com sucesso
        """
        subject = f"Notificação CIA App: {title}"

        body = f"""
        {title}
        
        {message}
        
        ---
        CIA App
        """

        html_body = f"""
        <html>
        <body>
            <h3>{title}</h3>
            <p>{message}</p>
            <hr>
            <p><em>CIA App</em></p>
        </body>
        </html>
        """

        return self.send_email(subject, body, html_body)

    def send_email_with_attachment(
        self,
        subject: str,
        body: str,
        recipient: Optional[str] = None,
        attachment_content: bytes = None,
        attachment_filename: str = None,
        attachment_type: str = "application/octet-stream",
    ) -> bool:
        """
        Envia um email com anexo.

        Args:
            subject (str): Assunto do email
            body (str): Corpo do email em texto simples
            recipient (str, optional): Email do destinatário. Se não fornecido, usa o padrão
            attachment_content (bytes): Conteúdo do anexo
            attachment_filename (str): Nome do arquivo anexo
            attachment_type (str): Tipo MIME do anexo

        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """
        try:
            from email.mime.application import MIMEApplication
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            # Usa o destinatário fornecido ou o padrão
            to_email = recipient or self.recipient_email

            # Cria a mensagem
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to_email

            # Adiciona o corpo do email
            text_part = MIMEText(body, "plain", "utf-8")
            msg.attach(text_part)

            # Adiciona o anexo se fornecido
            if attachment_content and attachment_filename:
                # Cria o anexo (MIMEApplication detecta automaticamente o tipo)
                attachment = MIMEApplication(attachment_content)
                attachment.add_header(
                    "Content-Disposition", f"attachment; filename={attachment_filename}"
                )
                msg.attach(attachment)

            # Conecta ao servidor SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Habilita criptografia TLS

            # Faz login
            server.login(self.sender_email, self.sender_password)

            # Envia o email
            server.send_message(msg)
            server.quit()

            logger.info(f"Email com anexo enviado com sucesso para {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Erro de autenticação: Verifique o email e senha")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error("Destinatário recusado pelo servidor")
            return False
        except smtplib.SMTPServerDisconnected:
            logger.error("Conexão com o servidor SMTP foi perdida")
            return False
        except Exception as e:
            logger.error(f"Erro ao enviar email com anexo: {str(e)}")
            return False


# Instância global para uso fácil
email_sender = EmailSender()


# Funções de conveniência
def send_email(
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    recipient: Optional[str] = None,
) -> bool:
    """Função de conveniência para envio de email."""
    return email_sender.send_email(subject, body, html_body, recipient)


def send_welcome_email(user_name: str) -> bool:
    """Função de conveniência para envio de email de boas-vindas."""
    return email_sender.send_welcome_email(user_name)


def send_notification_email(title: str, message: str) -> bool:
    """Função de conveniência para envio de email de notificação."""
    return email_sender.send_notification_email(title, message)
