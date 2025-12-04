from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..services.parser_service import run_full_parsing

router = APIRouter(prefix="/parser", tags=["Parser"])


@router.post("/run")
def run_parser(db: Session = Depends(get_db)):
    """
    Запуск полного парсинга и сохранения в БД.
    """
    result = run_full_parsing(db)
    return {
        "status": "ok",
        "message": f"Парсинг завершён. Получено АЗС: {result['stations']}, записано цен: {result['prices']}"
    }
