from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from typing import List

from app.core.database import get_db
from app.models.station import OurStation, CompetitorStation
from app.models.price import FuelPrice, RecommendedPrice
from app.models.fuel import FuelType

from pydantic import BaseModel


router = APIRouter(prefix="/our-stations", tags=["our stations"])


# --------------------------------------------------
# NORMALIZATION (единая схема топлива для фронта)
# --------------------------------------------------

def normalize_code(code: str):
    code = code.upper()
    match code:
        case "92": return "AI92"
        case "95": return "AI95"
        case "ДТ" | "DT" | "DIESEL": return "DIESEL"
        case "ГАЗ" | "GAS": return "GAS"
    return code


# --------------------------------------------------
# SCHEMAS
# --------------------------------------------------

class OurStationOut(BaseModel):
    id: int
    name: str
    address: str
    city_name: str
    latest_prices: dict

    class Config:
        from_attributes = True


# --------------------------------------------------
# 1️⃣ СПИСОК НАШИХ АЗС
# --------------------------------------------------

@router.get("/", response_model=List[OurStationOut])
def get_our_stations(db: Session = Depends(get_db)):
    stations = db.query(OurStation).all()
    result = []

    for s in stations:

        # последние цены
        subq = (
            db.query(
                FuelPrice.fuel_type_id,
                func.max(FuelPrice.date).label("mx")
            )
            .filter(FuelPrice.our_station_id == s.id)
            .group_by(FuelPrice.fuel_type_id)
            .subquery()
        )

        rows = (
            db.query(FuelPrice)
            .join(subq,
                  (FuelPrice.fuel_type_id == subq.c.fuel_type_id) &
                  (FuelPrice.date == subq.c.mx))
            .all()
        )

        # нормализация ключей
        prices = {normalize_code(r.fuel_type.code): float(r.price) for r in rows}

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


# --------------------------------------------------
# 2️⃣ ДЕТАЛИ ОДНОЙ НАШЕЙ АЗС
# --------------------------------------------------

@router.get("/{station_id}", response_model=OurStationOut)
def station_details(station_id: int, db: Session = Depends(get_db)):
    st = db.query(OurStation).filter_by(id=station_id).first()
    if not st:
        raise HTTPException(404, "Станция не найдена")

    subq = (
        db.query(
            FuelPrice.fuel_type_id,
            func.max(FuelPrice.date).label("mx")
        )
        .filter(FuelPrice.our_station_id == station_id)
        .group_by(FuelPrice.fuel_type_id)
        .subquery()
    )

    rows = (
        db.query(FuelPrice)
        .join(subq,
              (FuelPrice.fuel_type_id == subq.c.fuel_type_id) &
              (FuelPrice.date == subq.c.mx))
        .all()
    )

    prices = {normalize_code(r.fuel_type.code): float(r.price) for r in rows}

    return OurStationOut(
        id=st.id,
        name=st.name,
        address=st.address,
        city_name=st.city.name,
        latest_prices=prices
    )


# --------------------------------------------------
# 3️⃣ КОНКУРЕНТЫ В ГОРОДЕ + их последние цены
# --------------------------------------------------

