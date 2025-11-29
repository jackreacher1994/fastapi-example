from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_path = Path(__file__).parent / ".env"

class Settings(BaseSettings):
    database_url: str
    database_url_for_migration: str
    log_level: str
    celery_broker_url: str
    celery_result_backend: str

    model_config = SettingsConfigDict(env_file=str(_env_path))

settings = Settings()