"""Configuración del agente cargada desde variables de entorno."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parámetros de ejecución del Asistente de Consulta de Pólizas."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    google_cloud_project: str | None = Field(default=None, alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="us-central1", alias="GOOGLE_CLOUD_LOCATION")
    google_genai_use_vertexai: bool = Field(default=True, alias="GOOGLE_GENAI_USE_VERTEXAI")
    model: str = Field(default="gemini-2.5-flash", alias="MODEL")
    firestore_collection: str = Field(default="polizas", alias="FIRESTORE_COLLECTION")
    repository_backend: Literal["firestore", "memory"] = Field(
        default="memory", alias="REPOSITORY_BACKEND"
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retorna una instancia única de configuración."""
    return Settings()


settings = get_settings()