@router.get("/{station_id}/competitors")
def get_competitors_for_our(station_id: int, db: Session = Depends(get_db)):
    st = db.query(OurStation).filter_by(id=station_id).first()
    if not st:
        raise HTTPException(404, "Станция не найдена")

    competitors = (
        db.query(CompetitorStation)
        .filter(CompetitorStation.city_id == st.city_id)
        .all()
    )

    result = []

    for c in competitors:
        # последние цены конкурента
        subq = (
            db.query(
                FuelPrice.fuel_type_id,
                func.max(FuelPrice.date).label("mx")
            )
            .filter(FuelPrice.competitor_station_id == c.id)
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

        prices = {
            normalize_code(r.fuel_type.code): float(r.price)
            for r in rows
        }

        result.append({
            "station_name": c.station_name,
            "prices": prices
        })

    return result


# --------------------------------------------------
# 4️⃣ ИСТОРИЯ ЦЕН В НУЖНОМ ДЛЯ ФРОНТА ФОРМАТЕ
# --------------------------------------------------

@router.get("/{station_id}/history")
def get_price_history(station_id: int, db: Session = Depends(get_db)):
    st = db.query(OurStation).filter_by(id=station_id).first()
    if not st:
        raise HTTPException(404, "Станция не найдена")

    # 1. История нашей станции
    rows = (
        db.query(FuelPrice)
        .filter(FuelPrice.our_station_id == station_id)
        .order_by(FuelPrice.date)
        .all()
    )

    if rows:  # если есть данные — возвращаем их
        result = {}
        for p in rows:
            d = p.date.isoformat()
            fuel = normalize_code(p.fuel_type.code)

            if d not in result:
                result[d] = {"date": d}

            result[d][fuel] = float(p.price)

        return list(result.values())

    # 2. Если данных нет — строим историю средней цены по городу
    city_rows = (
        db.query(
            FuelPrice.date,
            FuelType.code,
            func.avg(FuelPrice.price)
        )
        .join(FuelType, FuelType.id == FuelPrice.fuel_type_id)
        .join(CompetitorStation, CompetitorStation.id == FuelPrice.competitor_station_id)
        .filter(CompetitorStation.city_id == st.city_id)
        .group_by(FuelPrice.date, FuelType.code)
        .order_by(FuelPrice.date)
        .all()
    )

    history = {}

    for date, fuel_code, avg_price in city_rows:
        d = date.isoformat()
        fuel = normalize_code(fuel_code)

        if d not in history:
            history[d] = {"date": d}

        history[d][fuel] = round(float(avg_price), 2)

    return list(history.values())



# --------------------------------------------------
# 5️⃣ СРЕДНЯЯ ЦЕНА ПО ГОРОДУ ДЛЯ ВЕРХНЕЙ ПЛАШКИ
# --------------------------------------------------

@router.get("/{station_id}/city-avg")
def get_city_avg(station_id: int, db: Session = Depends(get_db)):
    st = db.query(OurStation).filter_by(id=station_id).first()
    if not st:
        raise HTTPException(404, "Станция не найдена")

    rows = (
        db.query(
            FuelType.code,
            func.avg(FuelPrice.price)
        )
        .join(FuelPrice, FuelPrice.fuel_type_id == FuelType.id)
        .join(CompetitorStation, CompetitorStation.id == FuelPrice.competitor_station_id)
        .filter(CompetitorStation.city_id == st.city_id)
        .group_by(FuelType.code)
        .all()
    )

    result = {}

    for code, avg in rows:
        result[normalize_code(code)] = round(float(avg), 2)

    return result

@router.get("/{station_id}/recommended")
def get_recommended(station_id: int, db: Session = Depends(get_db)):
    st = db.query(OurStation).filter_by(id=station_id).first()
    if not st:
        raise HTTPException(404, "Станция не найдена")

    rows = (
        db.query(RecommendedPrice)
        .filter(RecommendedPrice.our_station_id == station_id)
        .order_by(RecommendedPrice.date.desc())
        .all()
    )

    result = {}
    for r in rows:
        code = r.fuel_type.code
        if code not in result:  # берём только самую свежую цену
            result[code] = float(r.price)

    return result

@router.get("/{station_id}/recommended/history")
def get_recommended_history(station_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(RecommendedPrice)
        .filter(RecommendedPrice.our_station_id == station_id)
        .order_by(RecommendedPrice.date)
        .all()
    )

    history = {}
    for r in rows:
        d = r.date.isoformat()
        if d not in history:
            history[d] = {"date": d}
        history[d][r.fuel_type.code] = float(r.price)

    return list(history.values())
