from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.database import engine, Base, get_db
from .routers import stations, prices
from .services.parser_service import run_full_parsing
from sqlalchemy.orm import Session

import datetime

app = FastAPI(title="HelpMeOil API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Создаем таблицы
Base.metadata.create_all(bind=engine)


def need_parse(db: Session):
    """Нужно ли обновлять парсер (24 часа)?"""

    from .models.models import FuelPrice

    last = db.query(FuelPrice).order_by(FuelPrice.timestamp.desc()).first()
    if not last:
        return True

    diff = datetime.datetime.now() - last.timestamp
    return diff.total_seconds() > 24 * 3600


# Запуск при старте
@app.on_event("startup")
def startup_event():
    db = next(get_db())

    if need_parse(db):
        print("=== ЗАПУСК ЕЖЕДНЕВНОГО ПАРСЕРА ===")
        result = run_full_parsing(db)
        print("Парсинг завершён:", result)
    else:
        print("Парсер не нужен — данные свежие (<24h)")


# Роутеры
app.include_router(stations.router, prefix="/stations")
app.include_router(prices.router, prefix="/prices")
