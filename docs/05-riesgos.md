# 5. Gestión de riesgos

## Escala de valoración

Escala tomada del formato *Documentación Modelos Analíticos (ML) e iniciativas de IA*.
**Atención:** en la escala de probabilidad el valor **1 corresponde a la mayor probabilidad**
(Casi seguro) y el 5 a la menor (Raro).

### Probabilidad

| Valor | Nivel |
|---|---|
| 1 | Casi seguro |
| 2 | Probable |
| 3 | Posible |
| 4 | Improbable |
| 5 | Raro |

### Impacto

| Valor | Nivel |
|---|---|
| 1 | Insignificante |
| 2 | Menor |
| 3 | Moderado |
| 4 | Mayor |
| 5 | Severo |

## Matriz de riesgos

Valoración del **riesgo residual**, es decir, considerando los controles ya implementados en
la versión v1.1.0.

| # | Riesgo | Descripción específica | Controles implementados | Probabilidad | Impacto |
|---|---|---|---|---|---|
| R1 | Veracidad / alucinaciones | El agente informa un estado de póliza, una vigencia, un valor asegurado o una cobertura que no corresponde a la realidad (p. ej. afirma que una póliza vencida está vigente o que un evento excluido está cubierto), lo que puede generar reclamaciones y quejas ante la Superintendencia Financiera. | (1) Las cifras y estados provienen solo de herramientas con lectura por clave (`tools/polizas.py`, `tools/siniestros.py`); (2) regla 2 de la instrucción: no inventar y explicar `error_message` (`prompts.py`); (3) coberturas desde catálogo curado por Producto, no generadas; (4) remisión al condicionado y al área de indemnizaciones (regla 6); (5) `temperature=0.2`; (6) evalset ADK con caso de póliza inexistente y medición de alucinación 0,8 % (`docs/03-modelo.md`); (7) muestreo semanal de 100 conversaciones con umbral de alerta 2 %. | 4 — Improbable | 3 — Moderado |
| R2 | Seguridad de datos y privacidad (Ley 1581 de 2012 / habeas data) | Exposición de datos personales del cliente o de terceros: el modelo repite una cédula o teléfono, un usuario obtiene información de una póliza ajena conociendo su número, o la PII queda almacenada en logs o enviada al proveedor del modelo sin necesidad. | (1) `before_model_guardrail` enmascara cédulas, correos y teléfonos colombianos en todo el historial antes de llegar al modelo (`guardrails/callbacks.py`); (2) `after_model_guardrail` enmascara PII en la salida; (3) minimización: `consultar_poliza` excluye tomador, canal y prima (`CAMPOS_PUBLICOS_POLIZA`); (4) réplica en Firestore sin documento, dirección, teléfono ni correo; (5) lectura solo por clave, sin búsquedas abiertas; (6) detección de solicitudes de datos de otros clientes como inyección; (7) Model Armor con Sensitive Data Protection; (8) Vertex AI sin retención de datos para entrenamiento y procesamiento en `us-central1` bajo contrato corporativo; (9) Cloud Run privado con IAM y cuenta de servicio de mínimo privilegio (`roles/datastore.viewer`); (10) los canales autentican al cliente antes de abrir la conversación y envían un `user_id` seudonimizado; (11) logs con PII ya enmascarada y retención de 13 meses. | 4 — Improbable | 4 — Mayor |
| R3 | Propiedad intelectual | Uso en las respuestas de contenido protegido de terceros o divulgación indebida de documentos internos (manuales, tarifas) como si fueran públicos. | (1) El agente solo responde con datos de fuentes propias de la compañía (core, catálogo curado y condicionados públicos radicados); (2) no se usa contenido de terceros en la base de conocimiento; (3) la instrucción limita el alcance a pólizas, coberturas y siniestros; (4) los términos de servicio de Vertex AI otorgan indemnización por propiedad intelectual sobre los resultados del modelo; (5) código desarrollado por el AI Lab sobre librerías con licencia Apache 2.0 (ADK, SDK de Google Cloud). | 5 — Raro | 2 — Menor |
| R4 | Sesgos y toxicidad | Calidad de servicio desigual entre grupos de clientes (detectado: menor contención en mayores de 60 años) o respuestas ofensivas, discriminatorias o con tono inapropiado. | (1) Análisis de equidad por región, canal y edad con regla 4/5 (`docs/03-modelo.md` §3.4) y plan de ajuste para mayores de 60 años; (2) monitoreo mensual de la razón de contención por segmento; (3) filtros de IA responsable de Model Armor y de Vertex AI (odio, acoso, contenido peligroso); (4) instrucción con tono cordial y lenguaje claro; (5) el agente no toma decisiones sobre el cliente y siempre ofrece un asesor humano. | 3 — Posible | 2 — Menor |
| R5 | Inyección de prompts | Un usuario intenta que el agente ignore sus reglas, revele la instrucción del sistema, actúe fuera de alcance o consulte información de otros clientes. | (1) `detectar_prompt_injection` bloquea patrones conocidos sin invocar al modelo (`guardrails/callbacks.py`); (2) Model Armor con detección de prompt injection y jailbreak; (3) regla 8 de la instrucción: no revelar instrucciones; (4) `filtrar_salida` reemplaza respuestas con marcadores de la instrucción; (5) las herramientas validan argumentos con expresiones regulares cerradas y solo leen; el agente no tiene herramientas de escritura; (6) set adversarial de 40 prompts con 100 % de rechazo con las dos capas; (7) alerta si la tasa de bloqueo supera 5 % en 1 h. | 2 — Probable (los intentos son esperables en un canal público) | 2 — Menor (el alcance del daño está acotado a lectura por clave) |
| R6 | Disponibilidad / dependencia del proveedor | Indisponibilidad o degradación de Vertex AI, agotamiento de cuota (429 observado en estrés), retiro o cambio de comportamiento de la versión del modelo, o caída de Cloud Run / Firestore. | (1) Modelo configurable por variable `MODEL` y evalset para validar cambios de versión antes de migrar; (2) `min-instances=1` y escalamiento hasta 10 instancias; (3) uptime check sobre `/health` y alertas de latencia y errores (`docs/03-modelo.md` §3.3); (4) degradación controlada: los canales redirigen al contact center; (5) plan de acción de pruebas de carga: aumento de cuota, reintentos con *backoff*, mensaje de contingencia (`docs/04-pruebas-carga.md`); (6) ADK es de código abierto, lo que reduce el acoplamiento a una plataforma de orquestación propietaria. | 3 — Posible | 2 — Menor |
| R7 | Costos descontrolados | Crecimiento no previsto del consumo de tokens (historial largo, bucles de herramientas, abuso automatizado del canal) o del número de instancias que deteriora el caso de negocio. | (1) `max_output_tokens=1024` y `max-instances=10`; (2) KPI de tokens por conversación (alerta > 22.000) y de costo por 1.000 conversaciones (alerta > USD 15); (3) alertas de presupuesto de facturación al 80 % y 100 %; (4) bloqueo de inyecciones sin invocar al modelo (costo cero); (5) autenticación IAM y Cloud Armor con límite de tasa por cliente en el balanceador; (6) análisis de sensibilidad: duplicar tokens mantiene ROI de 288 % (`docs/01-negocio.md`). | 4 — Improbable | 2 — Menor |
| R8 | Datos desactualizados | La réplica en Firestore no refleja un cambio reciente del core (pago, cancelación, cambio de estado de siniestro) y el agente informa un estado anterior. | (1) Sincronización cada 15 min con alerta si la frescura supera 30 min; (2) exactitud medida de 99,8 % en `estado` (`docs/02-datos.md`); (3) el agente informa la fecha de última actualización del siniestro; (4) ante inconformidad ofrece un asesor. | 3 — Posible | 2 — Menor |

## Riesgos fuera del umbral de apetito y seguimiento

- **R2** es el de mayor impacto residual (Mayor). Se mantiene con probabilidad Improbable por
  la combinación de minimización, enmascarado y autenticación del canal. Cualquier ampliación
  del alcance que incluya nuevos datos personales requiere evaluación de impacto de privacidad
  con el Oficial de Protección de Datos.
- **R4** tiene un plan de acción abierto (ajuste de instrucción para mayores de 60 años, v1.2.0).
- **R6** tiene un plan de acción abierto (cuota y reintentos, octubre–noviembre 2026).

Los riesgos se revisan trimestralmente o ante cualquier incidente, cambio de modelo o
ampliación del alcance.
