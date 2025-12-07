from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/prices", tags=["prices"])

# Временная история цен (заглушка)
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
    ],
}


@router.get("/history")
async def get_price_history(station: str, fuel: str):
    if fuel not in DUMMY_HISTORY:
        raise HTTPException(404, "Нет данных по данному топливу")
    return DUMMY_HISTORY[fuel]
