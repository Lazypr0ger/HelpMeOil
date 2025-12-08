# backend/app/routers/prices.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func   # ← исправлено, раньше было db.func

from typing import List, Optional

from app.core.database import get_db
from app.models.price import FuelPrice
from app.models.station import CompetitorStation, OurStation
from app.models.city import City
from app.models.fuel import FuelType

from pydantic import BaseModel


router = APIRouter(
    prefix="/prices",
    tags=["prices"]
)

class PricePoint(BaseModel):
    timestamp: str
    price: float

class FuelHistoryOut(BaseModel):
    fuel_type: str
    history: List[PricePoint]

class LatestFuelPrice(BaseModel):
    fuel_type: str
    price: float
    timestamp: Optional[str]

class MarketAvgOut(BaseModel):
    fuel_type: str
    avg_price: float


@router.get("/history", response_model=List[FuelHistoryOut])
def get_price_history(
    station_id: int,
    station_type: str, 
    db: Session = Depends(get_db)
):
    if station_type not in ("competitor", "our"):
        raise HTTPException(400, "station_type must be competitor or our")

    query = db.query(FuelPrice).order_by(FuelPrice.date)

    if station_type == "competitor":
        prices = query.filter(FuelPrice.competitor_station_id == station_id).all()
    else:
        prices = query.filter(FuelPrice.our_station_id == station_id).all()

    if not prices:
        return []


    history_map = {}
    for p in prices:
        code = p.fuel_type.code
        history_map.setdefault(code, []).append(
            PricePoint(timestamp=p.date.isoformat(), price=float(p.price))
        )

    return [
        FuelHistoryOut(fuel_type=fuel, history=pts)
        for fuel, pts in history_map.items()
    ]


@router.get("/latest", response_model=List[LatestFuelPrice])
def get_latest_prices(
    station_id: int,
    station_type: str,
    db: Session = Depends(get_db)
):
    if station_type not in ("competitor", "our"):
        raise HTTPException(400, "station_type must be competitor or our")

    id_filter = (
        FuelPrice.competitor_station_id == station_id
        if station_type == "competitor"
        else FuelPrice.our_station_id == station_id
    )

    # Подзапрос последних дат по каждому виду топлива
    subq = (
        db.query(
            FuelPrice.fuel_type_id,
            func.max(FuelPrice.date).label("mx")
        )
        .filter(id_filter)
        .group_by(FuelPrice.fuel_type_id)
        .subquery()
    )

    rows = (
        db.query(FuelPrice)
        .join(
            subq,
            (FuelPrice.fuel_type_id == subq.c.fuel_type_id) &
            (FuelPrice.date == subq.c.mx)
        )
        .all()
    )

    return [
        LatestFuelPrice(
            fuel_type=r.fuel_type.code,
            price=float(r.price),
            timestamp=r.date.isoformat()
        )
        for r in rows
    ]


@router.get("/market/city", response_model=List[MarketAvgOut])
def get_city_market_avg(
    city_id: int,
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            FuelType.code,
            func.avg(FuelPrice.price)
        )
        .join(FuelPrice, FuelPrice.fuel_type_id == FuelType.id)
        .join(CompetitorStation, CompetitorStation.id == FuelPrice.competitor_station_id)
        .filter(CompetitorStation.city_id == city_id)
        .group_by(FuelType.code)
        .all()
    )

    return [
        MarketAvgOut(fuel_type=code, avg_price=float(avg))
        for code, avg in rows
    ]


@router.get("/market/region", response_model=List[MarketAvgOut])
def get_region_market_avg(db: Session = Depends(get_db)):
    rows = (
        db.query(
            FuelType.code,
            func.avg(FuelPrice.price)
        )
        .join(FuelType, FuelType.id == FuelPrice.fuel_type_id)
        .filter(FuelPrice.competitor_station_id.isnot(None))
        .group_by(FuelType.code)
        .all()
    )

    return [
        MarketAvgOut(fuel_type=code, avg_price=float(avg))
        for code, avg in rows
    ]
