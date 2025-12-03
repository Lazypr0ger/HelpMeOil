from fastapi import APIRouter, HTTPException

router = APIRouter()

# =============================
# Временная история цен
# (позже заменим реальными таймсериями из CSV / PostgreSQL)
# =============================
DUMMY_HISTORY = {
    "Аи-95": [
        {"timestamp": "2025-12-01 12:00", "price": 63.85},
        {"timestamp": "2025-12-02 12:00", "price": 63.90},
        {"timestamp": "2025-12-03 12:00", "price": 63.80},
    ],
    "Аи-92": [
        {"timestamp": "2025-12-01 12:00", "price": 59.10},
        {"timestamp": "2025-12-02 12:00", "price": 59.20},
        {"timestamp": "2025-12-03 12:00", "price": 59.00},
    ],
    "Газ": [
        {"timestamp": "2025-12-01 12:00", "price": 28.0},
        {"timestamp": "2025-12-02 12:00", "price": 28.1},
        {"timestamp": "2025-12-03 12:00", "price": 28.0},
    ]
}

# =============================
# Временная таблица конкурентов (для recommendation)
# =============================
DUMMY_COMPETITORS = [
    {"Аи-95": 63.85},
    {"Аи-95": 66.54},
    {"Аи-95": 64.99}
]


# ==========================================================
#            1. История цен (GET /prices/history)
# ==========================================================
@router.get("/history")
async def get_price_history(station: str, fuel: str):
    if fuel not in DUMMY_HISTORY:
        raise HTTPException(404, "Нет данных по данному топливу")

    # В будущем здесь будет запрос в БД: SELECT * FROM fuel_prices ...
    return DUMMY_HISTORY[fuel]


# ==========================================================
#            2. Рекомендованная цена
# ==========================================================
@router.get("/recommended/{station_id}")
async def get_recommended_price(station_id: int):
    # Ищем минимальную цену конкурентов (по AI-95 пока)
    prices = [c["Аи-95"] for c in DUMMY_COMPETITORS if c["Аи-95"]]

    if not prices:
        return {"station_id": station_id, "price": None}

    min_price = min(prices)

    recommended = round(min_price - 0.20, 2)

    return {
        "station_id": station_id,
        "price": recommended
    }
