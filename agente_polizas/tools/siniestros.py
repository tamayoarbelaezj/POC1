"""Herramienta de consulta del estado de siniestros."""

from __future__ import annotations

import re
from typing import Any

from ..repositories import RepositoryError

PATRON_SINIESTRO = re.compile(r"^SIN-\d{8}$")

ESTADOS_DESCRIPCION = {
    "RADICADO": "El aviso fue recibido y está pendiente de asignación.",
    "EN_EVALUACION": "El siniestro está siendo evaluado por el equipo de indemnizaciones.",
    "OBJETADO": "El siniestro fue objetado. El asesor puede explicar los motivos.",
    "APROBADO": "El siniestro fue aprobado y el pago está en proceso.",
    "PAGADO": "La indemnización fue pagada y el siniestro está cerrado.",
}


def consultar_estado_siniestro(numero_siniestro: str) -> dict[str, Any]:
    """Consulta el estado actual de un siniestro (reclamación).

    Args:
        numero_siniestro: Número de siniestro con formato ``SIN-`` seguido de 8
            dígitos, por ejemplo ``SIN-20000001``.

    Returns:
        Diccionario con ``status`` ``"success"`` y la clave ``siniestro`` (tipo,
        estado, descripción del estado, fechas y siguiente paso), o ``status``
        ``"error"`` con ``error_message``.
    """
    from . import repositorio_actual

    numero = (numero_siniestro or "").strip().upper().replace(" ", "")
    if not PATRON_SINIESTRO.match(numero):
        return {
            "status": "error",
            "error_message": (
                "El número de siniestro no tiene un formato válido. Debe ser 'SIN-' seguido "
                "de 8 dígitos, por ejemplo SIN-20000001."
            ),
        }
    try:
        siniestro = repositorio_actual().obtener_siniestro(numero)
    except RepositoryError:
        return {
            "status": "error",
            "error_message": "El sistema de siniestros no está disponible en este momento.",
        }
    if siniestro is None:
        return {
            "status": "error",
            "error_message": f"No se encontró un siniestro con el número {numero}.",
        }
    siniestro["descripcion_estado"] = ESTADOS_DESCRIPCION.get(
        siniestro.get("estado", ""), "Estado no catalogado; consulte con un asesor."
    )
    return {"status": "success", "siniestro": siniestro}
