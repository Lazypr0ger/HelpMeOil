from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

    competitor_stations = relationship(
        "CompetitorStation", back_populates="city", cascade="all, delete-orphan"
    )
    our_stations = relationship(
        "OurStation", back_populates="city", cascade="all, delete-orphan"
    )
