from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str
    debug: bool

    database_url: str

    log_level: str
    log_dir: str

    # Google AI / Embedding config
    google_api_key: str
    embedding_model: str = "gemini-embedding-001"
    embedding_dims: int = 3072  # must match Vector(n) in the model and the DB column
    llm_model: str = "gemini-2.0-flash"
    top_k_context: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
