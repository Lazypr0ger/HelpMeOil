from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric, TIMESTAMP
from sqlalchemy.orm import relationship
from ..db.database import Base


# ==============================
# 1. CITY — город
# ==============================
class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    lat = Column(Float)
    lon = Column(Float)

    our_stations = relationship("OurStation", back_populates="city")
    competitor_stations = relationship("CompetitorStation", back_populates="city")


# ==============================
# 2. НАШИ АЗС (HelpMeOil)
# ==============================
class OurStation(Base):
    __tablename__ = "our_stations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    lat = Column(Float)
    lon = Column(Float)

    city = relationship("City", back_populates="our_stations")


# ==============================
# 3. Конкурирующие АЗС
# ==============================
class CompetitorStation(Base):
    __tablename__ = "competitor_stations"

    id = Column(Integer, primary_key=True)
    station_name = Column(String, nullable=False)
    brand = Column(String)
    address = Column(String)
    city_id = Column(Integer, ForeignKey("cities.id"))
    lat = Column(Float)
    lon = Column(Float)

    city = relationship("City", back_populates="competitor_stations")
    prices = relationship("FuelPrice", back_populates="station")


# ==============================
# 4. История цен
# ==============================
class FuelPrice(Base):
    __tablename__ = "fuel_prices"

    id = Column(Integer, primary_key=True)
    station_id = Column(Integer, ForeignKey("competitor_stations.id"))
    fuel_type = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)

    station = relationship("CompetitorStation", back_populates="prices")
