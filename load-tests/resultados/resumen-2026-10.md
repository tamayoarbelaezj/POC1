# Resumen de resultados — pruebas de carga (octubre 2026)

- **Versión probada:** v1.1.0 (imagen `agente-polizas:v1.1.0`)
- **Herramienta:** k6 v0.54, ejecutado desde una VM `e2-standard-4` en `us-central1`
- **Script:** [`../script.js`](../script.js)
- **Entorno:** Cloud Run (proyecto de desarrollo), `REPOSITORY_BACKEND=firestore` con 2.000
  pólizas y 800 siniestros sintéticos, modelo `gemini-2.5-flash` en Vertex AI, Model Armor activo
- **Configuración del servicio:** 1 vCPU, 1 GiB, concurrencia 40, `min-instances=1`,
  `max-instances=10`, CPU boost, timeout 60 s
- **Unidad de medida:** turno = una llamada a `POST /run` (una conversación = 4 turnos)

## Resultados por escenario

| Escenario | VUs | Duración | Turnos | Throughput (turnos/s) | P50 | P90 | P99 | Tasa de error | Instancias (máx.) | Costo / 1.000 turnos (USD) |
|---|---|---|---|---|---|---|---|---|---|---|
| Nominal | 4 | 15 min | 495 | 0,55 | 2,1 s | 3,4 s | 5,9 s | 0,0 % | 1 | 2,86 |
| Pico | 16 | 20 min | 2.700 | 2,25 | 2,3 s | 3,8 s | 6,8 s | 0,3 % | 2 | 2,41 |
| Estrés | 0 → 60 | 25 min | 7.410 | 7,6 (máx. sostenido) | 3,1 s | 6,4 s | 11,8 s | 2,7 % | 4 | 2,47 |
| Resistencia (soak) | 8 | 2 h | 8.064 | 1,12 | 2,1 s | 3,5 s | 6,1 s | 0,1 % | 1 | 2,92 |

## Observaciones

1. **Punto de quiebre:** la tasa de error supera 1 % a partir de **5,8 turnos/s** (≈ 25 veces
   la hora pico real). El 94 % de los errores del escenario de estrés son `429 RESOURCE_EXHAUSTED`
   de Vertex AI (cuota de tokens por minuto del proyecto de desarrollo); el 6 % restante son
   timeouts durante arranques en frío.
2. **Arranque en frío:** las nuevas instancias tardaron en promedio 4,2 s en atender la primera
   solicitud (importación de ADK y cliente de Vertex AI).
3. **Firestore:** latencia P99 de lectura de 38 ms en todos los escenarios; no es cuello de botella.
4. **Memoria:** estable en 390–420 MiB durante las 2 horas de soak; sin fugas.
5. **CPU:** máximo 62 % por instancia en estrés; la carga está dominada por la espera de E/S
   hacia el modelo.
6. **Costo:** el costo por 1.000 turnos baja en pico porque la instancia mínima se amortiza en
   más solicitudes; en soak sube levemente por la menor utilización.
7. **Tokens medidos:** 3.760 de entrada y 272 de salida por turno en promedio, consistente con
   el supuesto del caso de negocio (15.000 / 1.100 por conversación de 4 turnos).

## Estado

Escenarios nominal, pico y soak: **aprobados**. Escenario de estrés: **aprobado con
observaciones** (ver plan de acción en [docs/04-pruebas-carga.md](../../docs/04-pruebas-carga.md)).
