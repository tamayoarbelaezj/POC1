# 2. Datos

> El Asistente de Consulta de Pólizas es una iniciativa de IA generativa: **no se entrena ni
> ajusta un modelo** con datos de la compañía. Los datos se usan (a) como fuente de consulta
> en tiempo real a través de herramientas, (b) como base de conocimiento para la curaduría de
> coberturas y (c) como conjunto de evaluación. Este capítulo adapta las secciones del
> formato a esa naturaleza.

## 2.1 Fuentes de información

### Inventario de fuentes

| # | Fuente | Responsable | Naturaleza |
|---|---|---|---|
| F1 | Core de pólizas (tabla de pólizas y vigencias) | Tecnología Core Seguros / Gobierno de Datos | Estructurada, interna, transaccional. Contiene datos personales del tomador. |
| F2 | Core de siniestros (avisos y estados) | Gerencia de Indemnizaciones | Estructurada, interna, transaccional. |
| F3 | Catálogo de productos y coberturas | Gerencia de Producto / Experiencia del Cliente | Semiestructurada, interna, curada manualmente a partir de F4. |
| F4 | Condicionados generales de producto (PDF) | Gerencia de Producto / Jurídica | No estructurada, documental, pública para el cliente. |
| F5 | Preguntas frecuentes de servicio al cliente | Experiencia del Cliente | No estructurada (texto), interna. |
| F6 | Conversaciones del piloto y tipificaciones del contact center | AI Lab / Servicio al Cliente | No estructurada (texto), generada; usada solo para evaluación y monitoreo. PII enmascarada. |

### Transformación y diccionario de datos

