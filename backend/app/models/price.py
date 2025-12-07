from datetime import date, datetime

from sqlalchemy import (
    Column, Integer, Numeric, Date, DateTime,
    Enum, ForeignKey
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class StationType(str, enum.Enum):
    competitor = "competitor"
    our = "our"


class FuelPrice(Base):
    __tablename__ = "fuel_prices"

    id = Column(Integer, primary_key=True, index=True)

    station_id = Column(Integer, nullable=False)
    station_type = Column(
        Enum(StationType, name="station_type_enum"),
        nullable=False
    )

    fuel_type_id = Column(Integer, ForeignKey("fuel_types.id"), nullable=False)

    price = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, default=date.today, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # связи
    fuel_type = relationship("FuelType", back_populates="prices")

    # удобные связи (опциональные, но полезные)
    competitor_station_id = Column(
        Integer,
        ForeignKey("competitor_stations.id"),
        nullable=True
    )
    our_station_id = Column(
        Integer,
        ForeignKey("our_stations.id"),
        nullable=True
    )

    competitor_station = relationship(
        "CompetitorStation",
        back_populates="prices",
        foreign_keys=[competitor_station_id],
    )
    our_station = relationship(
        "OurStation",
        back_populates="prices",
        foreign_keys=[our_station_id],
    )
