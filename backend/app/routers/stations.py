from fastapi import APIRouter, HTTPException

router = APIRouter()

# =============================
# Временные данные — наши АЗС
# =============================
OUR_STATIONS = [
    {"id": 1, "name": "HelpMeOil — Засвияжье", "district": "Засвияжский район"},
    {"id": 2, "name": "HelpMeOil — Центр", "district": "Ленинский район"},
    {"id": 3, "name": "HelpMeOil — Заволжье", "district": "Заволжский район"},
    {"id": 4, "name": "HelpMeOil — Железка", "district": "Железнодорожный район"},
    {"id": 5, "name": "HelpMeOil — Чердаклы", "district": "Чердаклинский район"},
]

# =============================
# Временная база конкурентов
# (позже заменим на реальный датасет)
# =============================
DUMMY_COMPETITORS = [
    {
        "station_name": "Татнефть №540",
        "district": "Засвияжский район",
        "Аи-92": 59.10,
        "Аи-95": 63.85,
        "Аи-95+": None,
        "Аи-98": None,
        "ДТ": 70.15,
        "Газ": 28.00
    },
    {
        "station_name": "ЛУКОЙЛ №73231",
        "district": "Засвияжский район",
        "Аи-92": 61.89,
        "Аи-95": 66.54,
        "Аи-95+": None,
        "Аи-98": None,
        "ДТ": 71.75,
        "Газ": 28.19
    }
]


# ==========================================================
#                1. Все наши АЗС (GET /stations/our)
# ==========================================================
@router.get("/our")
async def get_our_stations():
    return OUR_STATIONS


# ==========================================================
#             2. Одна наша АЗС (GET /stations/our/{id})
# ==========================================================
@router.get("/our/{station_id}")
async def get_one_station(station_id: int):
    for st in OUR_STATIONS:
        if st["id"] == station_id:
            return st
    raise HTTPException(status_code=404, detail="Station not found")


# ==========================================================
#           3. Конкуренты в районе (GET /stations/competitors)
# ==========================================================
@router.get("/competitors")
async def get_competitors(district: str):
    competitors = [
        comp for comp in DUMMY_COMPETITORS
        if comp["district"].lower().startswith(district.lower())
    ]

    if not competitors:
        return []

    return competitors
