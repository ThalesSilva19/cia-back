import os
from typing import List, Optional

from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()


class Settings:
    """Configurações da aplicação carregadas das variáveis de ambiente."""

    # =============================================================================
    # CONFIGURAÇÕES DE BANCO DE DADOS
    # =============================================================================
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # =============================================================================
    # CONFIGURAÇÕES DE AUTENTICAÇÃO JWT
    # =============================================================================
    JWT_SECRET_KEY: Optional[str] = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # =============================================================================
    # CONFIGURAÇÕES DE EMAIL SMTP
    # =============================================================================
    SMTP_SENDER_EMAIL: Optional[str] = os.getenv("SMTP_SENDER_EMAIL")
    SMTP_SENDER_PASSWORD: Optional[str] = os.getenv("SMTP_SENDER_PASSWORD")
    SMTP_RECIPIENT_EMAIL: Optional[str] = os.getenv("SMTP_RECIPIENT_EMAIL")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))

    # =============================================================================
    # CONFIGURAÇÕES DE OAUTH2 GOOGLE
    # =============================================================================
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI")
    GOOGLE_SCOPES: List[str] = os.getenv(
        "GOOGLE_SCOPES", "https://www.googleapis.com/auth/gmail.send"
    ).split(",")

    # =============================================================================
    # CONFIGURAÇÕES DE AMBIENTE
    # =============================================================================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # =============================================================================
    # CONFIGURAÇÕES DE CORS
    # =============================================================================
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:8000"
    ).split(",")

    # =============================================================================
    # MÉTODOS DE VALIDAÇÃO
    # =============================================================================

    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento."""
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção."""
        return self.ENVIRONMENT == "production"

    def validate_required_settings(self) -> None:
        """Valida se todas as configurações obrigatórias estão presentes."""
        required_settings = [
            "DATABASE_URL",
            "JWT_SECRET_KEY",
            "SMTP_SENDER_EMAIL",
            "SMTP_SENDER_PASSWORD",
        ]

        missing_settings = []
        for setting in required_settings:
            if not getattr(self, setting):
                missing_settings.append(setting)

        if missing_settings:
            raise ValueError(
                f"Configurações obrigatórias ausentes: {', '.join(missing_settings)}"
            )


# Instância global das configurações
settings = Settings()

# Valida as configurações ao importar o módulo
if settings.is_production():
    settings.validate_required_settings()
