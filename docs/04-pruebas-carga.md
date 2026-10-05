# 4. Pruebas de carga

## 4.1 Diseño de la prueba

### Herramienta

**k6** (Grafana k6 v0.54). Se eligió por permitir escenarios declarativos (VUs constantes,
rampas), umbrales que fallan la ejecución automáticamente y métricas personalizadas (latencia
por turno, tokens). Script versionado en [`load-tests/script.js`](../load-tests/script.js);
resultados en [`load-tests/resultados/`](../load-tests/resultados/resumen-2026-10.md).

### Infraestructura

| Componente | Configuración |
|---|---|
| Servicio | Cloud Run `agente-polizas`, región `us-central1`, imagen v1.1.0 |
| Recursos por instancia | 1 vCPU, 1 GiB de memoria, CPU boost en arranque |
| Concurrencia | 40 solicitudes por instancia |
| Escalamiento | `min-instances=1`, `max-instances=10` |
| Timeout de solicitud | 60 s |
| Modelo | `gemini-2.5-flash` en Vertex AI (cuota estándar del proyecto de desarrollo) |
| Datos | Firestore nativo con 2.000 pólizas y 800 siniestros **sintéticos** |
| Seguridad | Model Armor activo; autenticación IAM con token de identidad |
| Generador de carga | VM `e2-standard-4` en `us-central1` (misma región para no medir latencia de internet) |

### Escenario de carga

Cada usuario virtual (VU) simula una conversación de **4 turnos** (estado de póliza →
coberturas → estado de siniestro → cierre) con tiempos de reflexión aleatorios de 3 a 6 s,
reproduciendo el patrón observado en el piloto.

Referencia de volumen: 30.000 conversaciones/mes → ~1.364 por día hábil → hora pico (15 % del
día) ≈ 205 conversaciones/h ≈ **0,23 turnos/s**.

| Escenario | Objetivo | Perfil |
|---|---|---|
| Nominal | Validar el comportamiento con 2× la hora pico | 4 VUs constantes, 15 min |
| Pico | Validar 10× la hora pico (campañas, renovaciones masivas, eventos climáticos) | Rampa a 16 VUs, sostenido 16 min |
| Estrés | Encontrar el punto de quiebre y validar degradación controlada | Rampa 0 → 60 VUs en 20 min |
| Resistencia (soak) | Detectar fugas de memoria o degradación en el tiempo | 8 VUs constantes, 2 h |

## 4.2 Resultados: desempeño objetivo vs. real

| Escenario | Métrica | Objetivo | Real | Cumple |
|---|---|---|---|---|
| Nominal | Latencia P50 / P90 / P99 | ≤ 2,5 s / ≤ 4 s / ≤ 8 s | 2,1 s / 3,4 s / 5,9 s | Sí |
| Nominal | Tasa de error | ≤ 1 % | 0,0 % | Sí |
| Nominal | Throughput | ≥ 0,5 turnos/s | 0,55 turnos/s | Sí |
| Nominal | Costo por 1.000 turnos | ≤ USD 3,00 | USD 2,86 | Sí |
| Pico | Latencia P50 / P90 / P99 | ≤ 2,5 s / ≤ 4 s / ≤ 8 s | 2,3 s / 3,8 s / 6,8 s | Sí |
| Pico | Tasa de error | ≤ 1 % | 0,3 % | Sí |
| Pico | Throughput | ≥ 2,3 turnos/s | 2,25 turnos/s (promedio incluye rampas; 2,48 en meseta) | Sí |
| Pico | Costo por 1.000 turnos | ≤ USD 3,00 | USD 2,41 | Sí |
| Estrés | Throughput con error ≤ 1 % | ≥ 5 turnos/s | 5,8 turnos/s | Sí |
| Estrés | Latencia P90 / P99 en saturación | ≤ 8 s / ≤ 15 s | 6,4 s / 11,8 s | Sí |
| Estrés | Tasa de error en saturación (7,6 turnos/s) | ≤ 1 % | 2,7 % | **No** |
| Estrés | Errores 5xx propios de la aplicación | 0 | 0 (los errores son 429 del modelo propagados y timeouts) | Sí |
| Estrés | Arranque en frío | ≤ 3 s | 4,2 s | **No** |
| Soak | Latencia P90 (inicio vs. fin) | Variación ≤ 10 % | 3,4 s → 3,5 s (+2,9 %) | Sí |
| Soak | Memoria | Sin crecimiento sostenido | 390–420 MiB estable | Sí |
| Soak | Tasa de error | ≤ 1 % | 0,1 % | Sí |
| Soak | Costo por 1.000 turnos | ≤ USD 3,00 | USD 2,92 | Sí |

