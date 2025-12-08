from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.price import FuelPrice
from app.models.fuel import FuelType
from sqlalchemy import func

router = APIRouter(prefix="/analytics/market", tags=["analytics"])


@router.get("/avg")
def market_average(db: Session = Depends(get_db)):
    rows = (
        db.query(
            FuelType.code,
            func.avg(FuelPrice.price)
        )
        .join(FuelPrice, FuelPrice.fuel_type_id == FuelType.id)
        .filter(FuelPrice.competitor_station_id.isnot(None))
        .group_by(FuelType.code)
        .all()
    )

    return {code: float(avg) for code, avg in rows}


@router.get("/history")
def market_history(db: Session = Depends(get_db)):
    rows = (
        db.query(
            FuelPrice.date,
            FuelType.code,
            func.avg(FuelPrice.price)
        )
        .join(FuelType, FuelPrice.fuel_type_id == FuelType.id)
        .filter(FuelPrice.competitor_station_id.isnot(None))
        .group_by(FuelPrice.date, FuelType.code)
        .order_by(FuelPrice.date)
        .all()
    )
    
    result = {}
    for date, fuel, avg in rows:
        d = date.isoformat()
        if d not in result:
            result[d] = {"date": d}
        result[d][fuel] = float(avg)

    return list(result.values())
