# backend/app/routers/prices.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.price import FuelPrice
from app.models.station import CompetitorStation, OurStation
from app.models.city import City
from app.models.fuel import FuelType

from pydantic import BaseModel
from datetime import datetime


router = APIRouter(
    prefix="/prices",
    tags=["prices"]
)

# ------------------------
#  SCHEMAS
# ------------------------

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


# ===============================================================
# 1. Получить историю цен станции: competitor или our
# ===============================================================
@router.get("/history", response_model=List[FuelHistoryOut])
def get_price_history(
    station_id: int,
    station_type: str,   # "competitor" or "our"
    db: Session = Depends(get_db)
):
    if station_type not in ("competitor", "our"):
        raise HTTPException(400, "station_type must be competitor or our")

    if station_type == "competitor":
        prices = (
            db.query(FuelPrice)
            .filter(FuelPrice.competitor_station_id == station_id)
            .order_by(FuelPrice.date)
            .all()
        )
    else:
        prices = (
            db.query(FuelPrice)
            .filter(FuelPrice.our_station_id == station_id)
            .order_by(FuelPrice.date)
            .all()
        )
    
    if not prices:
        return []

    # группируем по fuel_type
    history_map = {}
    for p in prices:
        key = p.fuel_type.code
        if key not in history_map:
            history_map[key] = []
        history_map[key].append(
            PricePoint(
                timestamp=p.date.isoformat(),
                price=float(p.price)
            )
        )

    result = [
        FuelHistoryOut(fuel_type=fuel, history=pts)
        for fuel, pts in history_map.items()
    ]
    return result


# ===============================================================
# 2. Получить последние цены по станции
# ===============================================================
@router.get("/latest", response_model=List[LatestFuelPrice])
def get_latest_prices(
    station_id: int,
    station_type: str,
    db: Session = Depends(get_db)
):
    if station_type not in ("competitor", "our"):
        raise HTTPException(400, "station_type must be competitor or our")

    subq = (
        db.query(
            FuelPrice.fuel_type_id,
            db.func.max(FuelPrice.date).label("mx")
        )
        .filter(
            FuelPrice.competitor_station_id == station_id
            if station_type == "competitor"
            else FuelPrice.our_station_id == station_id
        )
        .group_by(FuelPrice.fuel_type_id)
        .subquery()
    )

    rows = (
        db.query(FuelPrice)
        .join(
            subq,
            (FuelPrice.fuel_type_id == subq.c.fuel_type_id)
            & (FuelPrice.date == subq.c.mx)
        )
        .all()
    )

    result = []
    for r in rows:
        result.append(
            LatestFuelPrice(
                fuel_type=r.fuel_type.code,
                price=float(r.price),
                timestamp=r.date.isoformat()
            )
        )
    return result


# ===============================================================
# 3. Средняя рыночная цена по каждому виду топлива в городе
# ===============================================================
@router.get("/market/city", response_model=List[MarketAvgOut])
def get_city_market_avg(
    city_id: int,
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            FuelType.code,
            db.func.avg(FuelPrice.price)
        )
        .join(FuelType, FuelType.id == FuelPrice.fuel_type_id)
        .join(CompetitorStation, CompetitorStation.id == FuelPrice.competitor_station_id)
        .filter(CompetitorStation.city_id == city_id)
        .group_by(FuelType.code)
        .all()
    )

    return [
        MarketAvgOut(
            fuel_type=code,
            avg_price=float(avg)
        )
        for code, avg in rows
    ]


# ===============================================================
# 4. Средняя цена по области (всем конкурентам)
# ===============================================================
@router.get("/market/region", response_model=List[MarketAvgOut])
def get_region_market_avg(
    db: Session = Depends(get_db)
):
    rows = (
        db.query(
            FuelType.code,
            db.func.avg(FuelPrice.price)
        )
        .join(FuelType, FuelType.id == FuelPrice.fuel_type_id)
        .filter(FuelPrice.competitor_station_id.isnot(None))
        .group_by(FuelType.code)
        .all()
    )

    return [
        MarketAvgOut(
            fuel_type=code,
            avg_price=float(avg)
        )
        for code, avg in rows
    ]
