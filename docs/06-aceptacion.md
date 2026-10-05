# 6. Aceptación

## 6.1 Visto bueno del propietario de negocio

| Campo | Valor |
|---|---|
| Nombre | María Fernanda Cárdenas Ruiz |
| Cargo | Gerente — Experiencia del Cliente, VP Servicio al Cliente |
| Fecha | 2026-10-05 |
| Decisión | **Aprobado** para salida gradual a clientes (10 % → 50 % → 100 % del tráfico web y app), con las condiciones registradas en el acta |
| Evidencia | [anexos/acta-aprobacion.md](anexos/acta-aprobacion.md) |

## 6.2 Validación técnica independiente

**Aplicabilidad:** la validación técnica independiente (equipo de validación de modelos) es
obligatoria para modelos analíticos de ML entrenados por la compañía que soportan decisiones
de riesgo, suscripción o precio. **No aplica obligatoriamente** a esta iniciativa porque:

- no se entrena ni ajusta ningún modelo con datos de la compañía (se usa un modelo fundacional
  de Vertex AI);
- el agente no toma decisiones sobre el cliente; solo consulta y explica información existente;
- la criticidad de la iniciativa es MEDIA (ver [00-ficha-iniciativa.md](00-ficha-iniciativa.md)).

En su lugar se realizó una **revisión técnica de pares** dentro del AI Lab, con participación
de Seguridad de la Información para los controles de privacidad y guardrails.

| Campo | Valor |
|---|---|
| Tipo de revisión | Revisión técnica de pares (código, arquitectura, evaluación, seguridad) |
| Revisor | Santiago Ríos Herrera — Ingeniero de IA, AI Lab (no participó en el desarrollo) |
| Participación adicional | Seguridad de la Información (revisión de guardrails, IAM y Model Armor) |
| Fecha | 2026-10-05 |
| Versión revisada | [v1.1.0](https://github.com/tamayoarbelaezj/POC1/releases/tag/v1.1.0) |
| Resultado | **Aprobado con observaciones** (3 observaciones menores, ninguna bloqueante) |
| Evidencia | [anexos/revision-tecnica.md](anexos/revision-tecnica.md) |
