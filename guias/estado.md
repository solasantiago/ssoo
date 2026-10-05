# Estado de la guía

## Dónde retomar

- **Estudio:** retomar en `cap-01-planificacion.md`, en este orden:
  1. Responder la pregunta pendiente de hilos: si dos hilos ejecutan la misma función, ¿comparten la variable local x?
  2. Bloque 1.2, guiado HRRN desde la decisión de t=7 (hecho con ayuda: B 0-2, A 2-5, C 5-7, B vuelve de E/S en t=6), en papel o planilla.
  3. Bloque 1.2, ejemplo resuelto de RR y extras, en papel.
  4. Bloque 1.3, guiado hoja «Básico», en papel.
  5. Bloque 1.4 desde el principio (dos niveles de planificación, jacketing).
  Pendientes en papel: fork con código y árbol de procesos (1.1) y prioridades no apropiativo con aging A, B, C, D (material propio, propuesto por la voz).
- **Sesiones de voz registradas** (cierre consolidado del 04/10): del 30/09 al 02/10, 1.1 y 1.2 completos en conceptos y 1.3 en conceptos. Todo quedó en nivel 1, sin ejercicios resueltos sin ayuda. El tramo 2 (30/09, ~22:30 a 00:05) no tenía duración y se cargó con 90 min estimados. Lo que más costó: PCB vs. imagen del proceso, el ciclo de estados, síncrona vs. asíncrona, cambio de contexto vs. de proceso, SPN vs. SRT, la fórmula del RR de HRRN y dónde viven las variables con hilos (detalle en `notas` de cada tema).
- **Para la guía (sugerido por la voz, sin aplicar):** en 1.1, aclarar dónde vive cada cosa con hilos (globales en datos, locales en la pila, malloc en el heap; los registros son el estado de la CPU y van al TCB), los tres niveles de "hilo" (de hardware, KLT y ULT) y que modo kernel no es hilo de kernel. En 1.2, que "ráfaga de duración 2" no es "dos ráfagas". En 1.3, el porqué del feedback. Solo se aplica si el estudiante lo pide.
- **Fuera del repo:** en claude.ai hay un artefacto "Esquemas de SO" (material propio) con el diagrama de proceso e hilos, un ejemplo en C y la tabla de dónde vive cada cosa.
- **Armado del libro:** los 6 capítulos del calendario de clases están completos (30/09/2026): 1 planificación, 2 sincronización, 3 deadlock, 4 memoria, 5 memoria virtual y 6 file systems. Un capítulo por tema de clase (SO no tiene TPs de ejercicios). Los PDF de los 6 capítulos y del índice están generados (30/09/2026) y revisados con pdftotext y pdftoppm.
- **A confirmar:** E/S (u6), seguridad (u8) y virtualización (u9) no están en el calendario ni hay material de la cátedra: no tienen capítulo hasta que el estudiante confirme si se toman. El buddy system (u5) tampoco se dio.
- **1er parcial:** fue el sábado 03/10/2026 a las 10:00; desaprobado con 1. Lo próximo es el 2do parcial (21/11) y el 1er recuperatorio del 1er parcial (01/12, 18:30): para el recuperatorio, falta saber qué tomaron y en qué falló.
- **Fuentes que faltan:** parciales completos con fecha (del campus, "Parciales y Finales resueltos"): de los que hay solo se conoce el ejercicio 1 de planificación. El simulacro de parcial 2026 (clase del 26/09). El programa analítico en PDF para `programa/`.
- **Convenciones de la cátedra** para los Gantt (salen de decodificar las planillas resueltas): un solo dispositivo de E/S con cola FIFO; al mismo instante entran a listos primero el fin de quantum, después el fin de E/S y después el nuevo; empates por FIFO. Sin jacketing, la biblioteca replanifica al volver de la E/S si la E/S pasa por ella ("por biblioteca"), y no si la maneja el SO.
- **Material propio** (no de la cátedra): el ejemplo y el guiado de 1.1, 2.1 y 4.1, el bloque 3.3 entero (banquero), el guiado de 6.1, las autoevaluaciones, y las respuestas marcadas "(resolución propia)" (2C 2022 c, 1C 2022 Recu b y c, KA/KB/KC, "¿Es o no es?", "Deadlock Empire", "Puzzle de mutex", la traza A/B/C de memoria y el ejercicio de final de segmentación paginada). Los Gantt y las tablas de reemplazo de páginas de la cátedra se verificaron con simuladores contra sus resoluciones.
- **Diferencias con la cátedra:** en 6.2 (FAT32), la guía toma el tamaño máximo de archivo igual al del FS, pero la diapositiva de FAT dice que el campo de tamaño de la entrada de directorio lo limita a 4 GiB; quedó aclarado en la respuesta.
- **Lumen:** fechas de parciales y recuperatorios cargadas desde el calendario (tentativas) y régimen de promoción desde la presentación. Falta la nota mínima para regularizar. Primera sesión registrada el 30/09/2026.
- **Formato:** color, LaTeX en las fórmulas (en el chat, texto plano), números de página del lado de afuera, cada capítulo y cada bloque en hoja nueva. Gantt en bloques de código, dos caracteres por unidad: █ CPU, ░ E/S, · listo, - esperando el dispositivo, n esperando admisión. Los PDF se generan con `guia-pdf.py` en `guias/pdf/`, fuera de git.

## Avance por bloque

| Bloque | Conceptos | Ejemplo | Guiado | Práctica | Autoevaluación |
|---|:-:|:-:|:-:|:-:|:-:|
| 1.1 | completos (voz, 30/09) | — | — | — | — |
| 1.2 | completos (voz, 01/10) | — | HRRN hasta t=7, con ayuda | — | — |
| 1.3 | completos (voz, 01/10) | — | — | — | — |

## Pedidos del estudiante

- Mantener todo liviano: pocas reglas, pocos archivos.
- No planificar horarios de estudio salvo que lo pida.
- La voz valida lo que entendió; las autoevaluaciones las hace en el chat (Claude Code o claude.ai).
- En la voz funciona: una pregunta de control corta después de cada concepto y un repaso en bloque cada 5 o 6 conceptos. Si contesta a medias, dar una pista más antes de resolver, no la respuesta completa de una. Pedir el porqué además de la regla. Si un concepto no cierra, un diagrama (destrabó hilos), en un artefacto aparte.
- En la voz no funciona: Gantt, fork con código ni ejercicios con 3 o más procesos, aunque tenga la hoja impresa; van a papel o planilla. No interrumpirlo a mitad de la respuesta ni contestar en texto durante una sesión de voz.
- Los archivos generados (PDF) van dentro del repo; no borrar nada fuera del repo.
