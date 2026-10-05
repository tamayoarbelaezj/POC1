"""Herramientas (function tools) expuestas al agente."""

from __future__ import annotations

from ..repositories import PolizaRepository, get_repository

_repositorio_override: PolizaRepository | None = None


def set_repository(repositorio: PolizaRepository | None) -> None:
    """Permite inyectar un repositorio alterno (pruebas o evaluaciones)."""
    global _repositorio_override
    _repositorio_override = repositorio


def repositorio_actual() -> PolizaRepository:
    """Retorna el repositorio activo para las herramientas."""
    if _repositorio_override is not None:
        return _repositorio_override
    return get_repository()


from .polizas import consultar_poliza, listar_coberturas  # noqa: E402
from .siniestros import consultar_estado_siniestro  # noqa: E402

__all__ = [
    "consultar_estado_siniestro",
    "consultar_poliza",
    "listar_coberturas",
    "repositorio_actual",
    "set_repository",
]
