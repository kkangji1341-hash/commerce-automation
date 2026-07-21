import os
from dotenv import load_dotenv

load_dotenv()


def _normalize_database_url(url: str) -> str:
    """Railway/Heroku 등이 주입하는 postgres(ql):// URL을 asyncpg 드라이버 스킴으로 변환."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://") :]
    return url


class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Commerce Automation API"
    DATABASE_URL: str = _normalize_database_url(
        os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./commerce_automation.db")
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

settings = Settings()
