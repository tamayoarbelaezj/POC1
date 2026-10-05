"""Punto de entrada HTTP del agente para Cloud Run.

Expone la API de ADK (``/run``, ``/run_sse``, ``/apps/...``) y un endpoint
``/health`` para las sondas de disponibilidad.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Orígenes permitidos para CORS, separados por coma (vacío = sin CORS).
ALLOWED_ORIGINS = [o for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o]

# Sesiones en memoria por defecto; en productivo se puede apuntar a Cloud SQL o
# a Vertex AI Agent Engine mediante SESSION_SERVICE_URI.
SESSION_SERVICE_URI = os.getenv("SESSION_SERVICE_URI") or None

app: FastAPI = get_fast_api_app(
    agents_dir=AGENTS_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=False,
    trace_to_cloud=os.getenv("TRACE_TO_CLOUD", "false").lower() == "true",
)


# Versiones recientes de ADK registran su propio /health; se reemplaza por uno que
# identifica el servicio para las sondas y el monitoreo de disponibilidad.
app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != "/health"]


@app.get("/health", tags=["operacion"])
def health() -> dict[str, str]:
    """Sonda de disponibilidad para Cloud Run."""
    return {"status": "ok", "agente": "agente_polizas"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
