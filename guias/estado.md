# Estado de la guía

## Dónde retomar

- **Estudio:** retomar en `cap-01-planificacion.md`, bloque 1.1, desde **"Estructura del kernel"** (después de syscalls); siguen cambio de contexto, el ejemplo, el guiado y la práctica. Primera sesión (voz, 30/09/2026): conceptos hasta syscalls, todo a nivel 1. Lo que más costó: PCB vs. imagen del proceso y el ciclo de estados (nuevo al principio, bloqueado → listo).
- **Armado del libro:** los 6 capítulos del calendario de clases están completos (30/09/2026): 1 planificación, 2 sincronización, 3 deadlock, 4 memoria, 5 memoria virtual y 6 file systems. Un capítulo por tema de clase (SO no tiene TPs de ejercicios). Los PDF de los 6 capítulos y del índice están generados (30/09/2026) y revisados con pdftotext y pdftoppm.
- **A confirmar:** E/S (u6), seguridad (u8) y virtualización (u9) no están en el calendario ni hay material de la cátedra: no tienen capítulo hasta que el estudiante confirme si se toman. El buddy system (u5) tampoco se dio.
- **Fecha urgente:** según el calendario de la cátedra (tentativo), el **1er parcial es el sábado 03/10/2026**. Hay que confirmarla con el estudiante.
- **Fuentes que faltan:** parciales completos con fecha (del campus, "Parciales y Finales resueltos"): de los que hay solo se conoce el ejercicio 1 de planificación. El simulacro de parcial 2026 (clase del 26/09). El programa analítico en PDF para `programa/`.
- **Convenciones de la cátedra** para los Gantt (salen de decodificar las planillas resueltas): un solo dispositivo de E/S con cola FIFO; al mismo instante entran a listos primero el fin de quantum, después el fin de E/S y después el nuevo; empates por FIFO. Sin jacketing, la biblioteca replanifica al volver de la E/S si la E/S pasa por ella ("por biblioteca"), y no si la maneja el SO.
- **Material propio** (no de la cátedra): el ejemplo y el guiado de 1.1, 2.1 y 4.1, el bloque 3.3 entero (banquero), el guiado de 6.1, las autoevaluaciones, y las respuestas marcadas "(resolución propia)" (2C 2022 c, 1C 2022 Recu b y c, KA/KB/KC, "¿Es o no es?", "Deadlock Empire", "Puzzle de mutex", la traza A/B/C de memoria y el ejercicio de final de segmentación paginada). Los Gantt y las tablas de reemplazo de páginas de la cátedra se verificaron con simuladores contra sus resoluciones.
- **Diferencias con la cátedra:** en 6.2 (FAT32), la guía toma el tamaño máximo de archivo igual al del FS, pero la diapositiva de FAT dice que el campo de tamaño de la entrada de directorio lo limita a 4 GiB; quedó aclarado en la respuesta.
- **Lumen:** fechas de parciales y recuperatorios cargadas desde el calendario (tentativas) y régimen de promoción desde la presentación. Falta la nota mínima para regularizar. Primera sesión registrada el 30/09/2026.
- **Formato:** color, LaTeX en las fórmulas (en el chat, texto plano), números de página del lado de afuera, cada capítulo y cada bloque en hoja nueva. Gantt en bloques de código, dos caracteres por unidad: █ CPU, ░ E/S, · listo, - esperando el dispositivo, n esperando admisión. Los PDF se generan con `guia-pdf.py` en `guias/pdf/`, fuera de git.

## Avance por bloque

| Bloque | Conceptos | Ejemplo | Guiado | Práctica | Autoevaluación |
|---|:-:|:-:|:-:|:-:|:-:|
| 1.1 | hasta syscalls (voz, 30/09) | — | — | — | — |

## Pedidos del estudiante

- Mantener todo liviano: pocas reglas, pocos archivos.
- No planificar horarios de estudio salvo que lo pida.
- La voz valida lo que entendió; las autoevaluaciones las hace en el chat (Claude Code o claude.ai).
- En la voz funciona: una pregunta de control corta después de cada concepto y un repaso en bloque cada 5 o 6 conceptos. Si contesta a medias, dar una pista más antes de resolver, no la respuesta completa de una.
- Los archivos generados (PDF) van dentro del repo; no borrar nada fuera del repo.
