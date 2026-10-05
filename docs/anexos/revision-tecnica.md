# Revisión técnica de pares

**Iniciativa:** Asistente de Consulta de Pólizas
**Versión revisada:** v1.1.0 — <https://github.com/tamayoarbelaezj/POC1/releases/tag/v1.1.0>
**Fecha:** 2026-10-05
**Revisor:** Santiago Ríos Herrera — Ingeniero de IA, AI Lab
**Participación adicional:** Seguridad de la Información
**Resultado:** **Aprobado con observaciones**

## Lista de verificación

| # | Aspecto | Resultado | Comentario |
|---|---|---|---|
| 1 | Estructura del agente según convenciones de ADK (`root_agent`, `__init__.py`) | Cumple | — |
| 2 | Configuración por variables de entorno, sin secretos en el código | Cumple | `config.py` con `pydantic-settings`; `.env` excluido en `.gitignore` y `.dockerignore` |
| 3 | Herramientas con docstrings claros, validación de entrada y errores controlados | Cumple | Respuesta uniforme `status` / `error_message` |
| 4 | Minimización de datos en las respuestas de herramientas | Cumple | `CAMPOS_PUBLICOS_POLIZA` |
| 5 | Guardrails de entrada y salida con pruebas unitarias | Cumple con observación | Ver O1 |
| 6 | Acceso a datos desacoplado (interfaz de repositorio) y sin consultas abiertas | Cumple | Lectura por clave en Firestore |
| 7 | Pruebas automatizadas sin dependencia del LLM; lint en CI | Cumple | 72 pruebas, `ruff` sin hallazgos |
| 8 | Evaluación con evalset de ADK y criterios definidos | Cumple | `tests/eval/` |
| 9 | Contenedor sin privilegios y despliegue privado | Cumple | Usuario no root, `--no-allow-unauthenticated`, ingreso interno |
| 10 | IAM de mínimo privilegio | Cumple | `datastore.viewer`, `aiplatform.user`, `cloudtrace.agent` |
| 11 | Observabilidad (logs, trazas, métricas, alertas) | Cumple | Cloud Trace habilitado en despliegue |
| 12 | Manejo de errores del modelo (429 / 503) | Cumple con observación | Ver O2 |
| 13 | Coherencia entre documentación, costos y resultados de pruebas | Cumple | — |
| 14 | Verificación de titularidad de la póliza consultada | Cumple con observación | Ver O3 |

## Observaciones

| # | Observación | Severidad | Respuesta del equipo | Estado |
|---|---|---|---|---|
| O1 | Las expresiones regulares de inyección cubren español e inglés básico; variaciones semánticas dependen de Model Armor. | Menor | Se acepta: es el diseño de dos capas. Se agregarán al set de pruebas los prompts que Model Armor bloquee en producción y no la capa 1. | Abierta (seguimiento mensual) |
| O2 | No hay reintentos ante 429 del modelo (confirmado en prueba de estrés). | Menor | Acción 2 del plan de pruebas de carga (v1.2.0). | Abierta |
| O3 | El agente confía en la autenticación del canal; no valida que el número de póliza consultado pertenezca al usuario autenticado. | Menor (los datos expuestos están minimizados) | Para v1.2.0 los canales enviarán en el estado de la sesión la lista de pólizas del usuario y la herramienta validará la pertenencia. | Abierta |

## Concepto

La solución es apta para la salida gradual aprobada por negocio. Las observaciones O2 y O3
deben cerrarse en v1.2.0, antes de pasar al 100 % del tráfico.
