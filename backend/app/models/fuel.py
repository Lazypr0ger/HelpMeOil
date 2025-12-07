from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class FuelType(Base):
    __tablename__ = "fuel_types"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)   # AI92, DIESEL...
    name = Column(String, unique=True, nullable=False)   # "Аи-92", "ДТ"...

    prices = relationship("FuelPrice", back_populates="fuel_type")
