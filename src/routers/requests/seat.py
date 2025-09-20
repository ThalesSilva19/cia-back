from pydantic import BaseModel


class SeatRequest(BaseModel):
    seat_code: str
    is_half_price: bool
