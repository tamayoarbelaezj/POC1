# Acta de aprobación de negocio

**Iniciativa:** Asistente de Consulta de Pólizas
**Versión presentada:** v1.1.0
**Fecha:** 2026-10-05
**Modalidad:** reunión virtual de cierre de piloto

## Asistentes

| Nombre | Rol en la iniciativa | Área |
|---|---|---|
| María Fernanda Cárdenas Ruiz | Responsable de negocio | Experiencia del Cliente — VP Servicio al Cliente |
| Juan Tamayo | Elaborador y custodio técnico | AI Lab — VP de Tecnología |
| Líder del AI Lab | Líder del desarrollo | AI Lab — VP de Tecnología |
| Representante de Seguridad de la Información | Revisión de controles | Seguridad de la Información |

## Temas revisados

1. Resultados del piloto con asesores (1.200 conversaciones): contención 61,0 %, exactitud
   95,0 %, CSAT 4,3 ([03-modelo.md](../03-modelo.md)).
2. Evaluación comparativa de modelos y selección de `gemini-2.5-flash`.
3. Análisis de sesgo: disparidad de contención en mayores de 60 años y plan de ajuste.
4. Pruebas de carga: objetivos cumplidos hasta 10× la hora pico; plan de acción para saturación
   ([04-pruebas-carga.md](../04-pruebas-carga.md)).
5. Matriz de riesgos y controles ([05-riesgos.md](../05-riesgos.md)).
6. Caso de negocio: inversión COP 53,0 M, ROI año 1 de 327,7 %, recuperación ≈ 3,0 meses
   ([01-negocio.md](../01-negocio.md)).

## Decisión

El responsable de negocio **aprueba** la salida gradual a clientes del Asistente de Consulta de
Pólizas en los canales web y app, con el siguiente cronograma: 10 % del tráfico a partir de la
aprobación de cambios de producción, 50 % a las 4 semanas y 100 % a las 8 semanas, sujeto al
cumplimiento de los KPIs de la sección 3.2.

## Condiciones

1. Mantener visible la opción "Hablar con un asesor" en todos los canales.
2. Desplegar el ajuste de instrucción para mayores de 60 años (v1.2.0) antes de pasar al 100 %.
3. Ejecutar las acciones 1 y 3 del plan de pruebas de carga (cuota y `min-instances=2`) antes
   de pasar al 50 %.
4. Presentar mensualmente al comité de Experiencia del Cliente el informe de KPIs, equidad y
   costos.
5. Cualquier ampliación del alcance a trámites transaccionales requiere nueva aprobación y
   reclasificación de criticidad.

## Firmas

| Nombre | Cargo | Aprobación |
|---|---|---|
| María Fernanda Cárdenas Ruiz | Gerente — Experiencia del Cliente | Aprobado (registro de aprobación en la herramienta de gestión de la demanda, 2026-10-05) |
| Juan Tamayo | Ingeniero de IA — AI Lab | Elaboró |
