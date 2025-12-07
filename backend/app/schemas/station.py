from pydantic import BaseModel
from typing import Optional


class OurStationBase(BaseModel):
    id: int
    name: str
    address: Optional[str]
    city: str

    class Config:
        orm_mode = True


class CompetitorStationBase(BaseModel):
    id: int
    station_name: str
    brand: Optional[str]
    address: Optional[str]
    city: str

    class Config:
        orm_mode = True
