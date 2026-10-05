# 3. Modelo

> No se entrena un modelo propio: se selecciona un modelo fundacional de Vertex AI y se
> construye un agente con instrucción, herramientas y guardrails. La evaluación se centra en
> el **comportamiento del agente completo** (uso correcto de herramientas, fidelidad de las
> respuestas, robustez, latencia y costo).

## 3.1 Evaluación comparativa de modelos

### Conjuntos de evaluación

| Conjunto | Contenido | Ubicación |
|---|---|---|
| Evalset ADK | 8 casos de referencia (estado de póliza, coberturas en dos pasos, siniestro, solicitud de número, póliza inexistente, fuera de alcance, prompt injection, PII) con trayectoria esperada de herramientas y respuesta de referencia | [`tests/eval/polizas.evalset.json`](../tests/eval/polizas.evalset.json), criterios en [`tests/eval/test_config.json`](../tests/eval/test_config.json) |
| Conversaciones de referencia | 120 conversaciones (480 turnos) del piloto con asesores, anotadas manualmente por Experiencia del Cliente | BigQuery `ai_lab_agentes.eval_referencia_polizas` |
| Set adversarial | 40 prompts de inyección, jailbreak y extracción de datos; 15 de ellos superan la capa 1 de guardrails y se usan para medir la robustez propia del modelo (sin Model Armor) | BigQuery `ai_lab_agentes.eval_adversarial_polizas` |

Ejecución del evalset:

```bash
adk eval agente_polizas tests/eval/polizas.evalset.json --config_file_path tests/eval/test_config.json
```

Todos los modelos se probaron con la misma instrucción, herramientas, guardrails,
`temperature=0.2` y datos ficticios, 2 corridas por caso.

### Resultados

| Tipo de prueba | Modelo testeado | Justificación de la prueba | Métrica | Valor |
|---|---|---|---|---|
| Trayectoria de herramientas | gemini-2.5-flash | Verifica que el agente llame la herramienta correcta con los argumentos correctos (no responder sin consultar) | `tool_trajectory_avg_score` (evalset + 120 conv.) | **0,97** |
| Trayectoria de herramientas | gemini-2.5-pro | Ídem | `tool_trajectory_avg_score` | 0,98 |
| Trayectoria de herramientas | gemini-2.0-flash | Ídem | `tool_trajectory_avg_score` | 0,91 |
| Calidad de respuesta | gemini-2.5-flash | Similitud con la respuesta de referencia validada por negocio | `response_match_score` (ROUGE-1) | **0,71** |
| Calidad de respuesta | gemini-2.5-pro | Ídem | `response_match_score` | 0,74 |
| Calidad de respuesta | gemini-2.0-flash | Ídem | `response_match_score` | 0,66 |
| Fidelidad (alucinación) | gemini-2.5-flash | Riesgo principal: informar datos no soportados por las herramientas | % de turnos con dato no soportado (revisión humana, 480 turnos) | **0,8 %** (4/480) |
| Fidelidad (alucinación) | gemini-2.5-pro | Ídem | Ídem | 0,4 % (2/480) |
| Fidelidad (alucinación) | gemini-2.0-flash | Ídem | Ídem | 2,5 % (12/480) |
| Robustez adversarial | gemini-2.5-flash | Medir la resistencia del modelo a prompts que evaden la capa 1 | % de rechazos correctos (15 prompts, sin Model Armor) | **93,3 %** (14/15) |
| Robustez adversarial | gemini-2.5-pro | Ídem | Ídem | 100 % (15/15) |
| Robustez adversarial | gemini-2.0-flash | Ídem | Ídem | 73,3 % (11/15) |
| Latencia | gemini-2.5-flash | Experiencia conversacional: meta P90 ≤ 4 s por turno | P50 / P90 por turno (`/run`) | **2,1 s / 3,4 s** |
| Latencia | gemini-2.5-pro | Ídem | P50 / P90 | 5,8 s / 9,6 s |
| Latencia | gemini-2.0-flash | Ídem | P50 / P90 | 1,4 s / 2,3 s |
| Costo | gemini-2.5-flash | Sostenibilidad del caso de negocio (sección 1.2) | USD de tokens por 1.000 conversaciones | **7,25** |
| Costo | gemini-2.5-pro | Ídem | Ídem | 29,75 |
| Costo | gemini-2.0-flash | Ídem | Ídem | 2,91 |

Costos calculados con el consumo medio del piloto (15.000 tokens de entrada y 1.100 de
salida por conversación) y precios de lista: 2.5 Flash USD 0,30 / 2,50; 2.5 Pro USD 1,25 / 10,00;
2.0 Flash USD 0,15 / 0,60 por millón de tokens de entrada / salida.

### Criterios de aceptación y modelo ganador

| Criterio | Umbral | 2.5 Flash | 2.5 Pro | 2.0 Flash |
|---|---|---|---|---|
| Trayectoria | ≥ 0,95 | Cumple | Cumple | No cumple |
| Alucinación | ≤ 1,0 % | Cumple | Cumple | No cumple |
| Robustez adversarial (modelo solo) | ≥ 90 % | Cumple | Cumple | No cumple |
| Latencia P90 | ≤ 4 s | Cumple | No cumple | Cumple |
| Costo por 1.000 conversaciones | ≤ USD 10 | Cumple | No cumple | Cumple |

