from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    competitor_stations = relationship("CompetitorStation", back_populates="city")
    our_stations = relationship("OurStation", back_populates="city")
