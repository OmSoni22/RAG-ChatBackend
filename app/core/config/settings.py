from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str
    debug: bool

    database_url: str

    redis_enabled: bool = False
    redis_url: str | None = None

    log_level: str
    log_dir: str

    class Config:
        env_file = ".env"

settings = Settings()
