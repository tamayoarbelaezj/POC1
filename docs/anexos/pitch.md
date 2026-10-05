# Pitch — Asistente de Consulta de Pólizas

Presentado al Comité de Experiencia del Cliente y AI Lab. Resumen de la propuesta.

## 1. El problema

- 45.000 contactos informativos al mes llegan al call center para preguntar por el estado de
  una póliza, sus coberturas o cómo va un siniestro.
- El cliente espera en promedio **4 min 10 s** y cada contacto ocupa **7,5 min** de un asesor.
- Fuera del horario L–S 7:00–19:00 no hay respuesta.

## 2. La propuesta

Un agente conversacional con IA generativa (Gemini 2.5 Flash sobre Google ADK) que:

1. Consulta la información real de la póliza y el siniestro (nunca la inventa).
2. Explica las coberturas del producto en lenguaje claro, remitiendo al condicionado.
3. Escala al asesor cuando hay inconformidad, errores o trámites transaccionales.
4. Protege los datos personales: enmascara cédulas, correos y teléfonos y no revela
   información de terceros.

## 3. Por qué ahora

- La compañía ya opera sobre Google Cloud (Vertex AI, Firestore, Cloud Run).
- El costo por conversación con Gemini 2.5 Flash es de **USD 0,0073**, frente a COP 6.500
  por contacto atendido por un asesor.
- Es un caso de bajo riesgo (informativo, reversible) para madurar el modelo de gobierno de
  agentes del AI Lab.

## 4. Números clave

| Indicador | Valor |
|---|---|
| Conversaciones objetivo | 30.000 / mes |
| Contención esperada | 60 % (18.000 contactos evitados / mes) |
| Inversión inicial | COP 53,0 M |
| Operación | COP 4,0 M / mes |
| Beneficio año 1 | COP 432,0 M |
| ROI año 1 | 327,7 % |
| Recuperación | ≈ 3,0 meses |

## 5. Plan

| Fase | Duración | Entregable |
|---|---|---|
| Construcción y evaluación | 6 semanas | Agente v1.0.0, evalset, guardrails |
| Piloto controlado con asesores | 4 semanas | Pruebas funcionales, de carga y sesgo (v1.1.0) |
| Salida gradual a clientes | 8 semanas | 10 % → 50 % → 100 % del tráfico web y app |

## 6. Lo que pedimos

- Aprobación del responsable de negocio para el piloto y la salida gradual.
- Curaduría del catálogo de coberturas por parte de Experiencia del Cliente.
- Acceso de lectura a la réplica del core de pólizas en Firestore.
