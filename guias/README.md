# Sistemas Operativos: guía de estudio

El libro de la materia, en el orden de la cursada 2026. SO no tiene TPs de ejercicios (el TP es un desarrollo grupal), así que hay un capítulo por tema de clase, cada uno en su archivo. Cada bloque es un tipo de ejercicio o de pregunta que toman, con teoría mínima, un ejemplo real resuelto, un ejercicio guiado, práctica y un cierre para memorizar y autoevaluarte. Las respuestas están al final de cada capítulo. Para imprimir: `python3 guia-pdf.py` genera en `guias/pdf/` un PDF por capítulo y el índice (`SO-indice.pdf`).

**PDF para imprimir** (generados el 30/09/2026, en `guias/pdf/`, fuera de git): `SO-cap01.pdf` (30 páginas), `SO-cap02.pdf` (14), `SO-cap03.pdf` (16), `SO-cap04.pdf` (14), `SO-cap05.pdf` (15), `SO-cap06.pdf` (13) y este índice, `SO-indice.pdf`. Si cambia un capítulo, se regenera con `python3 guia-pdf.py N`.

## Índice

Las estrellas dicen cuánto aparece cada bloque en los parciales reales relevados. Para el 1er parcial hay **4 parciales con fecha**, pero de cada uno se conoce solo el ejercicio de planificación (ejercicio 1): el de 1C 2017 y los recuperatorios de 1C 2022, 2C 2022 y 1C 2023, todos en la práctica adicional de la cátedra. Por eso las estrellas del capítulo 1 dicen qué tipo de ejercicio de planificación toman. Para el resto no hay parciales con fecha: las estrellas marcadas "(estimado)" salen de los "Ejercicios de parcial" de cada tema (sin fecha), de la "Práctica avanzada 1er parcial" y del final del 20/02/2024. 📌 va a marcar lo que se tome en los parciales de esta cursada.

| Capítulo | Bloque | Frecuencia | Estado |
|---|---|:-:|---|
| [1. Procesos, hilos y planificación](cap-01-planificacion.md) (clases 1 y 2) | 1.1 Procesos, hilos y cambio de contexto | ★★★☆☆ (estimado) | listo |
| | 1.2 Diagrama de Gantt: algoritmos de corto plazo | ★★★★☆ (3 de 4) | listo |
| | 1.3 Colas multinivel | ☆☆☆☆☆ (0 de 4) | listo |
| | 1.4 Planificación con hilos: ULT, KLT y jacketing | ★★☆☆☆ (1 de 4) | listo |
| [2. Sincronización](cap-02-sincronizacion.md) (clase 3) | 2.1 Condición de carrera y sección crítica | ★★★☆☆ (estimado) | listo |
| | 2.2 Sincronizar con semáforos | ★★★★★ (estimado) | listo |
| [3. Deadlock](cap-03-deadlock.md) (clase 4) | 3.1 Condiciones y estrategias | ★★★☆☆ (estimado) | listo |
| | 3.2 Deadlock en código con semáforos | ★★★★☆ (estimado) | listo |
| | 3.3 Algoritmo del banquero y detección | ★☆☆☆☆ (estimado) | listo |
| [4. Memoria](cap-04-memoria.md) (clase 5) | 4.1 Asignación contigua y particiones | ★★☆☆☆ (estimado) | listo |
| | 4.2 Paginación | ★★★★☆ (estimado) | listo |
| | 4.3 Segmentación y segmentación paginada | ★★★★☆ (estimado) | listo |
| [5. Memoria virtual](cap-05-memoria-virtual.md) (clase 6) | 5.1 Paginación bajo demanda y fallos de página | ★★★★☆ (estimado) | listo |
| | 5.2 Algoritmos de sustitución de páginas | ★★★★★ (estimado) | listo |
| | 5.3 Thrashing y conjunto de trabajo | ★★★☆☆ (estimado) | listo |
| [6. File systems](cap-06-file-systems.md) (clases 7 y 8) | 6.1 Archivos, directorios, permisos y links | ★★★☆☆ (estimado) | listo |
| | 6.2 Asignación de bloques y FAT | ★★★★☆ (estimado) | listo |
| | 6.3 ext2: inodos y punteros | ★★★★☆ (estimado) | listo |

**A confirmar:** el programa tiene tres unidades que no figuran en el calendario de clases 2026 y de las que no hay material de la cátedra: **entrada/salida** (u6: E/S programada, interrupciones y DMA, buffering, planificación de disco, RAID), **protección y seguridad** (u8) y **virtualización** (u9). No tienen capítulo hasta que se confirme si se toman. Tampoco se dio el buddy system (u5).

Ojo con 1.4: entre los parciales con fecha apareció una sola vez, pero los cuatro ejercicios de parcial **sin fecha** que dejó la cátedra ("Ejercicios de parcial" y "Práctica avanzada 1er parcial") son de hilos. En 3.3 (banquero) no hay ejercicios de la cátedra: está en la teoría de la clase y los ejemplos son material propio.

## Cursada 2026

Según la presentación de la materia y el calendario de clases de la cátedra (las fechas son **tentativas**, lo aclara el calendario):

