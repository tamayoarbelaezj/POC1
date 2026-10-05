"""Pruebas de las herramientas del agente."""

from __future__ import annotations

import pytest

from agente_polizas.repositories import PolizaRepository, RepositoryError
from agente_polizas.tools import (
    consultar_estado_siniestro,
    consultar_poliza,
    listar_coberturas,
    set_repository,
)


class RepositorioCaido(PolizaRepository):
    def obtener_poliza(self, numero_poliza):
        raise RepositoryError("timeout")

    def obtener_coberturas(self, codigo_producto):
        raise RepositoryError("timeout")

    def obtener_siniestro(self, numero_siniestro):
        raise RepositoryError("timeout")


class TestConsultarPoliza:
    def test_poliza_existente(self):
        resultado = consultar_poliza("POL-10000001")
        assert resultado["status"] == "success"
        assert resultado["poliza"]["estado"] == "VIGENTE"
        assert resultado["poliza"]["codigo_producto"] == "AUTO-PLUS"

    def test_normaliza_minusculas_y_espacios(self):
        resultado = consultar_poliza("  pol-10000002 ")
        assert resultado["status"] == "success"
        assert resultado["poliza"]["estado"] == "VENCIDA"

    def test_no_expone_datos_del_tomador(self):
        resultado = consultar_poliza("POL-10000001")
        assert "tomador" not in resultado["poliza"]
        assert "canal" not in resultado["poliza"]

    @pytest.mark.parametrize(
        "numero", ["", "10000001", "POL-123", "POL-1234567890", "SIN-10000001", "POL-ABCDEFGH"]
    )
    def test_formato_invalido(self, numero):
        resultado = consultar_poliza(numero)
        assert resultado["status"] == "error"
        assert "formato" in resultado["error_message"]

    def test_poliza_inexistente(self):
        resultado = consultar_poliza("POL-99999999")
        assert resultado["status"] == "error"
        assert "No se encontró" in resultado["error_message"]

    def test_fuente_no_disponible(self):
        set_repository(RepositorioCaido())
        resultado = consultar_poliza("POL-10000001")
        assert resultado["status"] == "error"
        assert "no está disponible" in resultado["error_message"]


class TestListarCoberturas:
    def test_producto_existente(self):
        resultado = listar_coberturas("AUTO-PLUS")
        assert resultado["status"] == "success"
        nombres = [c["nombre"] for c in resultado["producto"]["coberturas"]]
        assert "Hurto" in nombres

    def test_codigo_en_minusculas(self):
        assert listar_coberturas("hogar-basico")["status"] == "success"

    @pytest.mark.parametrize("codigo", ["", "A", "AUTO PLUS; DROP", "123-456"])
    def test_codigo_invalido(self, codigo):
        assert listar_coberturas(codigo)["status"] == "error"

    def test_producto_inexistente(self):
        resultado = listar_coberturas("SALUD-TOTAL")
        assert resultado["status"] == "error"

    def test_fuente_no_disponible(self):
        set_repository(RepositorioCaido())
        assert listar_coberturas("AUTO-PLUS")["status"] == "error"


class TestConsultarSiniestro:
    def test_siniestro_existente(self):
        resultado = consultar_estado_siniestro("SIN-20000001")
        assert resultado["status"] == "success"
        assert resultado["siniestro"]["estado"] == "EN_EVALUACION"
        assert "evaluado" in resultado["siniestro"]["descripcion_estado"]

    @pytest.mark.parametrize("numero", ["", "SIN-1", "POL-20000001", "sin_20000001"])
    def test_formato_invalido(self, numero):
        assert consultar_estado_siniestro(numero)["status"] == "error"

    def test_siniestro_inexistente(self):
        resultado = consultar_estado_siniestro("SIN-99999999")
        assert resultado["status"] == "error"
        assert "No se encontró" in resultado["error_message"]

    def test_fuente_no_disponible(self):
        set_repository(RepositorioCaido())
        assert consultar_estado_siniestro("SIN-20000001")["status"] == "error"
