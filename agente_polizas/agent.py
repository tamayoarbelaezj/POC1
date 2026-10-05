"""Definición del agente raíz para Google ADK."""

from __future__ import annotations

import logging

from google.adk.agents import Agent
from google.genai import types

from .config import settings
from .guardrails import after_model_guardrail, before_model_guardrail
from .prompts import INSTRUCCION_SISTEMA
from .tools import consultar_estado_siniestro, consultar_poliza, listar_coberturas

logging.basicConfig(level=settings.log_level)

root_agent = Agent(
    name="agente_polizas",
    model=settings.model,
    description=(
        "Asistente de Consulta de Pólizas: responde sobre estado de pólizas, "
        "coberturas de producto y estado de siniestros."
    ),
    instruction=INSTRUCCION_SISTEMA,
    tools=[consultar_poliza, listar_coberturas, consultar_estado_siniestro],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
        max_output_tokens=1024,
    ),
    before_model_callback=before_model_guardrail,
    after_model_callback=after_model_guardrail,
)
