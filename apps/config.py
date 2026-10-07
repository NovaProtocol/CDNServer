from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CDN_ROOT = PROJECT_ROOT / "cdn"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
DATA_DIR = PROJECT_ROOT / "data"
VENDOR_DIR = DATA_DIR / "vendor"


class Settings(BaseSettings):
    DEPLOYMENT_TYPE: str = "debug"
    SECRET_KEY: str = Field(min_length=32, description="CSRF/session signing key, >=32 chars")

    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASS: str = ""
    MYSQL_DATABASE: str = "cdnserver"

    # Tests set this to sqlite+aiosqlite:///:memory:; compose never sets it, in which
    # case it is built from the MYSQL_* values (per reference/docker/mysql.md).
    DATABASE_URL: str | None = None

    model_config = SettingsConfigDict(extra="ignore", populate_by_name=True)

    @property
    def debug(self) -> bool:
        return self.DEPLOYMENT_TYPE.lower() == "debug"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASS}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
        )


Config = Settings


@lru_cache
def get_config() -> Settings:
    return Settings()
