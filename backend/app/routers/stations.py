from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.city import City
from app.models.station import CompetitorStation
from app.models.price import FuelPrice
from app.models.fuel import FuelType

from pydantic import BaseModel

router = APIRouter(
    prefix="/stations",
    tags=["stations"],
)

# ===== SCHEMAS =====

class CityOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class FuelPriceOut(BaseModel):
    fuel_type: str
    price: float
    date: str

    class Config:
        from_attributes = True


class CompetitorStationShort(BaseModel):
    id: int
    station_name: str
    address: str
    city_name: str

    class Config:
        from_attributes = True


class CompetitorStationDetail(BaseModel):
    id: int
    station_name: str
    address: str
    city: Optional[CityOut]
    latest_prices: dict

    class Config:
        from_attributes = True


# ===== ENDPOINTS =====

@router.get("/cities", response_model=List[CityOut])
def get_cities(db: Session = Depends(get_db)):
    return db.query(City).order_by(City.name).all()


@router.get("/competitors", response_model=List[CompetitorStationShort])
def get_competitors(db: Session = Depends(get_db)):
    stations = db.query(CompetitorStation).all()

    result = []
    for s in stations:
        result.append(
            CompetitorStationShort(
                id=s.id,
                station_name=s.station_name,
                address=s.address or "",
                city_name=s.city.name if s.city else "",
            )
        )
    return result


@router.get("/competitors/{station_id}", response_model=CompetitorStationDetail)
def get_competitor_detail(station_id: int, db: Session = Depends(get_db)):
    station = db.query(CompetitorStation).filter_by(id=station_id).first()
    if not station:
        raise HTTPException(404, "Станция не найдена")

    # Последние цены по каждому виду топлива
    subq = (
        db.query(
            FuelPrice.fuel_type_id,
            db.func.max(FuelPrice.date).label("mx")
        )
        .filter(FuelPrice.competitor_station_id == station_id)
        .group_by(FuelPrice.fuel_type_id)
        .subquery()
    )

    rows = (
        db.query(FuelPrice)
        .join(subq, (FuelPrice.fuel_type_id == subq.c.fuel_type_id) &
                    (FuelPrice.date == subq.c.mx))
        .all()
    )

    latest = {
        r.fuel_type.code: float(r.price)
        for r in rows
    }

    return CompetitorStationDetail(
        id=station.id,
        station_name=station.station_name,
        address=station.address,
        city=station.city,
        latest_prices=latest
    )
