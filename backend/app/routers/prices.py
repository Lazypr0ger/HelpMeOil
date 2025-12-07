from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.price import FuelPrice, StationType
from app.models.station import OurStation, CompetitorStation
from app.models.city import City
from app.schemas.price import PriceRecord
from app.services.analytics import get_recommended_price


router = APIRouter()


# -------------------------
#  DB dependency
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================================================================
# 1. ИСТОРИЯ ЦЕН СТАНЦИИ ПО ВИДУ ТОПЛИВА
# ================================================================
@router.get("/history", response_model=list[PriceRecord])
def get_price_history(
    station_id: int,
    fuel: str,
    station_type: StationType = StationType.competitor,
    db: Session = Depends(get_db)
):
    """
    Возвращает историю цен по конкретной станции и типу топлива.
    Используется на странице station.html и charts.html.
    """

    records = (
        db.query(FuelPrice)
        .filter(FuelPrice.station_type == station_type)
        .filter(FuelPrice.station_id == station_id)
        .filter(FuelPrice.fuel_type.has(code=fuel))
        .order_by(FuelPrice.date.asc())
        .all()
    )

    return [
        PriceRecord(date=r.date, price=float(r.price))
        for r in records
    ]


# ================================================================
# 2. СРЕДНИЕ ЦЕНЫ КОНКУРЕНТОВ ПО ГОРОДУ (для графиков)
# ================================================================
@router.get("/avg")
def get_city_average_prices(city: str, db: Session = Depends(get_db)):
    """
    Возвращает средние цены по каждому виду топлива за каждый день.
    Используется charts.js.
    """

    city_obj = db.query(City).filter(City.name.ilike(city)).first()
    if not city_obj:
        return []

    rows = (
        db.query(
            FuelPrice.fuel_type_id,
            FuelPrice.date,
            func.avg(FuelPrice.price).label("avg_price")
        )
        .join(FuelPrice.competitor_station)
        .filter(CompetitorStation.city_id == city_obj.id)
        .group_by(FuelPrice.fuel_type_id, FuelPrice.date)
        .order_by(FuelPrice.date.asc())
        .all()
    )

    return [
        {
            "fuel_type_id": fuel_type_id,
            "date": date,
            "avg": float(avg_price)
        }
        for fuel_type_id, date, avg_price in rows
    ]


# ================================================================
# 3. РЕКОМЕНДОВАННАЯ ЦЕНА ДЛЯ НАШЕЙ СТАНЦИИ
# ================================================================
@router.get("/recommended/{station_id}")
def recommended_price(station_id: int, db: Session = Depends(get_db)):
    """
    Возвращает словарь вида:
    {
        "92": 45.10,
        "95": 48.30,
        "diesel": 49.90,
        ...
    }
    """
    station = db.query(OurStation).filter(OurStation.id == station_id).first()
    if not station:
        raise HTTPException(404, "Station not found")

    result = get_recommended_price(station_id, db)

    return {
        "station_id": station_id,
        "city": station.city.name,
        "recommended_prices": result
    }


# ================================================================
# 4. ПОСЛЕДНИЕ ЦЕНЫ СТАНЦИИ (для быстрого отображения)
# ================================================================
@router.get("/latest")
def get_latest_prices(
    station_id: int,
    station_type: StationType = StationType.competitor,
    db: Session = Depends(get_db)
):
    """
    Возвращает последние известные цены станции любого типа (нашей или конкурента).
    Удобно для отображения таблиц.
    """

    q = (
        db.query(FuelPrice)
        .filter(FuelPrice.station_type == station_type)
        .filter(FuelPrice.station_id == station_id)
        .order_by(FuelPrice.date.desc(), FuelPrice.created_at.desc())
        .all()
    )

    result = {}
    for rec in q:
        fuel_name = rec.fuel_type.code
        if fuel_name not in result:
            result[fuel_name] = float(rec.price)

    return result
