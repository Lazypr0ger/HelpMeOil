from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.database import Base, engine
from .routers import stations, prices
from .models import models  

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="HelpMeOil API",
    description="API для системы мониторинга цен на топливо HelpMeOil",
    version="0.1.0",
)

# Разрешаем запросы с фронтенда (статический HTML, открытый в браузере)
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://localhost:5500",    # если вдруг будешь запускать через Live Server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно сузить до origins, когда всё отладим
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "HelpMeOil API is running"}


# Подключение роутеров (позже создадим их)
app.include_router(stations.router, prefix="/stations", tags=["stations"])
app.include_router(prices.router, prefix="/prices", tags=["prices"])
