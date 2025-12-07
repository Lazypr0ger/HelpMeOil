import datetime
from sqlalchemy.orm import Session
from app.models.price import FuelPrice


def need_update(db: Session) -> bool:
    """
    Проверяем, нужно ли запускать парсер.
    Условие: если последняя запись старше 12 часов.
    """
    last_record = db.query(FuelPrice).order_by(FuelPrice.created_at.desc()).first()

    if not last_record:
        return True  # данных нет → нужно обновлять

    now = datetime.datetime.utcnow()
    diff = now - last_record.created_at

    return diff.total_seconds() > 12 * 3600
