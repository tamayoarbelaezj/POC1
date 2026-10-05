"""Prueba de humo de la API HTTP (no invoca el modelo)."""

from __future__ import annotations

import pytest

pytest.importorskip("google.adk")

from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="module")
def cliente():
    import main

    return TestClient(main.app)


def test_health(cliente):
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok", "agente": "agente_polizas"}


def test_lista_el_agente(cliente):
    respuesta = cliente.get("/list-apps")
    assert respuesta.status_code == 200
    assert "agente_polizas" in respuesta.json()
