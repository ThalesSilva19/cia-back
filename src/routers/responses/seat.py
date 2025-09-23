from pydantic import BaseModel


class SeatResponse(BaseModel):
    code: str
    status: str
