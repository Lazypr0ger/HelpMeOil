from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .parser_service import run_full_parsing
from ..models.models import FuelPrice


# Проверяем, нужно ли запускать парсер
def should_run_parser(db: Session) -> bool:
    last_price = (
        db.query(FuelPrice)
        .order_by(desc(FuelPrice.timestamp))
        .first()
    )

    if not last_price:
        # В БД нет данных → запуск обязателен
        return True

    now = datetime.now()
    age = now - last_price.timestamp

    return age > timedelta(hours=24)


# Запускаем парсер если нужно
def run_parser_if_needed(db: Session):
    if should_run_parser(db):
        print("⚡ Обновление цен — данные старше 24 часов!")
        result = run_full_parsing(db)
        print(f"✔ Парсер выполнил загрузку: {result}")
    else:
        print("⏳ Данные свежие — парсер не запускается.")
