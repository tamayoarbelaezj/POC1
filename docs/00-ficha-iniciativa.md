# 0. Ficha de la iniciativa

| Campo | Valor |
|---|---|
| **Nombre de la iniciativa** | Asistente de Consulta de Pólizas (agente conversacional de IA generativa) |
| **Código interno / repositorio** | `agente-polizas` — <https://github.com/tamayoarbelaezj/POC1> |
| **Tipo de iniciativa** | Iniciativa de IA generativa (agente basado en LLM con herramientas). No es un modelo analítico de ML entrenado por la compañía. |
| **Fecha de elaboración** | 2026-10-05 |
| **Versión del documento** | 1.1 (corresponde a la versión de software v1.1.0) |
| **Nivel de criticidad** | **MEDIA** |
| **Fecha último despliegue** | 2026-10-05 — v1.1.0, entorno de desarrollo (Cloud Run, `us-central1`) |
| **Estado** | Piloto controlado, aprobado por negocio para salida gradual (ver [06-aceptacion.md](06-aceptacion.md)) |

## Justificación del nivel de criticidad (MEDIA)

| Criterio | Evaluación | Efecto en la criticidad |
|---|---|---|
| Tipo de decisión | Informativa. El agente **no** toma decisiones sobre suscripción, indemnización, precio ni cartera; solo consulta y explica información existente. | Reduce |
| Datos tratados | Datos de pólizas y siniestros asociados a clientes (datos personales según Ley 1581 de 2012). El agente no expone datos del tomador y enmascara PII de entrada y salida. | Aumenta |
| Exposición | Canal directo al cliente final (web, app y WhatsApp de asesores). Un error afecta la experiencia y la reputación. | Aumenta |
| Reversibilidad | Alta. Toda respuesta puede corregirse escalando a un asesor humano; no se ejecutan transacciones. | Reduce |
| Dependencia operativa | El call center sigue disponible como canal alterno; una caída del agente no detiene la operación. | Reduce |
| Riesgo regulatorio | Relevante por protección de datos y por información de coberturas (Superintendencia Financiera, deber de información al consumidor financiero). Mitigado con guardrails y remisión al condicionado. | Aumenta |

**Conclusión:** el impacto de un error es moderado y reversible, pero el canal es de cara
al cliente y trata datos personales, por lo que se clasifica como **MEDIA**. Una ampliación
del alcance a operaciones transaccionales (pagos, cancelaciones, avisos de siniestro)
requerirá reclasificar la iniciativa como ALTA.

## Responsables

| Rol | Nombre | Vicepresidencia | Área | Cargo |
|---|---|---|---|---|
| **Elaborado por** | Juan Tamayo | VP de Tecnología / AI Lab | AI Lab | Ingeniero de IA |
| **Custodio técnico** | Juan Tamayo | VP de Tecnología / AI Lab | AI Lab | Ingeniero de IA |
| **Responsable de negocio** | María Fernanda Cárdenas Ruiz | VP Servicio al Cliente | Experiencia del Cliente | Gerente |

## Control de versiones del documento

| Versión doc. | Fecha | Autor | Cambio |
|---|---|---|---|
| 1.0 | 2026-10-05 | Juan Tamayo | Documentación funcional y técnica de la versión v1.0.0 del agente. |
| 1.1 | 2026-10-05 | Juan Tamayo | Se completan las secciones 1 a 6 del formato, pruebas de carga y acta de aprobación (v1.1.0). |

La trazabilidad de versiones de software está en [CHANGELOG.md](../CHANGELOG.md).
