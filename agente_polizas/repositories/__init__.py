"""Repositorios de datos del agente y fábrica según configuración."""

from __future__ import annotations

from functools import lru_cache

from .base import PolizaRepository, RepositoryError
from .memory_repo import InMemoryPolizaRepository

__all__ = [
    "InMemoryPolizaRepository",
    "PolizaRepository",
    "RepositoryError",
    "get_repository",
]


@lru_cache(maxsize=1)
def get_repository() -> PolizaRepository:
    """Construye el repositorio según ``REPOSITORY_BACKEND``."""
    from ..config import get_settings

    settings = get_settings()
    if settings.repository_backend == "firestore":
        from .firestore_repo import FirestorePolizaRepository

        return FirestorePolizaRepository(
            coleccion=settings.firestore_collection,
            proyecto=settings.google_cloud_project,
        )
    return InMemoryPolizaRepository()
