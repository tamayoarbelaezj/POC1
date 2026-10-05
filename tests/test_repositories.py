"""Pruebas de los repositorios de datos."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from agente_polizas.repositories import InMemoryPolizaRepository, RepositoryError
from agente_polizas.repositories.firestore_repo import FirestorePolizaRepository
from agente_polizas.repositories.memory_repo import POLIZAS_EJEMPLO


class TestRepositorioMemoria:
    def test_obtiene_registros(self):
        repo = InMemoryPolizaRepository()
        assert repo.obtener_poliza("POL-10000001")["producto"].startswith("Autos Plus")
        assert repo.obtener_coberturas("VIDA-INDIVIDUAL")["coberturas"]
        assert repo.obtener_siniestro("SIN-20000002")["estado"] == "PAGADO"

    def test_inexistentes_retornan_none(self):
        repo = InMemoryPolizaRepository()
        assert repo.obtener_poliza("POL-00000000") is None
        assert repo.obtener_coberturas("NO-EXISTE") is None
        assert repo.obtener_siniestro("SIN-00000000") is None

    def test_retorna_copias(self):
        repo = InMemoryPolizaRepository()
        repo.obtener_poliza("POL-10000001")["estado"] = "MODIFICADO"
        assert POLIZAS_EJEMPLO["POL-10000001"]["estado"] == "VIGENTE"

    def test_datos_inyectados(self):
        repo = InMemoryPolizaRepository(polizas={"POL-00000001": {"estado": "VIGENTE"}})
        assert repo.obtener_poliza("POL-00000001") == {"estado": "VIGENTE"}

    def test_datos_de_ejemplo_son_ficticios(self):
        for poliza in POLIZAS_EJEMPLO.values():
            assert "Ficticio" in poliza["tomador"]
            assert "(ejemplo)" in poliza["producto"]


class _Snapshot:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return dict(self._data)


class _ClienteFalso:
    """Doble de prueba del cliente de Firestore."""

    def __init__(self, datos, falla=False):
        self.datos = datos
        self.falla = falla
        self.consultas = []

    def collection(self, nombre):
        def document(doc_id):
            def get(timeout=None):
                self.consultas.append((nombre, doc_id, timeout))
                if self.falla:
                    raise TimeoutError("deadline exceeded")
                return _Snapshot(self.datos.get(nombre, {}).get(doc_id))

            return SimpleNamespace(get=get)

        return SimpleNamespace(document=document)


class TestRepositorioFirestore:
    def test_lee_colecciones_esperadas(self):
        cliente = _ClienteFalso(
            {
                "polizas": {"POL-10000001": {"estado": "VIGENTE"}},
                "polizas_productos": {"AUTO-PLUS": {"nombre": "Autos"}},
                "polizas_siniestros": {"SIN-20000001": {"estado": "PAGADO"}},
            }
        )
        repo = FirestorePolizaRepository(coleccion="polizas", client=cliente, timeout_segundos=3)
        assert repo.obtener_poliza("POL-10000001") == {"estado": "VIGENTE"}
        assert repo.obtener_coberturas("AUTO-PLUS") == {"nombre": "Autos"}
        assert repo.obtener_siniestro("SIN-20000001") == {"estado": "PAGADO"}
        assert cliente.consultas[0] == ("polizas", "POL-10000001", 3)

    def test_documento_inexistente(self):
        repo = FirestorePolizaRepository(coleccion="polizas", client=_ClienteFalso({}))
        assert repo.obtener_poliza("POL-99999999") is None

    def test_error_de_infraestructura(self):
        repo = FirestorePolizaRepository(coleccion="polizas", client=_ClienteFalso({}, falla=True))
        with pytest.raises(RepositoryError):
            repo.obtener_poliza("POL-10000001")
