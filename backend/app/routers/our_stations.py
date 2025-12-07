from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func   # ← ДОБАВЛЕНО

from typing import List

from app.core.database import get_db
from app.models.station import OurStation, CompetitorStation
from app.models.price import FuelPrice
from app.models.fuel import FuelType
from app.models.city import City

from pydantic import BaseModel

router = APIRouter(prefix="/our-stations", tags=["our stations"])


# ==== SCHEMAS ====

class OurStationOut(BaseModel):
    id: int
    name: str
    address: str
    city_name: str
    latest_prices: dict

    class Config:
        from_attributes = True


# ==== ENDPOINTS ====

@router.get("/", response_model=List[OurStationOut])
def get_our_stations(db: Session = Depends(get_db)):
    stations = db.query(OurStation).all()
    result = []

    for s in stations:

        # --- последние цены ---
        subq = (
            db.query(
                FuelPrice.fuel_type_id,
                func.max(FuelPrice.date).label("mx")   # ← FIXED
            )
            .filter(FuelPrice.our_station_id == s.id)
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

        prices = {r.fuel_type.code: float(r.price) for r in rows}

        result.append(
            OurStationOut(
                id=s.id,
                name=s.name,
                address=s.address,
                city_name=s.city.name,
                latest_prices=prices
            )
        )

    return result


@router.get("/{station_id}", response_model=OurStationOut)
def station_details(station_id: int, db: Session = Depends(get_db)):
    st = db.query(OurStation).filter_by(id=station_id).first()
    if not st:
        raise HTTPException(404, "Станция не найдена")

    subq = (
        db.query(
            FuelPrice.fuel_type_id,
            func.max(FuelPrice.date).label("mx")   # ← FIXED
        )
        .filter(FuelPrice.our_station_id == station_id)
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

    prices = {r.fuel_type.code: float(r.price) for r in rows}

    return OurStationOut(
        id=st.id,
        name=st.name,
        address=st.address,
        city_name=st.city.name,
        latest_prices=prices
    )


@router.get("/{station_id}/competitors")
def get_competitors_for_our(station_id: int, db: Session = Depends(get_db)):
    st = db.query(OurStation).filter_by(id=station_id).first()
    if not st:
        raise HTTPException(404, "Станция не найдена")

    comps = (
        db.query(CompetitorStation)
        .filter(CompetitorStation.city_id == st.city_id)
        .all()
    )

    return [
        {
            "id": c.id,
            "name": c.station_name,
            "address": c.address
        }
        for c in comps
    ]


@router.get("/{station_id}/history")
def get_price_history(station_id: int, db: Session = Depends(get_db)):
    prices = (
        db.query(FuelPrice)
        .filter(FuelPrice.our_station_id == station_id)
        .order_by(FuelPrice.date)
        .all()
    )

    history = {}
    for p in prices:
        code = p.fuel_type.code
        if code not in history:
            history[code] = []
        history[code].append({"date": p.date.isoformat(), "price": float(p.price)})

    return history
