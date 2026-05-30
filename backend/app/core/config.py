from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Resume Ranker API"
    database_url: str = "sqlite+pysqlite:///./local.db"
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    frontend_url: str = "http://localhost:3000"
    max_upload_mb: int = Field(default=8, ge=1, le=25)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins(self) -> list[str]:
        origins = {self.frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"}
        return [origin for origin in origins if origin]

    @property
    def cloudinary_enabled(self) -> bool:
        return all([self.cloudinary_cloud_name, self.cloudinary_api_key, self.cloudinary_api_secret])


@lru_cache
def get_settings() -> Settings:
    return Settings()

