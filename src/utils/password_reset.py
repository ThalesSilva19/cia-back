import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.models.password_reset_token import PasswordResetToken
from src.models.user import User


class PasswordResetService:
    def __init__(self, db: Session):
        self.db = db

    def create_reset_token(self, user_id: int) -> str:
        """
        Cria um token de recuperação de senha para o usuário.
        Expira em 1 hora.
        """
        # Remove tokens anteriores não utilizados do usuário
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id, PasswordResetToken.used == "false"
        ).delete()

        # Gera novo token
        token = PasswordResetToken.generate_token()
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        # Salva no banco
        reset_token = PasswordResetToken(
            user_id=user_id, token=token, expires_at=expires_at
        )
        self.db.add(reset_token)
        self.db.commit()

        return token

    def validate_reset_token(self, token: str) -> Optional[User]:
        """
        Valida um token de recuperação de senha.
        Retorna o usuário se o token for válido, None caso contrário.
        """
        reset_token = (
            self.db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token == token,
                PasswordResetToken.used == "false",
                PasswordResetToken.expires_at > datetime.datetime.utcnow(),
            )
            .first()
        )

        if not reset_token:
            return None

        # Busca o usuário
        user = self.db.query(User).filter(User.id == reset_token.user_id).first()
        return user

    def mark_token_as_used(self, token: str) -> bool:
        """
        Marca um token como usado.
        """
        reset_token = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.token == token)
            .first()
        )

        if not reset_token:
            return False

        reset_token.used = "true"
        self.db.commit()
        return True

    def cleanup_expired_tokens(self):
        """
        Remove tokens expirados do banco de dados.
        """
        expired_tokens = (
            self.db.query(PasswordResetToken)
            .filter(PasswordResetToken.expires_at < datetime.datetime.utcnow())
            .delete()
        )
        self.db.commit()
        return expired_tokens
