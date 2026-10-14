from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://sentinel:sentinel@localhost:5432/secretsentinel"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    max_upload_bytes: int = 5_000_000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
