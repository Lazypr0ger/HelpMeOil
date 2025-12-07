from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import engine, Base, get_db
from .routers import stations, prices
from .services.parser_service import run_full_parsing

from sqlalchemy.orm import Session
import datetime


app = FastAPI(title="HelpMeOil API")


# ==========================================================
# CORS настройки
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # можно ограничить при необходимости
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# Создаем таблицы, если их нет
# ==========================================================
Base.metadata.create_all(bind=engine)


# ==========================================================
# Нужно ли обновлять парсер раз в 24 часа?
# ==========================================================
def need_parse(db: Session):
    from .models.models import FuelPrice

    last = db.query(FuelPrice).order_by(FuelPrice.timestamp.desc()).first()
    if not last:
        return True

    diff = datetime.datetime.now() - last.timestamp
    return diff.total_seconds() > 24 * 3600


# ==========================================================
# Автоматический запуск парсера при старте API
# ==========================================================
@app.on_event("startup")
def startup_event():
    db = next(get_db())

    try:
        if need_parse(db):
            print("=== ЗАПУСК ЕЖЕДНЕВНОГО ПАРСЕРА ===")
            result = run_full_parsing(db)
            print("Парсинг завершён:", result)
        else:
            print("Парсер не нужен — данные свежие (<24h)")
    except Exception as e:
        print("Ошибка во время запуска парсера:", e)


# ==========================================================
# Подключение роутеров (БЕЗ повторного prefix!)
# ==========================================================
app.include_router(stations.router)   # В stations.py prefix="/stations"
app.include_router(prices.router)     # В prices.py prefix="/prices"

# при необходимости можно подключить новый роутер:
# app.include_router(analytics.router)
