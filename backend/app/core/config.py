from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://helpmeoil:helpmeoil_pass@localhost:5432/helpmeoil_db"

    class Config:
        env_file = ".env"


settings = Settings()
