from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..db.database import get_db
from ..models.models import City, OurStation, CompetitorStation, FuelPrice

router = APIRouter()


# ---------------------------------------------------------
# 1. Список городов
# ---------------------------------------------------------
@router.get("/cities")
def get_cities(db: Session = Depends(get_db)):
    return db.query(City).all()


@router.post("/cities")
def create_city(name: str, lat: float, lon: float, db: Session = Depends(get_db)):
    city = City(name=name, lat=lat, lon=lon)
    db.add(city)
    db.commit()
    db.refresh(city)
    return city


# ---------------------------------------------------------
# 2. Наши станции
# ---------------------------------------------------------
@router.get("/our")
def get_our_stations(db: Session = Depends(get_db)):
    stations = db.query(OurStation).all()

    result = []
    for st in stations:
        city = db.query(City).filter(City.id == st.city_id).first()
        result.append({
            "id": st.id,
            "name": st.name,
            "city": city.name if city else None
        })

    return result


@router.get("/our/{station_id}")
def get_one_our_station(station_id: int, db: Session = Depends(get_db)):
    st = db.query(OurStation).filter(OurStation.id == station_id).first()
    if not st:
        raise HTTPException(404, "station not found")

    city = db.query(City).filter(City.id == st.city_id).first()

    return {
        "id": st.id,
        "name": st.name,
        "city": city.name if city else None
    }


@router.post("/our")
def add_our_station(name: str, city_id: int, db: Session = Depends(get_db)):
    st = OurStation(name=name, city_id=city_id)
    db.add(st)
    db.commit()
    db.refresh(st)
    return st


# ---------------------------------------------------------
# 3. Конкуренты — по городам
# ---------------------------------------------------------
@router.get("/competitors")
def get_competitors(city: str, db: Session = Depends(get_db)):
    city_obj = db.query(City).filter(City.name == city).first()
    if not city_obj:
        return []

    competitors = db.query(CompetitorStation).filter(
        CompetitorStation.city_id == city_obj.id
    ).all()

    result = []

    for c in competitors:
        row = {"station_name": c.station_name}

        for fuel in ["Аи-92", "Аи-95", "Аи-95+", "Аи-98", "ДТ", "Газ"]:
            last_price = (
                db.query(FuelPrice)
                .filter(
                    FuelPrice.station_id == c.id,
                    FuelPrice.fuel_type == fuel
                )
                .order_by(desc(FuelPrice.timestamp))
                .first()
            )

            row[fuel] = float(last_price.price) if last_price else None

        result.append(row)

    return result


# ---------------------------------------------------------
# 4. Создать конкурента вручную
# ---------------------------------------------------------
@router.post("/competitor")
def add_competitor(station_name: str, brand: str, address: str, city_id: int,
                   db: Session = Depends(get_db)):
    st = CompetitorStation(
        station_name=station_name,
        brand=brand,
        address=address,
        city_id=city_id
    )
    db.add(st)
    db.commit()
    db.refresh(st)
    return st
