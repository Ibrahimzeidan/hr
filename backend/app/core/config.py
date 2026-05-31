from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Resume Ranker API"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/resume_ranker"
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    frontend_url: str = "http://localhost:3000"
    max_upload_mb: int = Field(default=8, ge=1, le=25)

    # Google Gemini AI configuration
    # Optional: If GEMINI_API_KEY is not set, the system uses deterministic local fallback
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"

    # Supabase configuration (optional - only needed if using Supabase features beyond PostgreSQL)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_project_ref: str = ""

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