- **Clases:** sábados de 8:30 a 13, presenciales en Campus. La práctica se ve junto con la teoría. No se toma asistencia.
- **Orden de los temas:** introducción y fundamentos; procesos y planificación; hilos y planificación; sincronización; deadlock; práctica avanzada; simulacro de parcial; **1er parcial**; memoria; memoria virtual; file systems; FAT y ext2; práctica avanzada; simulacro; **2do parcial**.
- **Parciales:** dos, presenciales en Campus, unificados por turno. **1er parcial: sábado 03/10.** 2do parcial: sábado 21/11.
- **Recuperatorios** (martes, 18:30, en Campus): 1er recuperatorio del 1er parcial el 01/12 y del 2do parcial el 15/12; 2do recuperatorio del 1er parcial el 16/02/2027 y del 2do parcial el 23/02/2027. Complementos: 22/12.
- **TP:** grupal (5 integrantes), con checkpoints durante el cuatrimestre y entrega en 1ra fecha el 28/11, 2da el 12/12 o 3ra el 19/12. Se aprueba con pruebas en el laboratorio y un coloquio individual.
- **Aprobación:** dos parciales, TP grupal y final (con ejercicios integradores, como los parciales). **Promoción:** 8 o más en cada parcial y el TP aprobado en 1ra o 2da fecha, con un coloquio de promoción. Se puede recuperar uno de los parciales para subir la nota (la del recuperatorio es la que queda). La presentación menciona un "complemento" para quien queda con 8 y 7, sin más detalle.

## Modalidad 2026

Todavía no hubo parciales en esta cursada. De los parciales viejos se conoce solo el ejercicio 1, que siempre fue de planificación: armar el Gantt con un algoritmo (SJF con estimación, RR, HRRN con grado de multiprogramación, o KLTs y ULTs) y responder dos ítems más, como calcular una métrica, decir qué algoritmo lo mejoraría o qué cambiaría con otro parámetro, justificando "sin volver a hacer el Gantt".

El único examen completo que hay es el final del 20/02/2024: **5 verdaderos o falsos con justificación** (deadlock, condición de carrera, E/S con hilos, TLB y fallos de página, compactación en disco) y **2 ejercicios** (encontrar errores en una sincronización con semáforos, y TLB y thrashing con LRU), en 90 minutos. La presentación dice que el final tiene un "esquema similar a los parciales, con ejercicios integradores".

**Qué esperar** (es una inferencia, no algo que haya dicho la cátedra):
- **1er parcial:** teoría en verdadero o falso justificado, más un ejercicio de planificación como los de 1.2 o 1.4 y ejercicios de sincronización (2.2) y deadlock (3.2). La "Práctica avanzada 1er parcial" tiene dos de planificación con hilos, dos de semáforos y dos que combinan deadlock y sincronización.
- **2do parcial:** teoría en verdadero o falso, más ejercicios de memoria (traducción de direcciones, sustitución de páginas, thrashing) y de file systems (FAT y ext2).

Cuando se tome cada parcial, anotá acá cómo fue y marcá con 📌 lo que entró.

## Ruta del 1er parcial (capítulos 1 a 3)

Por estrellas, porque todavía no hay nada marcado con 📌:

1. 1.2 Gantt con algoritmos de corto plazo ★★★★☆: es el ejercicio 1 de casi todos los parciales conocidos. Empezá por el ejemplo resuelto (RR) y el guiado (HRRN).
2. 1.4 Hilos, ULT, KLT y jacketing ★★☆☆☆: es lo que más aparece en los ejercicios de parcial sin fecha. Va después de 1.2, porque lo usa.
3. 2.2 Sincronizar con semáforos ★★★★★ (estimado): el ejercicio de sincronización. Antes, los conceptos de 2.1.
4. 3.2 Deadlock en código con semáforos ★★★★☆ (estimado): Gantt con semáforos y grafo. Usa 1.2 y 2.2.
5. 1.1 Procesos y cambio de contexto, 2.1 Sección crítica y 3.1 Condiciones y estrategias ★★★☆☆ (estimado): la teoría para los verdaderos o falsos.
6. 1.3 Colas multinivel ☆☆☆☆☆ y 3.3 Banquero ★☆☆☆☆: solo si sobra tiempo.

## Ruta del 2do parcial (capítulos 4 a 6)

Por estrellas, porque todavía no hay nada marcado con 📌:

1. 4.2 Paginación ★★★★☆ (estimado): la traducción de direcciones, que usan todos los ejercicios de memoria.
2. 5.2 Algoritmos de sustitución ★★★★★ (estimado): el ejercicio más frecuente de memoria virtual. Va después de 5.1.
3. 5.1 Paginación bajo demanda ★★★★☆ (estimado): fallos de página, TLB y conteo de accesos.
4. 6.2 FAT y 6.3 ext2 ★★★★☆ (estimado): las cuentas de tamaños y accesos.
5. 4.3 Segmentación ★★★★☆ (estimado).
6. 5.3 Thrashing ★★★☆☆ y 6.1 Archivos y links ★★★☆☆ (estimado): teoría para los verdaderos o falsos.
7. 4.1 Particiones ★★☆☆☆ (estimado).
