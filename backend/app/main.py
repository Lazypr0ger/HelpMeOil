from fastapi import FastAPI
from app.core.database import Base, engine, SessionLocal
from app.services.update_checker import need_update
from app.services.parser_service import run_full_parsing
from app.services.init_db import init_db
from app.routers import update

app = FastAPI(title="HelpMeOil API")
app.include_router(update.router, prefix="/update", tags=["update"])
#app.include_router(stations.router, prefix="/stations", tags=["stations"])
#app.include_router(prices.router,   prefix="/prices", tags=["prices"])
app.include_router(update.router,   prefix="/update", tags=["update"])

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # 1. Создаём справочники
        init_db(db)

        # 2. Проверяем нужно ли обновить данные
        if need_update(db):
            print("[INFO] Обновление данных: прошло > 12 часов → запускаем парсер…")
            try:
                run_full_parsing(db)
            except Exception as e:
                print("[WARN] Parser failed during startup:", e)

            else:
                print("[INFO] Данные свежие — парсер не требуется.")
    finally:
        db.close()