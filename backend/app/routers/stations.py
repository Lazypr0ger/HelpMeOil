from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..db.database import get_db
from ..models.models import District, OurStation, CompetitorStation, FuelPrice

router = APIRouter()

# ==========================================================
#                1. Получить наши АЗС (GET /stations/our)
# ==========================================================
@router.get("/our")
def get_our_stations(db: Session = Depends(get_db)):
    stations = db.query(OurStation).all()

    # Добавим название района (чтобы фронтенд мог показать district)
    result = []
    for st in stations:
        district = db.query(District).filter(District.id == st.district_id).first()
        result.append({
            "id": st.id,
            "name": st.name,
            "district": district.name if district else "Не указан",
        })

    return result


# ==========================================================
#           2. Получить одну АЗС (GET /stations/our/{id})
# ==========================================================
@router.get("/our/{station_id}")
def get_one_our_station(station_id: int, db: Session = Depends(get_db)):
    station = db.query(OurStation).filter(OurStation.id == station_id).first()
    if not station:
        raise HTTPException(404, "Our station not found")

    district = db.query(District).filter(District.id == station.district_id).first()

    return {
        "id": station.id,
        "name": station.name,
        "district": district.name if district else "Не указан"
    }


# ==========================================================
#     3. Получить конкурентов + их последние цены
#        (GET /stations/competitors?district=Засвияжский)
# ==========================================================
@router.get("/competitors")
def get_competitors(district: str, db: Session = Depends(get_db)):
    district_obj = db.query(District).filter(District.name == district).first()
    if not district_obj:
        return []

    competitors = (
        db.query(CompetitorStation)
        .filter(CompetitorStation.district_id == district_obj.id)
        .all()
    )

    result = []

    for c in competitors:
        latest_prices = {}

        for fuel in ["Аи-92", "Аи-95", "Аи-95+", "Аи-98", "ДТ", "Газ"]:
            price_obj = (
                db.query(FuelPrice)
                .filter(
                    FuelPrice.station_id == c.id,
                    FuelPrice.fuel_type == fuel
                )
                .order_by(desc(FuelPrice.timestamp))
                .first()
            )

            latest_prices[fuel] = (
                float(price_obj.price) if price_obj else None
            )

        result.append({
            "station_name": c.station_name,
            **latest_prices
        })

    return result


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
