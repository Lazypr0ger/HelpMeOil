from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.parser_service import run_full_parsing

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/force")
def force_update(db: Session = Depends(get_db)):
    """
    Принудительное обновление данных.
    Запускаем полный цикл парсинга независимо от таймера.
    """
    df = run_full_parsing(db)
    return {
        "status": "success",
        "rows_processed": len(df),
        "message": "Данные обновлены принудительно."
    }
