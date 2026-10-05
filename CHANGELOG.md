# Changelog

Todos los cambios relevantes de la iniciativa se documentan en este archivo.
El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y el
proyecto sigue [Versionamiento Semántico](https://semver.org/lang/es/).

## Trazabilidad de versiones

| Fecha | Versión | Autor | Descripción | Repositorio / tag |
|---|---|---|---|---|
| 2026-10-05 | 1.0.0 | Juan Tamayo (AI Lab) | Primera versión funcional del agente: herramientas, guardrails, API, pruebas y pipeline de despliegue. | [v1.0.0](https://github.com/tamayoarbelaezj/POC1/releases/tag/v1.0.0) |
| 2026-10-05 | 1.1.0 | Juan Tamayo (AI Lab) | Documentación completa del formato de iniciativas de IA, pruebas de carga con k6, acta de aprobación de negocio y revisión técnica de pares. | [v1.1.0](https://github.com/tamayoarbelaezj/POC1/releases/tag/v1.1.0) |

## [1.1.0] - 2026-10-05

### Agregado
- Documentación de gobierno en `docs/` según el formato *Documentación Modelos Analíticos (ML)
  e iniciativas de IA*: ficha, negocio, datos, modelo, pruebas de carga, riesgos y aceptación.
- Diccionario de datos, pitch, acta de aprobación y revisión técnica de pares en `docs/anexos/`.
- Flujograma BPMN del proceso en draw.io (`docs/diagramas/flujo-proceso.drawio`).
- Script de pruebas de carga con k6 (`load-tests/script.js`) y resumen de resultados.

### Cambiado
- README con sección de documentación y pruebas de carga.

## [1.0.0] - 2026-10-05

### Agregado
- Agente raíz `agente_polizas` sobre Google ADK con modelo `gemini-2.5-flash`.
- Herramientas `consultar_poliza`, `listar_coberturas` y `consultar_estado_siniestro` con
  validación de formato (`POL-` / `SIN-` + 8 dígitos) y respuestas `status` / `error_message`.
- Repositorios de datos: interfaz `PolizaRepository`, implementación en Firestore y en memoria
  con datos ficticios.
- Guardrails `before_model_callback` (enmascarado de cédulas, correos y teléfonos colombianos;
  bloqueo de prompt injection) y `after_model_callback` (filtro de PII y de fuga de instrucciones).
- API FastAPI basada en `get_fast_api_app` con endpoint `/health`.
- Pruebas unitarias con pytest y set de evaluación ADK `tests/eval/polizas.evalset.json`.
- Dockerfile con usuario no root, `cloudbuild.yaml` para Cloud Run y workflow de CI.
