from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class CompetitorStation(Base):
    __tablename__ = "competitor_stations"

    id = Column(Integer, primary_key=True, index=True)
    station_name = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    address = Column(String, nullable=True)

    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

    city = relationship("City", back_populates="competitor_stations")
    prices = relationship("FuelPrice", back_populates="competitor_station")


class OurStation(Base):
    __tablename__ = "our_stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)

    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    district = Column(String, nullable=True)  # под charts.js, если понадобится

    city = relationship("City", back_populates="our_stations")
    prices = relationship("FuelPrice", back_populates="our_station")
