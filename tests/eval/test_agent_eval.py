"""Evaluación del agente con el framework de evaluación de ADK.

Invoca el modelo real, por lo que solo se ejecuta cuando ``RUN_LLM_EVAL=true``
y existen credenciales de Google Cloud. Uso:

    RUN_LLM_EVAL=true pytest tests/eval -q

o bien desde la CLI de ADK:

    adk eval agente_polizas tests/eval/polizas.evalset.json \\
        --config_file_path tests/eval/test_config.json
"""

from __future__ import annotations

import json
import os
import pathlib

import pytest

EVAL_DIR = pathlib.Path(__file__).parent
EVALSET = EVAL_DIR / "polizas.evalset.json"


def test_evalset_bien_formado():
    """Valida la estructura mínima del evalset sin invocar el modelo."""
    data = json.loads(EVALSET.read_text(encoding="utf-8"))
    assert data["eval_set_id"]
    ids = [caso["eval_id"] for caso in data["eval_cases"]]
    assert len(ids) == len(set(ids)) >= 8
    for caso in data["eval_cases"]:
        for turno in caso["conversation"]:
            assert turno["user_content"]["parts"][0]["text"]
            assert turno["final_response"]["parts"][0]["text"]


@pytest.mark.skipif(
    os.getenv("RUN_LLM_EVAL", "false").lower() != "true",
    reason="Evaluación con LLM deshabilitada (definir RUN_LLM_EVAL=true)",
)
@pytest.mark.asyncio
async def test_evalset_agente():
    evaluation = pytest.importorskip("google.adk.evaluation.agent_evaluator")
    await evaluation.AgentEvaluator.evaluate(
        agent_module="agente_polizas",
        eval_dataset_file_path_or_dir=str(EVALSET),
        num_runs=2,
    )