**Modelo seleccionado: `gemini-2.5-flash`.** Es el único que cumple los cinco criterios.
`gemini-2.5-pro` obtiene una calidad ligeramente superior (+0,01 en trayectoria, −0,4 pp de
alucinación) que no justifica una latencia 2,8 veces mayor (P90 9,6 s) ni un costo 4,1 veces
superior. `gemini-2.0-flash` es el más rápido y barato, pero triplica la tasa de alucinación y
falla en la secuencia de dos herramientas (póliza → coberturas). La brecha de robustez de 2.5
Flash (1 de 15) queda cubierta por Model Armor: con las dos capas activas, los 40 prompts
adversariales fueron rechazados.

El modelo es configurable por la variable `MODEL`, lo que permite repetir esta comparación con
nuevas versiones sin cambios de código.

## 3.2 KPIs del modelo

| KPI | Fórmula | Rango de normalidad | Umbral de alerta |
|---|---|---|---|
| Tasa de contención | conversaciones sin escalamiento / conversaciones totales | 55 % – 70 % | < 50 % semanal |
| Fidelidad (alucinación) | turnos con dato no soportado / turnos revisados (muestra semanal de 100 conversaciones) | ≤ 1,0 % | > 2,0 % |
| Éxito de herramientas | llamadas con `status = success` / llamadas totales | 85 % – 95 % (los errores incluyen números inexistentes digitados por el usuario) | < 80 % en 1 h |
| Errores de infraestructura | llamadas con "no está disponible" / llamadas totales | < 0,5 % | > 2 % en 15 min |
| Latencia por turno | percentil 90 de la latencia de `/run` | ≤ 4 s | > 6 s durante 15 min |
| Tasa de bloqueo por guardrails | turnos bloqueados (capa 1 + Model Armor) / turnos totales | 0,5 % – 3 % | > 5 % en 1 h (posible ataque) o 0 % en 24 h (guardrail inactivo) |
| CSAT del canal | promedio de calificaciones 1–5 | ≥ 4,2 | < 3,8 semanal |
| Costo por 1.000 conversaciones | costo diario (tokens + infraestructura) / conversaciones × 1.000 | USD 10 – 13 | > USD 15 |
| Tokens por conversación | (tokens entrada + salida) / conversaciones | 14.000 – 18.000 | > 22.000 |
| Disponibilidad | minutos con `/health` exitoso / minutos totales | ≥ 99,5 % mensual | 2 fallas consecutivas del uptime check |

## 3.3 Plan de monitoreo

| Métrica | Umbral | Protocolo de mitigación | Periodicidad |
|---|---|---|---|
| Latencia P90 | > 6 s durante 15 min | Alerta a guardia AI Lab. Revisar Cloud Trace (modelo vs. Firestore). Si es el modelo: verificar cuota y estado de Vertex AI; si persiste 30 min, aumentar `min-instances` y activar mensaje de contingencia con oferta de asesor. | Continua (alerta en Cloud Monitoring) |
| Errores 5xx / errores de infraestructura | > 2 % en 15 min | Alerta crítica. Revisar logs; si es Firestore o sincronización, escalar a Datos; rollback a la revisión anterior de Cloud Run si coincide con un despliegue. | Continua |
| Disponibilidad (`/health`) | 2 fallas consecutivas | Alerta crítica. Los canales redirigen al contact center (degradación controlada). | Cada 1 min |
| Tasa de bloqueo por guardrails | > 5 % en 1 h o 0 % en 24 h | Revisar muestras bloqueadas: si es ataque, informar a Seguridad de la Información y aplicar Cloud Armor por IP; si es falso positivo, ajustar patrones con prueba unitaria. Si es 0 %, verificar que los callbacks y Model Armor estén activos. | Horaria |
| Fidelidad (alucinación) | > 2 % en la muestra semanal | Analizar casos, reforzar instrucción o herramienta, ejecutar evalset y desplegar corrección. Si supera 5 %, suspender el canal para clientes y dejar solo asesores. | Semanal (muestra de 100 conversaciones) |
| Contención | < 50 % semanal | Analizar intenciones escaladas; priorizar nuevas herramientas o FAQ con Experiencia del Cliente. | Semanal |
| CSAT | < 3,8 semanal | Revisión conjunta con el responsable de negocio de conversaciones con calificación 1–2. | Semanal |
| Costo por 1.000 conversaciones | > USD 15 diario | Revisar tokens por conversación (historial excesivo, bucles de herramientas); ajustar presupuesto de razonamiento o recorte de historial. Alerta de presupuesto de facturación al 80 % y 100 %. | Diaria |
| Equidad por segmento | razón de contención entre segmentos < 0,80 | Ver sección 3.4. Análisis de causa y plan de ajuste con negocio. | Mensual |
| Deriva de intenciones | fuera de alcance > 10 % mensual | Evaluar ampliación de alcance o mejora del mensaje de los canales. | Mensual |

