"""Implementación del repositorio sobre Cloud Firestore (modo nativo).

Estructura esperada de colecciones:

- ``{coleccion}``: documentos de póliza con id = número de póliza.
- ``{coleccion}_productos``: documentos de producto con id = código de producto.
- ``{coleccion}_siniestros``: documentos de siniestro con id = número de siniestro.

La cuenta de servicio de Cloud Run solo requiere ``roles/datastore.viewer``.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .base import PolizaRepository, RepositoryError

if TYPE_CHECKING:  # pragma: no cover
    from google.cloud import firestore

logger = logging.getLogger(__name__)


class FirestorePolizaRepository(PolizaRepository):
    """Lectura de pólizas, productos y siniestros desde Firestore."""

    def __init__(
        self,
        coleccion: str,
        proyecto: str | None = None,
        client: firestore.Client | None = None,
        timeout_segundos: float = 5.0,
    ) -> None:
        if client is None:
            from google.cloud import firestore

            client = firestore.Client(project=proyecto)
        self._client = client
        self._coleccion = coleccion
        self._timeout = timeout_segundos

    def _leer(self, coleccion: str, doc_id: str) -> dict[str, Any] | None:
        try:
            snapshot = (
                self._client.collection(coleccion).document(doc_id).get(timeout=self._timeout)
            )
        except Exception as exc:  # noqa: BLE001 - se encapsula cualquier error del SDK
            logger.exception("Error consultando Firestore en %s", coleccion)
            raise RepositoryError("No fue posible consultar la fuente de datos") from exc
        if not snapshot.exists:
            return None
        return snapshot.to_dict()

    def obtener_poliza(self, numero_poliza: str) -> dict[str, Any] | None:
        return self._leer(self._coleccion, numero_poliza)

    def obtener_coberturas(self, codigo_producto: str) -> dict[str, Any] | None:
        return self._leer(f"{self._coleccion}_productos", codigo_producto)

    def obtener_siniestro(self, numero_siniestro: str) -> dict[str, Any] | None:
        return self._leer(f"{self._coleccion}_siniestros", numero_siniestro)