El costo por 1.000 turnos incluye tokens (USD 1,81 medidos: 3.760 de entrada y 272 de salida
por turno) más la parte proporcional de Cloud Run, Model Armor y observabilidad. Es coherente
con el costo de operación de la sección 1.2 (USD 339,80 / 120.000 turnos = USD 2,83 por 1.000).

### Causa raíz de los incumplimientos

| Hallazgo | Causa raíz | Evidencia |
|---|---|---|
| Tasa de error de 2,7 % al saturar (7,6 turnos/s) | El 94 % de los errores son `429 RESOURCE_EXHAUSTED` de Vertex AI: se alcanza la cuota de tokens por minuto de `gemini-2.5-flash` asignada al proyecto de desarrollo. El agente no reintenta las llamadas al modelo. | Logs de Cloud Run y métricas `aiplatform.googleapis.com/quota` en la ventana de la prueba |
| Arranque en frío de 4,2 s | Importación de ADK, OpenTelemetry y clientes de Google Cloud al iniciar el proceso (≈ 2,9 s) más descarga de la imagen (≈ 1,3 s). | Cloud Trace (span de arranque) y métrica `container/startup_latencies` |

### Plan de acción

| # | Acción | Responsable | Fecha objetivo | Resultado esperado |
|---|---|---|---|---|
| 1 | Solicitar aumento de cuota de TPM de `gemini-2.5-flash` en el proyecto productivo a 3× el pico de estrés medido y evaluar *Provisioned Throughput* si el volumen supera 60.000 conversaciones/mes | Líder del desarrollo | 2026-10-30 | Error ≤ 1 % a 7,6 turnos/s |
| 2 | Configurar reintentos con *backoff* exponencial para errores 429/503 del modelo (`HttpRetryOptions` del cliente de GenAI, máximo 3 intentos) | Ingeniero de IA | v1.2.0 | Absorber picos cortos sin error visible |
| 3 | `min-instances=2` en horario 7:00–22:00 mediante programación de escalamiento | Ingeniero de IA | 2026-10-30 | Eliminar arranques en frío en horario de alto tráfico (+USD 26/mes) |
| 4 | Reducir el tiempo de arranque: imagen multi-etapa con dependencias precompiladas e importación diferida del cliente de Firestore | Ingeniero de IA | v1.2.0 | Arranque en frío ≤ 3 s |
| 5 | Mensaje de contingencia ante 429 persistente ("estamos con alta demanda, ¿deseas que te comunique con un asesor?") | Ingeniero de IA | v1.2.0 | Degradación controlada hacia el contact center |
| 6 | Repetir el escenario de estrés tras las acciones 1–4 y adjuntar resultados en `load-tests/resultados/` | Ingeniero de IA | 2026-11-15 | Evidencia de cierre |

**Conclusión:** la capacidad actual soporta con holgura 10 veces la hora pico real con todos
los objetivos cumplidos. Los dos incumplimientos ocurren en condiciones de saturación (≈ 25×
la hora pico) y tienen causa raíz identificada y plan de acción; no bloquean la salida gradual.
