from typing import Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.station import OurStation, CompetitorStation
from app.models.price import FuelPrice, StationType
from app.models.city import City
from app.models.fuel import FuelType


# На сколько рублей мы хотим быть дешевле средней цены конкурентов
DEFAULT_DELTA = 0.10


def get_recommended_price(our_station_id: int, db: Session) -> Optional[Dict[str, float]]:
    """
    Возвращает рекомендуемые цены для нашей станции по всем доступным видам топлива.

    Логика:
    1. Определяем город, в котором находится наша АЗС.
    2. Находим всех конкурентов в этом же городе.
    3. Считаем среднюю цену конкурентов для каждого типа топлива.
    4. Рекомендуемая цена = средняя_цена_конкурентов - DEFAULT_DELTA.
    5. Возвращаем словарь { fuel_code: recommended_price }.
    """

    # --- 1. Наша станция и её город ---
    our_station: OurStation | None = (
        db.query(OurStation)
        .filter(OurStation.id == our_station_id)
        .first()
    )

    if not our_station:
        return None

    city_id = our_station.city_id

    # --- 2. Убедимся, что город существует ---
    city: City | None = db.query(City).filter(City.id == city_id).first()
    if not city:
        return None

    # --- 3. Получаем средние цены конкурентов по каждому виду топлива ---
    # join FuelPrice -> CompetitorStation -> City
    avg_rows = (
        db.query(
            FuelPrice.fuel_type_id.label("fuel_type_id"),
            func.avg(FuelPrice.price).label("avg_price"),
        )
        .join(FuelPrice.competitor_station)           # FuelPrice -> CompetitorStation
        .join(CompetitorStation.city)                 # CompetitorStation -> City
        .filter(FuelPrice.station_type == StationType.competitor)
        .filter(City.id == city_id)
        .group_by(FuelPrice.fuel_type_id)
        .all()
    )

    if not avg_rows:
        return None

    # --- 4. Подтянем коды топлива (AI92, AI95, ...) ---
    fuel_types = {
        ft.id: ft.code
        for ft in db.query(FuelType).all()
    }

    recommendations: Dict[str, float] = {}

    for row in avg_rows:
        fuel_type_id = row.fuel_type_id
        avg_price = float(row.avg_price)

        fuel_code = fuel_types.get(fuel_type_id)
        if not fuel_code:
            continue

        # Рекомендуемую цену слегка снижаем относительно средней
        rec_price = round(max(avg_price - DEFAULT_DELTA, 0), 2)
        recommendations[fuel_code] = rec_price

    return recommendations
