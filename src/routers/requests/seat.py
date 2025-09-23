from pydantic import BaseModel


class SeatPreReserveRequest(BaseModel):
    seat_code: str


class SeatReserveRequest(BaseModel):
    seat_code: str
    is_half_price: bool
