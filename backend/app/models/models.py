from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric, TIMESTAMP
from sqlalchemy.orm import relationship
from ..db.database import Base


# =============================
#   1. Таблица районов
# =============================
class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    # связи
    our_stations = relationship("OurStation", back_populates="district")
    competitor_stations = relationship("CompetitorStation", back_populates="district")


# =============================
#   2. Наши АЗС (HelpMeOil)
# =============================
class OurStation(Base):
    __tablename__ = "our_stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    lat = Column(Float)
    lon = Column(Float)

    district = relationship("District", back_populates="our_stations")


# =============================
#   3. Конкурирующие АЗС
# =============================
class CompetitorStation(Base):
    __tablename__ = "competitor_stations"

    id = Column(Integer, primary_key=True, index=True)
    station_name = Column(String, nullable=False)
    brand = Column(String)
    address = Column(String)
    district_id = Column(Integer, ForeignKey("districts.id"))
    lat = Column(Float)
    lon = Column(Float)

    district = relationship("District", back_populates="competitor_stations")
    prices = relationship("FuelPrice", back_populates="station")


# =============================
#   4. История цен (таймсерии)
# =============================
class FuelPrice(Base):
    __tablename__ = "fuel_prices"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("competitor_stations.id"), nullable=False)
    fuel_type = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)

    station = relationship("CompetitorStation", back_populates="prices")
