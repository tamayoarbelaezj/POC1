"""Repositorio en memoria con datos de ejemplo FICTICIOS.

Se usa para desarrollo local, pruebas automatizadas y evaluaciones del agente.
Ningún registro corresponde a clientes, pólizas o siniestros reales.
"""

from __future__ import annotations

import copy
from typing import Any

from .base import PolizaRepository

POLIZAS_EJEMPLO: dict[str, dict[str, Any]] = {
    "POL-10000001": {
        "numero_poliza": "POL-10000001",
        "codigo_producto": "AUTO-PLUS",
        "producto": "Autos Plus (ejemplo)",
        "tomador": "Cliente Ficticio Uno",
        "estado": "VIGENTE",
        "fecha_inicio": "2026-01-15",
        "fecha_fin": "2027-01-14",
        "valor_asegurado": 85_000_000,
        "prima_anual": 2_450_000,
        "estado_pago": "AL_DIA",
        "canal": "ASESOR",
    },
    "POL-10000002": {
        "numero_poliza": "POL-10000002",
        "codigo_producto": "HOGAR-BASICO",
        "producto": "Hogar Básico (ejemplo)",
        "tomador": "Cliente Ficticio Dos",
        "estado": "VENCIDA",
        "fecha_inicio": "2025-03-01",
        "fecha_fin": "2026-02-28",
        "valor_asegurado": 320_000_000,
        "prima_anual": 780_000,
        "estado_pago": "PENDIENTE",
        "canal": "DIGITAL",
    },
    "POL-10000003": {
        "numero_poliza": "POL-10000003",
        "codigo_producto": "VIDA-INDIVIDUAL",
        "producto": "Vida Individual (ejemplo)",
        "tomador": "Cliente Ficticio Tres",
        "estado": "CANCELADA",
        "fecha_inicio": "2024-06-10",
        "fecha_fin": "2025-06-09",
        "valor_asegurado": 150_000_000,
        "prima_anual": 1_200_000,
        "estado_pago": "NO_APLICA",
        "canal": "BANCASEGUROS",
    },
}

PRODUCTOS_EJEMPLO: dict[str, dict[str, Any]] = {
    "AUTO-PLUS": {
        "codigo_producto": "AUTO-PLUS",
        "nombre": "Autos Plus (ejemplo)",
        "coberturas": [
            {"nombre": "Responsabilidad civil extracontractual", "limite": "4.000 SMMLV"},
            {"nombre": "Pérdida total por daños", "limite": "100% valor asegurado"},
            {"nombre": "Pérdida parcial por daños", "limite": "Deducible 10% mín. 1 SMMLV"},
            {"nombre": "Hurto", "limite": "100% valor asegurado"},
            {"nombre": "Asistencia en viaje", "limite": "Según condicionado"},
        ],
        "exclusiones": ["Conducción en estado de embriaguez", "Uso no declarado del vehículo"],
    },
    "HOGAR-BASICO": {
        "codigo_producto": "HOGAR-BASICO",
        "nombre": "Hogar Básico (ejemplo)",
        "coberturas": [
            {"nombre": "Incendio y anexos", "limite": "100% valor asegurado"},
            {"nombre": "Terremoto", "limite": "100% valor asegurado"},
            {"nombre": "Daños por agua", "limite": "20% valor asegurado"},
        ],
        "exclusiones": ["Deterioro gradual", "Actos intencionales del asegurado"],
    },
    "VIDA-INDIVIDUAL": {
        "codigo_producto": "VIDA-INDIVIDUAL",
        "nombre": "Vida Individual (ejemplo)",
        "coberturas": [
            {"nombre": "Muerte por cualquier causa", "limite": "100% valor asegurado"},
            {"nombre": "Incapacidad total y permanente", "limite": "100% valor asegurado"},
        ],
        "exclusiones": ["Suicidio durante el primer año de vigencia"],
    },
}

SINIESTROS_EJEMPLO: dict[str, dict[str, Any]] = {
    "SIN-20000001": {
        "numero_siniestro": "SIN-20000001",
        "numero_poliza": "POL-10000001",
        "tipo": "Pérdida parcial por daños",
        "estado": "EN_EVALUACION",
        "fecha_aviso": "2026-09-20",
        "ultima_actualizacion": "2026-09-28",
        "siguiente_paso": "Inspección del vehículo por parte del perito asignado",
    },
    "SIN-20000002": {
        "numero_siniestro": "SIN-20000002",
        "numero_poliza": "POL-10000002",
        "tipo": "Daños por agua",
        "estado": "PAGADO",
        "fecha_aviso": "2025-11-02",
        "ultima_actualizacion": "2025-12-10",
        "siguiente_paso": "Ninguno. Siniestro cerrado.",
    },
}


class InMemoryPolizaRepository(PolizaRepository):
    """Implementación en memoria. Retorna copias para evitar mutaciones externas."""

    def __init__(
        self,
        polizas: dict[str, dict[str, Any]] | None = None,
        productos: dict[str, dict[str, Any]] | None = None,
        siniestros: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self._polizas = polizas if polizas is not None else POLIZAS_EJEMPLO
        self._productos = productos if productos is not None else PRODUCTOS_EJEMPLO
        self._siniestros = siniestros if siniestros is not None else SINIESTROS_EJEMPLO

    def obtener_poliza(self, numero_poliza: str) -> dict[str, Any] | None:
        return copy.deepcopy(self._polizas.get(numero_poliza))

    def obtener_coberturas(self, codigo_producto: str) -> dict[str, Any] | None:
        return copy.deepcopy(self._productos.get(codigo_producto))

    def obtener_siniestro(self, numero_siniestro: str) -> dict[str, Any] | None:
        return copy.deepcopy(self._siniestros.get(numero_siniestro))
