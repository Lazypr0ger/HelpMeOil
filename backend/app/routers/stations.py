from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.station import OurStation, CompetitorStation
from app.models.city import City
from app.schemas.station import OurStationBase, CompetitorStationBase


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# 1. Получение наших АЗС
# -------------------------
@router.get("/our", response_model=list[OurStationBase])
def get_our_stations(db: Session = Depends(get_db)):
    stations = db.query(OurStation).all()

    return [
        OurStationBase(
            id=s.id,
            name=s.name,
            address=s.address,
            city=s.city.name  # доступ к связанной таблице City
        )
        for s in stations
    ]


# -------------------------
# 2. Получение одной нашей АЗС
# -------------------------
@router.get("/our/{station_id}", response_model=OurStationBase)
def get_our_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(OurStation).filter(OurStation.id == station_id).first()

    if not station:
        raise HTTPException(404, "Station not found")

    return OurStationBase(
        id=station.id,
        name=station.name,
        address=station.address,
        city=station.city.name
    )


# -------------------------
# 3. Конкуренты по городу
# -------------------------
@router.get("/competitors", response_model=list[CompetitorStationBase])
def get_competitors(city: str, db: Session = Depends(get_db)):
    city_obj = db.query(City).filter(City.name.ilike(city)).first()

    if not city_obj:
        return []

    competitors = (
        db.query(CompetitorStation)
          .filter(CompetitorStation.city_id == city_obj.id)
          .all()
    )

    return [
        CompetitorStationBase(
            id=s.id,
            station_name=s.station_name,
            brand=s.brand,
            address=s.address,
            city=city_obj.name
        )
        for s in competitors
    ]
