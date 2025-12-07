from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.price import FuelPrice, StationType
from app.models.station import OurStation


def get_recommended_price(station_id: int, db: Session):
    """
    Простейшая модель рекомендаций:
    - Берём среднюю цену конкурентов по каждому виду топлива
    - Делаем цену нашего топлива = средняя - 0.10 руб
    """

    our = db.query(OurStation).filter(OurStation.id == station_id).first()
    if not our:
        return None

    city_id = our.city_id

    q = (
        db.query(
            FuelPrice.fuel_type_id,
            func.avg(FuelPrice.price).label("avg_price")
        )
        .filter(FuelPrice.station_type == StationType.competitor)
        .filter(FuelPrice.competitor_station.has(city_id=city_id))
        .group_by(FuelPrice.fuel_type_id)
        .all()
    )

    recommendations = {}

    for fuel_type_id, avg_price in q:
        recommendations[fuel_type_id] = round(float(avg_price) - 0.10, 2)

    return recommendations
