from sqlalchemy.orm import Session
from app.models.fuel import FuelType




DEFAULT_FUELS = [
    ("AI92", "АИ-92"),
    ("AI95", "АИ-95"),
    ("DIESEL", "ДТ"),
    ("GAS", "Газ"),
]


def init_fuel_types(db: Session):
    """
    Создаёт справочник видов топлива, если он пустой.
    """
    existing = db.query(FuelType).count()
    if existing > 0:
        return

    for code, name in DEFAULT_FUELS:
        db.add(FuelType(code=code, name=name))

    db.commit()
    print("[INIT] fuel_types заполнены.")

def init_db(db: Session):
    """
    Запускается при старте приложения.
    Создаёт справочники и базовые записи.
    """
    init_fuel_types(db)