# Estado de la guía

## Dónde retomar

- **Armado del libro:** el capítulo 1 (procesos, hilos y planificación) está completo (29/09/2026). Faltan el 2 (sincronización) y el 3 (deadlock), que también entran en el 1er parcial, y después del 4 al 6 para el 2do. Los capítulos siguen el calendario de clases 2026, un capítulo por tema de clase (SO no tiene TPs de ejercicios).
- **Fecha urgente:** según el calendario de la cátedra (tentativo), el **1er parcial es el sábado 03/10/2026**. Hay que confirmarla con el estudiante.
- **Fuentes que faltan:** parciales completos con fecha (del campus, "Parciales y Finales resueltos"): de los que hay solo se conoce el ejercicio 1 de planificación. El simulacro de parcial 2026 (clase del 26/09). El programa analítico en PDF para `programa/`.
- **Convenciones de la cátedra** para los Gantt (salen de decodificar las planillas resueltas): un solo dispositivo de E/S con cola FIFO; al mismo instante entran a listos primero el fin de quantum, después el fin de E/S y después el nuevo; empates por FIFO. Sin jacketing, la biblioteca replanifica al volver de la E/S si la E/S pasa por ella ("por biblioteca"), y no si la maneja el SO.
- **Material propio** (no de la cátedra): el ejemplo y el guiado de 1.1, las autoevaluaciones, y las respuestas de 2C 2022 c, 1C 2022 Recu b y c, y del Ej 2 de "Ejercicios de parcial" (KA, KB, KC). Todos los Gantt de la cátedra se verificaron contra sus resoluciones.
- **Lumen:** fechas de parciales y recuperatorios cargadas desde el calendario (tentativas) y régimen de promoción desde la presentación. Falta la nota mínima para regularizar. Todavía no hay sesiones de estudio registradas.
- **Formato:** color, LaTeX en las fórmulas (en el chat, texto plano), números de página del lado de afuera, cada capítulo y cada bloque en hoja nueva. Gantt en bloques de código, dos caracteres por unidad: █ CPU, ░ E/S, · listo, - esperando el dispositivo, n esperando admisión. Los PDF se generan con `guia-pdf.py` en `guias/pdf/`, fuera de git.

## Avance por bloque

| Bloque | Conceptos | Ejemplo | Guiado | Práctica | Autoevaluación |
|---|:-:|:-:|:-:|:-:|:-:|

## Pedidos del estudiante

- Mantener todo liviano: pocas reglas, pocos archivos.
- No planificar horarios de estudio salvo que lo pida.
- La voz valida lo que entendió; las autoevaluaciones las hace en el chat (Claude Code o claude.ai).
- Los archivos generados (PDF) van dentro del repo; no borrar nada fuera del repo.
