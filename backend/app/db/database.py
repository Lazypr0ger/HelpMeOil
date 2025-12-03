from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "helpmeoil")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "helpmeoil_pass")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "helpmeoil_db")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Создаём движок
engine = create_engine(DATABASE_URL, echo=True)

# Создаём фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс ORM-моделей
Base = declarative_base()


# Зависимость FastAPI для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
