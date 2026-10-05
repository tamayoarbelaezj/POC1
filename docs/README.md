# Documentación de la iniciativa

Documentación del **Asistente de Consulta de Pólizas** según el *Formato Documentación Modelos
Analíticos (ML) e iniciativas de IA* de Seguros Bolívar. Cada sección del formato oficial se
encuentra en el archivo indicado.

## Mapa del formato oficial

| Sección del formato | Campo | Archivo |
|---|---|---|
| Encabezado | Nombre de la iniciativa, fecha de elaboración, nivel de criticidad, versión del documento | [00-ficha-iniciativa.md](00-ficha-iniciativa.md) |
| Encabezado | Elaborado por, custodio técnico, responsable de negocio (vicepresidencia, área, cargo) | [00-ficha-iniciativa.md](00-ficha-iniciativa.md#responsables) |
| Encabezado | Fecha último despliegue | [00-ficha-iniciativa.md](00-ficha-iniciativa.md) |
| Control de versiones | Fecha, versión, autor, descripción, link al repositorio / tag | [CHANGELOG.md](../CHANGELOG.md#trazabilidad-de-versiones) |
| 1. Negocio | 1.1 Objetivo y problema de negocio, situación actual, métricas a mejorar | [01-negocio.md §1.1](01-negocio.md#11-objetivo-y-problema-de-negocio) |
| 1. Negocio | 1.1 Matriz RACI | [01-negocio.md §1.1](01-negocio.md#matriz-raci) |
| 1. Negocio | 1.2 Caso de negocio: costos, beneficios, retorno, periodo de recuperación | [01-negocio.md §1.2](01-negocio.md#12-caso-de-negocio) |
| 1. Negocio | 1.2 Evidencia (pitch) | [anexos/pitch.md](anexos/pitch.md) |
| 1. Negocio | 1.3 Integraciones y dependencias | [01-negocio.md §1.3](01-negocio.md#13-integraciones-y-dependencias) |
| 1. Negocio | 1.3 Flujograma | [diagramas/flujo-proceso.drawio](diagramas/flujo-proceso.drawio) y versión mermaid en [01-negocio.md](01-negocio.md#flujograma-del-proceso) |
| 2. Datos | 2.1 Inventario de fuentes (fuente, responsable, naturaleza) | [02-datos.md §2.1](02-datos.md#inventario-de-fuentes) |
| 2. Datos | 2.1 Transformación y diccionario de datos | [02-datos.md](02-datos.md#transformación-y-diccionario-de-datos), [anexos/diccionario-datos.md](anexos/diccionario-datos.md) |
| 2. Datos | 2.1 Base de conocimiento (fuentes, nombre, link a embeddings) | [02-datos.md](02-datos.md#base-de-conocimiento) |
| 2. Datos | 2.1 Evaluación de calidad (EDA): distribución, atípicos, relevancia, conclusiones | [02-datos.md](02-datos.md#evaluación-de-calidad-de-los-datos-eda) |
| 2. Datos | 2.1 Estructura de la KB / chunking | [02-datos.md](02-datos.md#estructura-de-la-base-de-conocimiento-chunking) |
| 2. Datos | 2.2 Justificación técnica de transformaciones | [02-datos.md §2.2](02-datos.md#justificación-técnica-de-las-transformaciones) |
| 2. Datos | 2.2 Calidad final (fuente, variable, % completitud, exactitud) | [02-datos.md](02-datos.md#calidad-final-de-los-datos) |
| 2. Datos | 2.2 Filtrado de contenido / guardrails | [02-datos.md](02-datos.md#filtrado-de-contenido--guardrails) |
| 3. Modelo | 3.1 Evaluación comparativa y justificación del modelo ganador | [03-modelo.md §3.1](03-modelo.md#31-evaluación-comparativa-de-modelos) |
| 3. Modelo | 3.2 KPIs (fórmula, rango de normalidad, umbral de alerta) | [03-modelo.md §3.2](03-modelo.md#32-kpis-del-modelo) |
| 3. Modelo | 3.3 Plan de monitoreo y link al dashboard | [03-modelo.md §3.3](03-modelo.md#33-plan-de-monitoreo) |
| 3. Modelo | 3.4 Sesgo y equidad | [03-modelo.md §3.4](03-modelo.md#34-análisis-de-sesgo-y-equidad) |
| 4. Pruebas de carga | 4.1 Herramienta, infraestructura, escenario | [04-pruebas-carga.md §4.1](04-pruebas-carga.md#41-diseño-de-la-prueba) |
| 4. Pruebas de carga | 4.2 Desempeño objetivo vs. real, causa raíz, plan de acción | [04-pruebas-carga.md §4.2](04-pruebas-carga.md#42-resultados-desempeño-objetivo-vs-real) |
| 5. Riesgos | Escala de probabilidad e impacto; matriz de riesgos y controles | [05-riesgos.md](05-riesgos.md) |
| 6. Aceptación | VoBo del propietario de negocio | [06-aceptacion.md §6.1](06-aceptacion.md#61-visto-bueno-del-propietario-de-negocio), [anexos/acta-aprobacion.md](anexos/acta-aprobacion.md) |
| 6. Aceptación | Validación técnica independiente | [06-aceptacion.md §6.2](06-aceptacion.md#62-validación-técnica-independiente), [anexos/revision-tecnica.md](anexos/revision-tecnica.md) |

## Artefactos referenciados

| Artefacto | Ubicación |
|---|---|
| Código del agente | [`agente_polizas/`](../agente_polizas/) |
| Guardrails | [`agente_polizas/guardrails/callbacks.py`](../agente_polizas/guardrails/callbacks.py) |
| Set de evaluación ADK | [`tests/eval/polizas.evalset.json`](../tests/eval/polizas.evalset.json) |
| Pruebas de carga | [`load-tests/script.js`](../load-tests/script.js), [`load-tests/resultados/`](../load-tests/resultados/resumen-2026-10.md) |
| Pipeline de despliegue | [`cloudbuild.yaml`](../cloudbuild.yaml), [`Dockerfile`](../Dockerfile) |
