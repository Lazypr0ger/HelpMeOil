from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..models.models import District, OurStation, CompetitorStation

router = APIRouter()

# ==========================================================
#                1. Получить наши АЗС (GET /stations/our)
# ==========================================================
@router.get("/our")
def get_our_stations(db: Session = Depends(get_db)):
    return db.query(OurStation).all()


# ==========================================================
#           2. Получить одну АЗС (GET /stations/our/{id})
# ==========================================================
@router.get("/our/{station_id}")
def get_one_our_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(OurStation).filter(OurStation.id == station_id).first()
    if not station:
        raise HTTPException(404, "Our station not found")
    return station


# ==========================================================
#     3. Получить конкурентов в районе (GET /stations/competitors)
# ==========================================================
@router.get("/competitors")
def get_competitors(district: str, db: Session = Depends(get_db)):
    district_obj = db.query(District).filter(District.name == district).first()

    if not district_obj:
        return []  # если район нет в БД

    competitors = db.query(CompetitorStation).filter(
        CompetitorStation.district_id == district_obj.id
    ).all()

    return competitors


# ==========================================================
#        4. Добавить наш район (POST /stations/district)
# ==========================================================
@router.post("/district")
def add_district(name: str, db: Session = Depends(get_db)):
    district = District(name=name)
    db.add(district)
    db.commit()
    db.refresh(district)
    return district


# ==========================================================
#        5. Добавить нашу АЗС (POST /stations/our)
# ==========================================================
@router.post("/our")
def add_our_station(name: str, district_id: int, db: Session = Depends(get_db)):
    station = OurStation(name=name, district_id=district_id)
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


# ==========================================================
#   6. Добавить станцию-конкурента (POST /stations/competitor)
# ==========================================================
@router.post("/competitor")
def add_competitor(
    station_name: str,
    brand: str,
    address: str,
    district_id: int,
    db: Session = Depends(get_db)
):
    competitor = CompetitorStation(
        station_name=station_name,
        brand=brand,
        address=address,
        district_id=district_id,
    )
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return competitor