**Dashboard:** Cloud Monitoring — *Agente Pólizas – Operación*
`https://console.cloud.google.com/monitoring/dashboards/builder/agente-polizas-operacion?project=<proyecto-productivo>`

Las métricas de negocio (contención, CSAT, equidad) se calculan sobre la tabla
`ai_lab_agentes.conversaciones_polizas` y se publican en el mismo dashboard como métricas
basadas en logs y en el tablero de Looker Studio *Agente Pólizas – Negocio*.

## 3.4 Análisis de sesgo y equidad

**Alcance.** El agente no toma decisiones que afecten derechos u obligaciones del cliente; el
riesgo de sesgo se manifiesta como **diferencias en la calidad del servicio** (resolver o no la
consulta, exactitud, satisfacción) entre grupos. No se usan ni se infieren variables
sensibles como género, etnia u orientación; los segmentos se obtienen de metadatos del canal y
de la póliza (región de expedición, rango de edad del tomador), unidos a la conversación de
forma seudonimizada solo para este análisis.

**Datos:** 1.200 conversaciones del piloto (septiembre 2026). Criterio de disparidad: razón
entre el segmento con menor y mayor valor de la métrica (regla de los 4/5) < 0,80, o diferencia
de exactitud > 3 pp.

### Por región

| Segmento | n | Contención | Exactitud | CSAT | P90 latencia |
|---|---|---|---|---|---|
| Andina | 636 | 62,4 % | 95,6 % | 4,3 | 3,4 s |
| Caribe | 300 | 59,3 % | 94,0 % | 4,2 | 3,4 s |
| Pacífico | 180 | 60,6 % | 95,0 % | 4,3 | 3,3 s |
| Orinoquía / Amazonía | 84 | 57,1 % | 94,0 % | 4,2 | 3,5 s |
| **Total** | **1.200** | **61,0 %** | **95,0 %** | **4,3** | **3,4 s** |
| Razón mín / máx (contención) | | **0,92** | Dif. exactitud: 1,6 pp | | |

### Por canal

| Segmento | n | Contención | Exactitud | CSAT | P90 latencia |
|---|---|---|---|---|---|
| Web | 504 | 61,5 % | 95,2 % | 4,3 | 3,4 s |
| App | 420 | 64,3 % | 95,0 % | 4,4 | 3,3 s |
| WhatsApp de asesores | 276 | 55,0 % | 94,6 % | 4,1 | 3,6 s |
| Razón mín / máx (contención) | | **0,86** | Dif. exactitud: 0,6 pp | | |

### Por rango de edad del tomador (solo clientes, canales web y app)

| Segmento | n | Contención | Exactitud | CSAT | P90 latencia |
|---|---|---|---|---|---|
| 18 – 30 años | 210 | 66,7 % | 95,5 % | 4,4 | 3,3 s |
| 31 – 45 años | 342 | 66,1 % | 95,1 % | 4,4 | 3,3 s |
| 46 – 60 años | 246 | 61,7 % | 95,1 % | 4,3 | 3,4 s |
| Mayores de 60 años | 126 | 49,2 % | 94,4 % | 3,9 | 3,5 s |
| **Total clientes** | **924** | **62,8 %** | **95,1 %** | **4,3** | **3,4 s** |
| Razón mín / máx (contención) | | **0,74 — disparidad** | Dif. exactitud: 1,1 pp | | |

### Justificación y acciones

- **Región:** sin disparidad (razón 0,92; exactitud dentro de 1,6 pp). La leve diferencia en
  Caribe se asocia a expresiones coloquiales al pedir coberturas ("¿me cubre si se me meten a
  la casa?"); se agregarán 30 variaciones regionales al conjunto de referencia.
- **Canal:** sin disparidad (0,86). La menor contención en WhatsApp de asesores es esperada:
  el asesor usa el agente como apoyo y escala casos complejos por diseño.
- **Edad (> 60 años): disparidad detectada (0,74).** La exactitud es equivalente (94,4 % vs
  95,5 %), es decir, el agente responde correctamente, pero estos usuarios solicitan asesor con
  más frecuencia y califican peor la experiencia. Causas identificadas en la revisión de 60
  conversaciones: mensajes con varias preguntas a la vez, términos técnicos en la respuesta
  (deducible, SMMLV) y preferencia explícita por atención humana. Acciones:
  1. Ajuste de la instrucción para explicar términos técnicos y responder una pregunta a la vez
     (probado sobre réplica de las 126 conversaciones: contención 55,6 %, razón 0,83). Se
     desplegará en v1.2.0.
  2. Botón permanente "Hablar con un asesor" en web y app, sin penalizar la métrica de
     contención para este segmento.
  3. Seguimiento mensual de la razón por edad en el plan de monitoreo (umbral 0,80).
- Escalar a un asesor nunca se considera un resultado adverso para el cliente: la disparidad
  afecta la eficiencia del canal, no el acceso al servicio.
