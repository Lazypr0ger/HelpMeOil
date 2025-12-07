from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class StationType(enum.Enum):
    our = "our"
    competitor = "competitor"


class FuelPrice(Base):
    __tablename__ = "fuel_prices"

    id = Column(Integer, primary_key=True)

    station_type = Column(Enum(StationType), nullable=False)

    competitor_station_id = Column(Integer, ForeignKey("competitor_stations.id"))
    our_station_id = Column(Integer, ForeignKey("our_stations.id"))

    fuel_type_id = Column(Integer, ForeignKey("fuel_types.id"), nullable=False)
    price = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)

    competitor_station = relationship("CompetitorStation", back_populates="prices")
    our_station = relationship("OurStation", back_populates="prices")

    fuel_type = relationship("FuelType", back_populates="prices")
