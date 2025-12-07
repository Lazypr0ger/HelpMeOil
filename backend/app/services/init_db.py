from sqlalchemy.orm import Session
from app.models.fuel import FuelType




DEFAULT_FUELS = [
    ("AI92", "АИ-92"),
    ("AI95", "АИ-95"),
    ("DIESEL", "ДТ"),
    ("GAS", "Газ"),
]


def init_fuel_types(db: Session):
    existing = db.query(FuelType).count()
    if existing > 0:
        return

    fuel_types = [
        ("AI92", "Аи-92"),
        ("AI95", "Аи-95"),
        ("DIESEL", "ДТ"),
        ("GAS", "Газ"),
    ]

    for code, name in fuel_types:
        db.add(FuelType(code=code, name=name))

    db.commit()
def init_db(db: Session):
    """
    Запускается при старте приложения.
    Создаёт справочники и базовые записи.
    """
    init_fuel_types(db)