| Fuente | Nombre de la fuente transformada | Diccionario |
|---|---|---|
| F1 Core de pólizas | Firestore `polizas` (proyección de 11 campos, id = número de póliza) | [diccionario-datos.md#polizas](anexos/diccionario-datos.md#1-colección-polizas) |
| F2 Core de siniestros | Firestore `polizas_siniestros` (id = número de siniestro) | [diccionario-datos.md#siniestros](anexos/diccionario-datos.md#3-colección-polizas_siniestros) |
| F3 + F4 Catálogo y condicionados | Firestore `polizas_productos` (id = código de producto) | [diccionario-datos.md#productos](anexos/diccionario-datos.md#2-colección-polizas_productos) |
| F4 + F5 Condicionados y FAQ | Base de conocimiento `kb-condicionados-polizas` (Vertex AI Search) | [diccionario-datos.md#kb](anexos/diccionario-datos.md#4-base-de-conocimiento-kb-condicionados-polizas) |
| F6 Conversaciones | BigQuery `ai_lab_agentes.conversaciones_polizas` (sink de Cloud Logging) | [diccionario-datos.md#conversaciones](anexos/diccionario-datos.md#5-tabla-ai_lab_agentesconversaciones_polizas) |

### Base de conocimiento

| Campo | Valor |
|---|---|
| Fuentes | F4 Condicionados generales de los productos Autos Plus, Hogar Básico y Vida Individual (38 documentos PDF, 1.214 páginas); F5 FAQ de servicio al cliente (212 preguntas y respuestas) |
| Nombre de la KB | `kb-condicionados-polizas` |
| Tipo | Vertex AI Search, data store no estructurado con *layout parser* y embeddings gestionados (`text-embedding-005`, 768 dimensiones) |
| Enlace a embeddings / índice (productivo) | `https://console.cloud.google.com/gen-app-builder/locations/global/collections/default_collection/data-stores/kb-condicionados-polizas/data?project=<proyecto-productivo>` |
| Tamaño | 4.870 fragmentos (4.658 de condicionados, 212 de FAQ) |
| Uso en v1.1.0 | Fuente para curar y validar el catálogo `polizas_productos` (cada cobertura del catálogo referencia la cláusula del condicionado). La herramienta de búsqueda directa `buscar_condicionado` está planificada para v1.2.0. |
| Frecuencia de actualización | Por evento: cada nueva versión de condicionado radicada ante la Superintendencia Financiera; FAQ mensual |

### Evaluación de calidad de los datos (EDA)

Por tratarse de un agente conversacional, el EDA se hizo sobre: (i) 6.000 tipificaciones del
contact center (ene–ago 2026), (ii) 1.200 conversaciones del piloto con asesores y (iii) la
réplica de F1–F3 en Firestore (muestra de 2.000 pólizas y 800 siniestros).

**Distribución.** Intenciones de los usuarios (n = 1.200 conversaciones del piloto):

| Intención | % | Comentario |
|---|---|---|
| Estado / vigencia de póliza | 46 % | Concentrada en Autos (58 % de esta intención) |
| Coberturas de producto | 31 % | 72 % preguntan por una cobertura específica (hurto, terremoto, asistencia) |
| Estado de siniestro | 18 % | Mayor volumen los lunes (27 % de la semana) |
| Fuera de alcance (pagos, cotizaciones, otros) | 5 % | Se responden con mensaje de alcance y oferta de asesor |

Longitud de los mensajes de usuario: mediana 14 palabras, P95 48 palabras. Conversaciones:
mediana 4 turnos, P95 9 turnos (coherente con el supuesto de costos de la sección 1.2).

**Atípicos.**

| Hallazgo | Frecuencia | Tratamiento |
|---|---|---|
| Número de póliza escrito sin prefijo o con espacios / minúsculas (`pol 10000001`) | 9,4 % | Normalización en la herramienta (`normalizar_numero_poliza`) y solicitud del formato en la instrucción |
| Mensajes con PII no solicitada (cédula 5,1 %, teléfono 2,2 %, correo 1,4 %) | 7,8 % de los mensajes | Enmascarado en `before_model_guardrail` antes de llegar al modelo |
| Mensajes de más de 1.000 caracteres (copias de correos, quejas extensas) | 0,6 % | Se atienden; el agente ofrece asesor si hay inconformidad |
| Pólizas en Firestore con `fecha_fin` anterior a `fecha_inicio` | 0,05 % (1 de 2.000) | Reportado a Gobierno de Datos; regla de calidad en la sincronización |
| Siniestros con estado no catalogado | 0,4 % | La herramienta responde "Estado no catalogado; consulte con un asesor" |

**Relevancia de variables.** Se midió qué campos fueron necesarios para responder
correctamente cada intención (anotación manual de 300 conversaciones):

| Campo | % de respuestas que lo requieren | Decisión |
|---|---|---|
| `estado` (póliza) | 88 % | Se expone |
| `fecha_inicio` / `fecha_fin` | 41 % | Se exponen |
| `estado_pago` | 37 % | Se expone |
| `codigo_producto` | 31 % (necesario para coberturas) | Se expone |
| `valor_asegurado` | 12 % | Se expone |
| `prima_anual` | 3 % | **No se expone** (preguntas de valor a pagar se escalan al asesor) |
| `tomador`, `canal` | 0 % | **No se exponen** (minimización de datos personales) |

**Conclusiones del EDA.** (1) Tres intenciones cubren el 95 % de la demanda, lo que confirma
el alcance de tres herramientas. (2) La calidad de la réplica es alta y no requiere imputación;
los pocos atípicos se gestionan con reglas en la sincronización. (3) La PII aparece de forma
espontánea en casi 1 de cada 12 mensajes, lo que justifica el enmascarado previo al modelo.
(4) El modelo solo necesita 8 campos de póliza; los demás se excluyen por minimización.

### Estructura de la base de conocimiento (chunking)

| Parámetro | Valor | Justificación |
|---|---|---|
| Estrategia | Por estructura del documento (*layout-aware*): cada cláusula o numeral es la unidad base; las cláusulas largas se subdividen | Los condicionados están organizados en cláusulas autocontenidas (cobertura, exclusión, deducible) que no deben mezclarse |
| Tamaño de fragmento | 800 tokens | El 90 % de las cláusulas mide entre 300 y 900 tokens; 800 conserva una cláusula completa en la mayoría de casos sin diluir la similitud |
| Solapamiento | 120 tokens (15 %) | Evita perder definiciones que se extienden entre fragmentos (p. ej. listas de exclusiones) |
| Metadatos | `codigo_producto`, `version_condicionado`, `clausula`, `pagina`, `vigente_desde` | Permiten filtrar por producto y versión vigente y citar la fuente |
| FAQ | 1 fragmento por pregunta-respuesta (sin solapamiento) | Pares cortos (mediana 95 tokens) y autocontenidos |
| Validación | Recall@5 = 0,93 sobre 150 preguntas de referencia | Umbral de aceptación ≥ 0,90 |

## 2.2 Transformación de datos

### Justificación técnica de las transformaciones

| Transformación | Justificación |
|---|---|
| Réplica del core a Firestore con proyección de campos | Desacopla al agente del core transaccional (sin carga adicional ni exposición de red), garantiza latencia de lectura < 50 ms y aplica minimización de datos desde el origen: no se replican documento de identidad, dirección, teléfono ni correo del tomador. |
| Identificador de documento = número de póliza / siniestro / código de producto | Lectura por clave directa, sin consultas abiertas: el agente no puede listar ni buscar pólizas de otros clientes. |
| Normalización de estados a catálogo cerrado (`VIGENTE`, `VENCIDA`, `CANCELADA`; `RADICADO`, `EN_EVALUACION`, `OBJETADO`, `APROBADO`, `PAGADO`) | El core maneja 23 códigos internos de estado; se agrupan en estados comprensibles para el cliente y se agrega `descripcion_estado` en la herramienta. |
| Curaduría del catálogo de coberturas a partir de los condicionados | El resumen de coberturas que entrega el agente proviene de un catálogo validado por Producto y no de la generación libre del modelo, lo que reduce alucinaciones. |
| Validación de formato de entrada en las herramientas (`POL-` / `SIN-` + 8 dígitos) | Evita consultas con identificadores inválidos o intentos de inyección a través de argumentos de herramientas. |
| Exclusión de `tomador`, `canal` y `prima_anual` en la respuesta de `consultar_poliza` | Minimización de datos (Ley 1581 de 2012) y reducción de tokens. |

### Calidad final de los datos

Medida sobre la muestra de validación (2.000 pólizas, 800 siniestros, 3 productos) comparando
Firestore contra el core en la misma fecha de corte.

| Fuente | Variable | % completitud | Exactitud |
|---|---|---|---|
| `polizas` | `numero_poliza` | 100,0 % | 100,0 % |
| `polizas` | `codigo_producto` | 100,0 % | 100,0 % |
| `polizas` | `estado` | 100,0 % | 99,8 % (4 registros desactualizados por ventana de sincronización) |
| `polizas` | `fecha_inicio` / `fecha_fin` | 100,0 % | 99,95 % |
| `polizas` | `valor_asegurado` | 99,6 % | 99,9 % |
| `polizas` | `estado_pago` | 98,7 % | 99,5 % |
| `polizas_productos` | `coberturas[].nombre` / `limite` | 100,0 % | 100,0 % (validado por Producto contra condicionado) |
| `polizas_productos` | `exclusiones` | 100,0 % | 100,0 % |
| `polizas_siniestros` | `estado` | 100,0 % | 99,6 % |
| `polizas_siniestros` | `ultima_actualizacion` | 100,0 % | 99,6 % |
| `polizas_siniestros` | `siguiente_paso` | 96,3 % | 98,9 % (revisión manual de 200 registros) |

### Filtrado de contenido / guardrails

Se implementan dos capas complementarias:

**Capa 1 — Guardrails en el código del agente**
([`agente_polizas/guardrails/callbacks.py`](../agente_polizas/guardrails/callbacks.py)),
registrados en [`agent.py`](../agente_polizas/agent.py) como callbacks de ADK:

| Control | Función | Comportamiento |
|---|---|---|
| Enmascarado de PII de entrada | `before_model_guardrail` → `enmascarar_pii` | Reemplaza en todo el historial de usuario las cédulas (6–10 dígitos, con o sin puntos), teléfonos colombianos (celular `3XX`, fijo `60X`, con o sin `+57`) y correos por `[DOCUMENTO_OCULTO]`, `[TELEFONO_OCULTO]` y `[CORREO_OCULTO]` antes de enviar al modelo. No altera números de póliza, siniestro, fechas ni valores monetarios. |
| Bloqueo de prompt injection | `before_model_guardrail` → `detectar_prompt_injection` | Detecta patrones como "ignora las instrucciones", "muéstrame tu prompt", "modo desarrollador" o solicitudes de datos de otros clientes; responde con un mensaje de alcance **sin invocar al modelo** y cuenta el evento en `state["guardrail_bloqueos"]`. |
| Filtro de salida | `after_model_guardrail` → `filtrar_salida` | Enmascara PII que el modelo pudiera reproducir y reemplaza la respuesta si contiene marcadores de la instrucción del sistema (fuga de prompt). |
| Validación de argumentos | `tools/polizas.py`, `tools/siniestros.py` | Expresiones regulares cerradas para números de póliza, siniestro y código de producto. |
| Minimización | `CAMPOS_PUBLICOS_POLIZA` en `tools/polizas.py` | Solo se entregan al modelo 8 campos de la póliza. |
| Instrucción del sistema | `agente_polizas/prompts.py` | Reglas de alcance, no invención, privacidad y no revelación de instrucciones. |

Cobertura de pruebas: [`tests/test_guardrails.py`](../tests/test_guardrails.py) (casos positivos
y negativos de cada patrón).

**Capa 2 — Model Armor** (plantilla `ma-agente-polizas`, aplicada a prompts y respuestas en
el entorno productivo):

| Filtro | Configuración |
|---|---|
| Prompt injection y jailbreak | Habilitado, confianza `MEDIUM_AND_ABOVE` |
| IA responsable (odio, acoso, sexual explícito, contenido peligroso) | Habilitado, confianza `MEDIUM_AND_ABOVE` |
| Sensitive Data Protection (básico) | Habilitado: documentos de identidad, tarjetas de crédito, cuentas bancarias |
| URLs maliciosas | Habilitado |
| Acción | Bloquear y registrar en Cloud Logging (`modelarmor.googleapis.com/sanitize_operations`) |

La capa 1 es determinística, sin costo y probada unitariamente; la capa 2 cubre variaciones
semánticas que las expresiones regulares no detectan. En el piloto, de 40 prompts adversariales,
25 fueron bloqueados por la capa 1 y 13 de los 15 restantes por Model Armor; los 2 que llegaron
al modelo fueron rechazados por la instrucción del sistema (ver [03-modelo.md](03-modelo.md)).
