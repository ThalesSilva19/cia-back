from pydantic import BaseModel


class SeatResponse(BaseModel):
    code: str
    status: str
    qr_code: str | None = None
