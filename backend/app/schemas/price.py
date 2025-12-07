from pydantic import BaseModel
from datetime import date
from typing import Optional


class PriceRecord(BaseModel):
    date: date
    price: float

    class Config:
        orm_mode = True
