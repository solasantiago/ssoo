# Sistemas Operativos: guía de estudio

El libro de la materia, en el orden de la cursada 2026. SO no tiene TPs de ejercicios (el TP es un desarrollo grupal), así que hay un capítulo por tema de clase, cada uno en su archivo. Cada bloque es un tipo de ejercicio o de pregunta que toman, con teoría mínima, un ejemplo real resuelto, un ejercicio guiado, práctica y un cierre para memorizar y autoevaluarte. Las respuestas están al final de cada capítulo. Para imprimir: `python3 guia-pdf.py` genera en `guias/pdf/` un PDF por capítulo y el índice (`SO-indice.pdf`).

## Índice

Las estrellas dicen cuánto aparece cada bloque en los parciales reales relevados. Para el 1er parcial hay **4 parciales con fecha**, pero de cada uno se conoce solo el ejercicio de planificación (ejercicio 1): el de 1C 2017 y los recuperatorios de 1C 2022, 2C 2022 y 1C 2023, todos en la práctica adicional de la cátedra. Por eso las estrellas del capítulo 1 dicen qué tipo de ejercicio de planificación toman; la teoría (1.1) va estimada. 📌 va a marcar lo que se tome en los parciales de esta cursada.

| Capítulo | Bloque | Frecuencia | Estado |
|---|---|:-:|---|
| [1. Procesos, hilos y planificación](cap-01-planificacion.md) (clases 1 y 2) | 1.1 Procesos, hilos y cambio de contexto | ★★★☆☆ (estimado) | listo |
| | 1.2 Diagrama de Gantt: algoritmos de corto plazo | ★★★★☆ (3 de 4) | listo |
| | 1.3 Colas multinivel | ☆☆☆☆☆ (0 de 4) | listo |
| | 1.4 Planificación con hilos: ULT, KLT y jacketing | ★★☆☆☆ (1 de 4) | listo |
| 2. Sincronización (clase 3) | | | pendiente |
| 3. Deadlock (clase 4) | | | pendiente |
| 4. Memoria (clase 5) | | | pendiente |
| 5. Memoria virtual (clase 6) | | | pendiente |
| 6. File systems: FAT y ext2 (clases 7 y 8) | | | pendiente |

Ojo con 1.4: entre los parciales con fecha apareció una sola vez, pero los cuatro ejercicios de parcial **sin fecha** que dejó la cátedra ("Ejercicios de parcial" y "Práctica avanzada 1er parcial") son de hilos.

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

**Qué esperar** (es una inferencia, no algo que haya dicho la cátedra): un ejercicio de planificación como los de 1.2 o 1.4, más ejercicios de sincronización y deadlock (capítulos 2 y 3), que son los otros temas de la primera mitad. La "Práctica avanzada 1er parcial" de la cátedra tiene dos de planificación con hilos, dos de semáforos y dos que combinan deadlock y sincronización. Cuando se tome el parcial, anotá acá cómo fue y marcá con 📌 lo que entró.

## Ruta del 1er parcial (capítulos 1 a 3)

Por estrellas, porque todavía no hay nada marcado con 📌:

1. 1.2 Gantt con algoritmos de corto plazo ★★★★☆: es el ejercicio 1 de casi todos los parciales conocidos. Empezá por el ejemplo resuelto (RR) y el guiado (HRRN).
2. 1.4 Hilos, ULT, KLT y jacketing ★★☆☆☆: es lo que más aparece en los ejercicios de parcial sin fecha. Va después de 1.2, porque lo usa.
3. 1.1 Procesos y cambio de contexto ★★★☆☆ (estimado): la teoría que piden en los ítems de justificación.
4. 1.3 Colas multinivel ☆☆☆☆☆: solo si sobra tiempo.
5. Capítulos 2 (sincronización) y 3 (deadlock): pendientes.
