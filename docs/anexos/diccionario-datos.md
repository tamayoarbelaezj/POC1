# Diccionario de datos

Fuentes transformadas que consume o produce el Asistente de Consulta de Pólizas. Los ejemplos
corresponden a los datos **ficticios** del repositorio en memoria
([`memory_repo.py`](../../agente_polizas/repositories/memory_repo.py)).

Clasificación de la información según la política de la compañía: **Pública**, **Interna**,
**Confidencial** (datos personales o de negocio sensibles).

## 1. Colección `polizas`

Origen: F1 Core de pólizas. Id del documento: `numero_poliza`. Sincronización cada 15 min.

| Campo | Tipo | Descripción | Ejemplo | Clasificación | Expuesto al modelo |
|---|---|---|---|---|---|
| `numero_poliza` | string `^POL-\d{8}$` | Identificador único de la póliza | `POL-10000001` | Interna | Sí |
| `codigo_producto` | string | Código del producto comercial; llave hacia `polizas_productos` | `AUTO-PLUS` | Interna | Sí |
| `producto` | string | Nombre comercial del producto | `Autos Plus (ejemplo)` | Pública | Sí |
| `tomador` | string | Nombre del tomador | `Cliente Ficticio Uno` | Confidencial | **No** |
| `estado` | enum `VIGENTE`, `VENCIDA`, `CANCELADA` | Estado normalizado de la póliza | `VIGENTE` | Interna | Sí |
| `fecha_inicio` | date ISO 8601 | Inicio de vigencia | `2026-01-15` | Interna | Sí |
| `fecha_fin` | date ISO 8601 | Fin de vigencia | `2027-01-14` | Interna | Sí |
| `valor_asegurado` | integer (COP) | Valor asegurado total | `85000000` | Confidencial | Sí (al titular) |
| `prima_anual` | integer (COP) | Prima anual | `2450000` | Confidencial | **No** |
| `estado_pago` | enum `AL_DIA`, `PENDIENTE`, `NO_APLICA` | Estado de cartera de la póliza | `AL_DIA` | Interna | Sí |
| `canal` | enum `ASESOR`, `DIGITAL`, `BANCASEGUROS` | Canal de venta | `ASESOR` | Interna | **No** |

## 2. Colección `polizas_productos`

Origen: F3 catálogo curado + F4 condicionados. Id del documento: `codigo_producto`.

| Campo | Tipo | Descripción | Ejemplo | Clasificación |
|---|---|---|---|---|
| `codigo_producto` | string | Código del producto | `HOGAR-BASICO` | Interna |
| `nombre` | string | Nombre comercial | `Hogar Básico (ejemplo)` | Pública |
| `coberturas` | array de objetos | Coberturas resumidas | — | Pública |
| `coberturas[].nombre` | string | Nombre de la cobertura | `Terremoto` | Pública |
| `coberturas[].limite` | string | Límite o deducible en lenguaje del condicionado | `100% valor asegurado` | Pública |
| `exclusiones` | array de string | Exclusiones principales | `["Deterioro gradual"]` | Pública |

## 3. Colección `polizas_siniestros`

Origen: F2 Core de siniestros. Id del documento: `numero_siniestro`.

| Campo | Tipo | Descripción | Ejemplo | Clasificación |
|---|---|---|---|---|
| `numero_siniestro` | string `^SIN-\d{8}$` | Identificador del siniestro | `SIN-20000001` | Interna |
| `numero_poliza` | string | Póliza afectada | `POL-10000001` | Interna |
| `tipo` | string | Cobertura afectada | `Pérdida parcial por daños` | Interna |
| `estado` | enum `RADICADO`, `EN_EVALUACION`, `OBJETADO`, `APROBADO`, `PAGADO` | Estado normalizado | `EN_EVALUACION` | Interna |
| `fecha_aviso` | date | Fecha de aviso del siniestro | `2026-09-20` | Interna |
| `ultima_actualizacion` | date | Última gestión registrada | `2026-09-28` | Interna |
| `siguiente_paso` | string | Próxima acción del proceso | `Inspección del vehículo…` | Interna |
| `descripcion_estado` | string (derivado) | Agregado por la herramienta a partir de `estado` | — | Pública |

## 4. Base de conocimiento `kb-condicionados-polizas`

Vertex AI Search, data store no estructurado.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | string | Identificador del fragmento (`<documento>#<clausula>#<n>`) |
| `content` | string | Texto del fragmento (≤ 800 tokens, solapamiento 120) |
| `embedding` | vector float[768] | Generado por `text-embedding-005` (gestionado) |
| `codigo_producto` | string | Producto al que aplica |
| `version_condicionado` | string | Versión radicada del condicionado |
| `clausula` | string | Numeral de la cláusula |
| `pagina` | integer | Página del PDF de origen |
| `vigente_desde` | date | Fecha de entrada en vigencia |
| `tipo_fuente` | enum `CONDICIONADO`, `FAQ` | Origen del fragmento |

## 5. Tabla `ai_lab_agentes.conversaciones_polizas`

BigQuery, poblada por un sink de Cloud Logging. Retención: 13 meses. PII enmascarada antes de
registrarse (los logs reciben el texto ya procesado por los guardrails).

| Campo | Tipo | Descripción |
|---|---|---|
| `timestamp` | TIMESTAMP | Fecha y hora del evento |
| `session_id` | STRING | Sesión de ADK |
| `invocation_id` | STRING | Invocación (turno) |
| `user_id_hash` | STRING | SHA-256 del identificador del usuario en el canal |
| `canal` | STRING | `WEB`, `APP`, `WHATSAPP_ASESOR` |
| `intencion` | STRING | Clasificación posterior (estado, cobertura, siniestro, fuera de alcance) |
| `herramientas` | ARRAY<STRING> | Herramientas invocadas en el turno |
| `status_herramienta` | STRING | `success` / `error` |
| `escalado` | BOOL | Si la conversación terminó con oferta o transferencia a asesor |
| `guardrail_bloqueo` | BOOL | Si el turno fue bloqueado por guardrail o Model Armor |
| `tokens_entrada` / `tokens_salida` | INT64 | Consumo del turno |
| `latencia_ms` | INT64 | Latencia extremo a extremo de `/run` |
| `csat` | INT64 | Calificación 1–5 si el usuario respondió la encuesta |
