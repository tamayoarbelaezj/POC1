"""Fixtures compartidas de pruebas."""

from __future__ import annotations

import os

import pytest

# Las pruebas nunca deben usar Firestore ni credenciales reales.
os.environ.setdefault("REPOSITORY_BACKEND", "memory")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "proyecto-pruebas")

from agente_polizas.repositories import InMemoryPolizaRepository  # noqa: E402
from agente_polizas.tools import set_repository  # noqa: E402


@pytest.fixture(autouse=True)
def repositorio_memoria():
    """Inyecta el repositorio en memoria en todas las pruebas."""
    repo = InMemoryPolizaRepository()
    set_repository(repo)
    yield repo
    set_repository(None)
