# app/services/pricing_service.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.price import FuelPrice, RecommendedPrice
from app.models.station import OurStation, CompetitorStation
from app.models.fuel import FuelType
import datetime

MARGIN = 0.30   # 30 копеек

def generate_recommended_prices(db: Session):
    today = datetime.date.today()

    our_stations = db.query(OurStation).all()
    fuel_types = db.query(FuelType).all()

    for st in our_stations:
        city_id = st.city_id

        for ft in fuel_types:

            # Берём данные конкурентов
            row = (
                db.query(func.min(FuelPrice.price))
                .join(CompetitorStation, CompetitorStation.id == FuelPrice.competitor_station_id)
                .filter(
                    CompetitorStation.city_id == city_id,
                    FuelPrice.fuel_type_id == ft.id
                )
                .first()
            )

            if row is None or row[0] is None:
                continue

            min_price = float(row[0])
            recommended_price = round(min_price + MARGIN, 2)

            rec = RecommendedPrice(
                our_station_id=st.id,
                fuel_type_id=ft.id,
                price=recommended_price,
                date=today,
            )

            db.add(rec)

    db.commit()
