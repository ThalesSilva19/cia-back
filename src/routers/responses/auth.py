from pydantic import BaseModel


class AuthResponse(BaseModel):
    access_token: str


class MeResponse(BaseModel):
    user_id: int
    user_name: str
    user_scopes: str
