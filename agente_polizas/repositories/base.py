"""Contrato de acceso a datos de pólizas, productos y siniestros."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RepositoryError(Exception):
    """Error de infraestructura al consultar la fuente de datos."""


class PolizaRepository(ABC):
    """Interfaz de lectura sobre el core de pólizas.

    Las implementaciones retornan diccionarios planos o ``None`` cuando el
    registro no existe. Los errores de infraestructura se elevan como
    :class:`RepositoryError` para que las herramientas los traduzcan a un
    mensaje controlado.
    """

    @abstractmethod
    def obtener_poliza(self, numero_poliza: str) -> dict[str, Any] | None:
        """Retorna la póliza identificada por ``numero_poliza``."""

    @abstractmethod
    def obtener_coberturas(self, codigo_producto: str) -> dict[str, Any] | None:
        """Retorna el producto y su lista de coberturas."""

    @abstractmethod
    def obtener_siniestro(self, numero_siniestro: str) -> dict[str, Any] | None:
        """Retorna el siniestro identificado por ``numero_siniestro``."""
