"""Herramientas de consulta de pólizas y coberturas de producto."""

from __future__ import annotations

import logging
import re
from typing import Any

from ..repositories import RepositoryError

logger = logging.getLogger(__name__)

PATRON_POLIZA = re.compile(r"^POL-\d{8}$")
PATRON_PRODUCTO = re.compile(r"^[A-Z]{2,12}(-[A-Z]{2,15})?$")

CAMPOS_PUBLICOS_POLIZA = (
    "numero_poliza",
    "codigo_producto",
    "producto",
    "estado",
    "fecha_inicio",
    "fecha_fin",
    "valor_asegurado",
    "estado_pago",
)


def _error(mensaje: str) -> dict[str, Any]:
    return {"status": "error", "error_message": mensaje}


def normalizar_numero_poliza(numero_poliza: str) -> str:
    """Normaliza espacios y mayúsculas del número de póliza."""
    return (numero_poliza or "").strip().upper().replace(" ", "")


def consultar_poliza(numero_poliza: str) -> dict[str, Any]:
    """Consulta el estado de una póliza a partir de su número.

    Args:
        numero_poliza: Número de póliza con formato ``POL-`` seguido de 8 dígitos,
            por ejemplo ``POL-10000001``.

    Returns:
        Diccionario con ``status`` igual a ``"success"`` y la clave ``poliza`` con
        producto, estado, vigencia, valor asegurado y estado de pago; o ``status``
        igual a ``"error"`` con ``error_message`` cuando el formato es inválido,
        la póliza no existe o la fuente de datos no está disponible.
    """
    from . import repositorio_actual

    numero = normalizar_numero_poliza(numero_poliza)
    if not PATRON_POLIZA.match(numero):
        return _error(
            "El número de póliza no tiene un formato válido. Debe ser 'POL-' seguido de "
            "8 dígitos, por ejemplo POL-10000001."
        )
    try:
        poliza = repositorio_actual().obtener_poliza(numero)
    except RepositoryError:
        return _error("El sistema de pólizas no está disponible en este momento.")
    if poliza is None:
        return _error(f"No se encontró una póliza con el número {numero}.")

    # Se excluyen datos personales del tomador: el agente no los necesita para responder.
    datos = {campo: poliza.get(campo) for campo in CAMPOS_PUBLICOS_POLIZA}
    logger.info("Consulta de póliza exitosa", extra={"numero_poliza": numero})
    return {"status": "success", "poliza": datos}


def listar_coberturas(codigo_producto: str) -> dict[str, Any]:
    """Lista las coberturas y exclusiones principales de un producto.

    Args:
        codigo_producto: Código del producto en mayúsculas, por ejemplo ``AUTO-PLUS``.
            Se obtiene del campo ``codigo_producto`` de ``consultar_poliza``.

    Returns:
        Diccionario con ``status`` ``"success"`` y la clave ``producto`` (nombre,
        coberturas con su límite y exclusiones), o ``status`` ``"error"`` con
        ``error_message``.
    """
    from . import repositorio_actual

    codigo = (codigo_producto or "").strip().upper()
    if not PATRON_PRODUCTO.match(codigo):
        return _error("El código de producto no tiene un formato válido, por ejemplo AUTO-PLUS.")
    try:
        producto = repositorio_actual().obtener_coberturas(codigo)
    except RepositoryError:
        return _error("El catálogo de productos no está disponible en este momento.")
    if producto is None:
        return _error(f"No se encontró el producto {codigo}.")
    return {"status": "success", "producto": producto}
