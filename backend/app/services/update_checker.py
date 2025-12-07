from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.price import FuelPrice


def need_update(db: Session, hours: int = 12) -> bool:
    """
    Проверяет, прошли ли N часов с последнего обновления цен.
    Если данных нет — запуск обязателен.
    """

    last_record = db.query(FuelPrice).order_by(FuelPrice.date.desc()).first()

    if not last_record:
        return True  # данных нет → надо парсить

    last_time = last_record.date

    # Если date — это datetime.date (без времени)
    # то считаем от полубночи
    if isinstance(last_time, datetime):
        last_dt = last_time
    else:
        last_dt = datetime.combine(last_time, datetime.min.time())

    now = datetime.now()

    return (now - last_dt) > timedelta(hours=hours)
