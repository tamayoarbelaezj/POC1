# syntax=docker/dockerfile:1.7
# Imagen del Asistente de Consulta de Pólizas para Cloud Run.

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

WORKDIR /app

# Usuario sin privilegios
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app --shell /usr/sbin/nologin app

# Dependencias primero para aprovechar la caché de capas
COPY pyproject.toml README.md ./
COPY agente_polizas/__init__.py agente_polizas/__init__.py
RUN pip install --upgrade pip \
    && pip install .

# Código de la aplicación
COPY agente_polizas/ agente_polizas/
COPY main.py ./

RUN chown -R app:app /app
USER app

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1 --timeout-keep-alive 75"]
