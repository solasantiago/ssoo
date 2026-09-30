# Capítulo 1: Procesos, hilos y planificación (clases 1 y 2)

## 1.1 Procesos, hilos y cambio de contexto ★★★☆☆ (estimado)

Temas en Lumen: `u2-proceso-vs-programa`, `u2-bloque-control-proceso-pcb`, `u2-estados-transiciones-proceso`, `u2-operaciones-control-procesos`, `u2-contexto-cambio-contexto-cambio`, `u3-niveles-planificacion-largo-mediano`, `u1-soporte-hardware-interrupciones-modos`, `u1-llamadas-sistema-syscalls`, `u1-arquitecturas-kernel`

Es la teoría que usan todos los ejercicios de planificación. No hay preguntas de teoría relevadas de parciales reales (de los parciales con fecha solo se conoce el ejercicio de planificación), así que las estrellas son una estimación. En los parciales conocidos la teoría aparece como ítems chicos dentro del ejercicio: "¿qué cambiaría si fuesen KLTs?", "¿qué desventajas tiene el algoritmo?".

### 1. Conceptos

**Programa y proceso.** El programa es el archivo ejecutable en disco: es pasivo. El proceso es un programa en ejecución: es activo, y además del código tiene datos, pila, registros y recursos asignados. Un mismo programa abierto dos veces son dos procesos distintos.

**Imagen del proceso.** Es lo que el proceso tiene en memoria:

```
 MAX  ┌──────────────┐
      │    STACK     │  llamadas a funciones: parámetros, variables locales, retorno
      │      ↓       │
      │      ↑       │
      │     HEAP     │  memoria dinámica (malloc)
      ├──────────────┤
      │    DATOS     │  variables globales y constantes
      ├──────────────┤
      │    CÓDIGO    │  instrucciones
   0  └──────────────┘
      + PCB (lo guarda el SO, siempre en RAM)
```

**PCB (Process Control Block).** Es la estructura con la que el SO administra al proceso. Tiene el PID, el estado, el program counter, los registros de la CPU, la información de planificación (prioridad, ráfagas estimadas), la de memoria, la contable, la de E/S (archivos abiertos, dispositivos) y punteros (por ejemplo, al padre). Ojo: el PCB está **siempre en RAM**, aunque el proceso esté suspendido en disco, porque el SO lo necesita para saber qué hacer con él.

**Estados.** El modelo de cinco estados, más los dos suspendidos:

```
             admitir            despachar
   NUEVO ─────────────→ LISTO ─────────────→ EJECUTANDO ──→ FINALIZADO
                          ↑  ←──────────────      │
                          │   fin de quantum      │ pide E/S o
                          │   o desalojo          │ espera un evento
                          │                       ↓
                          └──────────────────  BLOQUEADO
                            ocurre el evento

   Suspendidos (en disco, swap): LISTO ⇄ SUSPENDIDO LISTO,  BLOQUEADO ⇄ SUSPENDIDO BLOQUEADO
```

**Planificadores.** Cada uno mueve procesos entre estados distintos:
- **Largo plazo:** admite procesos (nuevo → listo) y los saca al terminar. Controla el **grado de multiprogramación**: cuántos procesos hay en memoria a la vez. Si el grado es 3 y ya hay 3, el cuarto espera en nuevo.
- **Mediano plazo:** suspende y reanuda (swap out y swap in). Sirve para bajar el grado de multiprogramación o para lograr una buena mezcla de procesos CPU bound e I/O bound.
- **Corto plazo:** elige qué proceso listo pasa a ejecutar. Es el más frecuente, y es el de los diagramas de Gantt (bloque 1.2).

**Modos de ejecución.** La CPU tiene un **modo kernel** (puede ejecutar instrucciones privilegiadas) y un **modo usuario** (no puede). El modo está en un bit del PSW. De usuario a kernel se pasa **solo** por una interrupción o una syscall; de kernel a usuario, con una instrucción privilegiada o restaurando el contexto. Así un programa no puede tocar el hardware sin pasar por el SO.

**Interrupciones.** Son avisos que cortan el ciclo de instrucción para atender algo. Pueden ser asíncronas (de hardware: fin de E/S, timer) o síncronas (excepciones: división por cero, fallo de página). Algunas se pueden enmascarar (deshabilitar) y otras no. Al atender una, la CPU pasa a modo kernel y ejecuta el manejador.

**Syscalls.** Son la forma en que un proceso le pide un servicio al SO (leer un archivo, crear un proceso). Los programas no las llaman directo: usan las funciones de biblioteca (por ejemplo, la libc), que son **wrappers** de las syscalls y dan portabilidad.

**Estructura del kernel.** En el **monolítico** todo el SO corre en modo kernel, en un solo programa: es rápido, pero un error en un driver tira abajo todo (Linux). En el **microkernel** el núcleo solo tiene lo mínimo (planificación, IPC, memoria básica) y el resto (file systems, drivers) corre como procesos en modo usuario: es más robusto, pero más lento por los mensajes. El **híbrido** mezcla los dos (Windows NT).

**Cambio de contexto.** Es guardar el contexto de lo que se está ejecutando (registros, PC, PSW) para después poder reanudarlo. Pasa para ejecutar otro proceso, para atender una interrupción o para ejecutar una syscall. Es **overhead**: tiempo en que el sistema no hace trabajo útil para el usuario. Tres palabras que se confunden:
- **Cambio de modo:** usuario ⇄ kernel.
- **Cambio de contexto:** guardar un contexto y cargar otro.
- **Cambio de proceso:** el proceso que ocupa la CPU pasa a ser otro.

Las relaciones que toman en verdadero o falso:

```
1 cambio de proceso  ⇒  al menos 2 cambios de contexto (guardar el de P1 y restaurar el de P2)
1 cambio de modo     ⇒  1 cambio de contexto (del proceso de usuario al SO, o al revés)
1 cambio de contexto ⇏  1 cambio de proceso (se puede volver al mismo, tras una syscall o una interrupción)
1 cambio de contexto ⇏  1 cambio de modo   (una interrupción mientras ya se atiende otra: sigue en kernel)
```

**Creación de procesos: fork().** Un proceso padre crea un hijo con la syscall `fork()`. El hijo es una **copia** del padre (mismo código, copia de los datos y la pila) y los dos siguen desde la instrucción siguiente al fork. Lo único que cambia es lo que devuelve: **0 en el hijo** y el **PID del hijo en el padre** (−1 si falla). Con `exec()` el hijo reemplaza su imagen por otro programa. El padre puede esperar al hijo con `wait()`. Ojo: cada fork que se ejecuta duplica a todos los procesos que llegan a esa línea; n forks seguidos dan $2^n$ procesos en total.

**Hilos.** Un hilo es la unidad básica de uso de la CPU: tiene su propio PC, registros y pila (en su TCB), y **comparte** con los otros hilos del proceso el código, los datos, el heap y los archivos abiertos. Frente a crear procesos:
- Crear un hilo y cambiar de un hilo a otro es más rápido que hacerlo con procesos.
- Se comunican por la memoria compartida, sin pasar por el SO.
- No hay protección entre ellos: un hilo puede pisar la pila de otro.
- Si el proceso muere, mueren todos sus hilos.

El estado del proceso sale de sus hilos: está ejecutando si algún hilo ejecuta, listo si ninguno ejecuta y alguno está listo, y **bloqueado solo si todos** sus hilos están bloqueados.

**KLT y ULT.** Los **KLT** (hilos de kernel) los conoce y planifica el SO. Los **ULT** (hilos de usuario, "green threads") los maneja una biblioteca en modo usuario, y el SO no sabe que existen: para el SO, el proceso es un solo hilo. El detalle, con jacketing, está en el bloque 1.4.

**Comunicación entre procesos (IPC).** Los procesos cooperativos se comunican por **memoria compartida** (rápida: una vez creada la zona, no interviene el SO) o por **paso de mensajes** (más lento, porque cada mensaje es una syscall, pero sirve para pocos datos y entre máquinas).

**Los tipos de pregunta que toman:**
1. **Verdadero o falso con justificación:** cambios de contexto, modo y proceso; qué hay en el PCB; qué comparten los hilos.
2. **Estados y planificadores:** qué transición hace cada planificador; qué pasa con el grado de multiprogramación.
3. **fork():** cuántos procesos se crean y qué imprime cada uno.
4. **Ítems de teoría dentro de un ejercicio de planificación:** ventajas y desventajas de un algoritmo, o qué cambia con KLT o ULT (bloques 1.2 y 1.4).

### 2. Ejemplo resuelto (material propio, sobre la clase de procesos e hilos)

> Indique si las siguientes afirmaciones son verdaderas o falsas, justificando: a) Todo cambio de contexto implica un cambio de proceso. b) Cuando un proceso se suspende, su PCB se lleva a disco junto con su imagen. c) Un proceso con tres hilos KLT está bloqueado cuando uno de sus hilos pide una E/S.

Es del tipo 1. En un V o F lo que suma es la justificación: sin ella, el ítem no vale. Se justifica con la definición y, si se puede, con un contraejemplo.

```
Paso 1: a) ¿cambio de contexto ⇒ cambio de proceso?
  FALSO. Una syscall o una interrupción provocan un cambio de contexto (se guarda
  el del proceso y se ejecuta el SO), y al terminar se puede volver al mismo
  proceso. Al revés sí vale: un cambio de proceso implica cambios de contexto.

Paso 2: b) ¿el PCB va a disco al suspender?
  FALSO. Al suspender se lleva a swap la imagen del proceso, pero el PCB queda
  siempre en RAM: el SO lo necesita para saber que el proceso existe, en qué estado
  está y dónde está su imagen.

Paso 3: c) ¿un hilo KLT bloqueado bloquea al proceso?
  FALSO. El SO planifica cada KLT por separado: si uno se bloquea, los otros dos
  siguen listos o ejecutando. El proceso está bloqueado solo si sus tres hilos
  están bloqueados. (Con ULT sin jacketing sí se bloquearía todo el proceso).

Control: cada respuesta tiene la definición en juego y un caso concreto ✓
```

### 3. Ejercicio guiado (material propio)

> Dado el siguiente código, indique cuántos procesos hay al final (contando al original) y cuántas veces se imprime "hola".
>
> ```c
> int main() {
>     fork();
>     if (fork() == 0)
>         fork();
>     printf("hola\n");
> }
> ```

Es del tipo 3. Andá línea por línea contando cuántos procesos llegan a cada fork: cada uno que llega se duplica. El `if` deja pasar solo a los hijos de ese fork (a los que les devolvió 0).

```
Paso 1: procesos después del primer fork()
  → ________

Paso 2: procesos después del segundo fork(), y cuántos de ellos son hijos (reciben 0)
  → ________

Paso 3: procesos después del fork() del if (solo lo ejecutan los hijos del paso 2)
  → ________

Paso 4: cuántas veces se imprime "hola"
  → ________

Control: dibujá el árbol de procesos y contá las hojas y los nodos
  → ________
```

### 4. Práctica

Respondé cada una en dos o tres líneas antes de mirar las respuestas.

1. ¿Qué transiciones de estado hace cada planificador (largo, mediano y corto plazo)?
2. Verdadero o falso: "Todo cambio de modo implica un cambio de contexto". Justificá.
3. ¿Qué comparten los hilos de un mismo proceso y qué tiene cada uno propio?
4. ¿Por qué es más rápido cambiar entre hilos del mismo proceso que entre procesos?
5. ¿Cómo pasa la CPU de modo usuario a modo kernel? ¿Y de kernel a usuario?
6. ¿Qué ventaja y qué desventaja tiene un microkernel frente a un kernel monolítico?

### 5. Cierre

**Fórmulas**

$$\text{procesos totales con } n \text{ forks seguidos} = 2^n$$

```
Estados: nuevo → listo ⇄ ejecutando → finalizado;  ejecutando → bloqueado → listo
Largo plazo: nuevo → listo (grado de multiprogramación)   Mediano: suspender/reanudar
Corto plazo: listo → ejecutando
fork(): 0 en el hijo, PID del hijo en el padre, −1 si falla
1 cambio de proceso ⇒ ≥ 2 cambios de contexto;  1 cambio de modo ⇒ 1 cambio de contexto
```

**Trampas**
- **Decir que el PCB va a disco al suspender.** Va la imagen; el PCB queda en RAM.
- **Confundir cambio de contexto con cambio de proceso.** Una syscall es cambio de contexto (y de modo) sin cambio de proceso.
- **Decir que los hilos comparten la pila.** Cada hilo tiene su pila y sus registros; comparten código, datos, heap y archivos.
- **Contar los forks como suma.** Cada fork duplica a todos los que llegan a esa línea: se multiplica.
- **Decir que un hilo bloqueado bloquea al proceso.** Solo si son ULT sin jacketing; con KLT, el proceso se bloquea cuando se bloquean todos.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) Diferenciá cambio de modo, cambio de contexto y cambio de proceso, y da un ejemplo de un cambio de contexto sin cambio de proceso.
2. (Ejercicio) Un programa ejecuta `fork(); fork(); fork();` y después `printf("x")`. ¿Cuántos procesos hay y cuántas "x" se imprimen? ¿Qué devuelve cada fork en el hijo? (material propio)

## 1.2 Diagrama de Gantt: algoritmos de corto plazo ★★★★☆ (3 de 4)

Temas en Lumen: `u3-criterios-planificacion-politica-vs`, `u3-algoritmos-no-apropiativos-fcfs`, `u3-planificacion-prioridades`, `u3-srt-hrrn`, `u3-round-robin-virtual-round`, `u2-procesos-cpu-bound-i`, `u3-planificacion-multiprocesadores-afinidad`

Es el ejercicio 1 de los parciales relevados: el de 1C 2017 (SJF con estimación), el recuperatorio de 2C 2022 (RR con una métrica) y el de 1C 2023 (HRRN con grado de multiprogramación). El cuarto, el recuperatorio de 1C 2022, es de hilos (bloque 1.4), pero se resuelve con este mismo método.

### 1. Conceptos

**Ráfagas.** Un proceso alterna ráfagas de CPU y ráfagas de E/S. El enunciado las da en una tabla: llegada, CPU, E/S, CPU... Un proceso **CPU bound** tiene ráfagas de CPU largas; uno **I/O bound**, ráfagas de CPU cortas y mucha E/S.

**Diagrama de Gantt.** Es una tabla con un renglón por proceso y una columna por unidad de tiempo, donde se marca qué hace cada uno en cada unidad. En esta guía:

```
     0         5         10
     |.........|.........|        cada unidad ocupa dos caracteres
P1   ████░░░░··████               █ CPU    ░ E/S    · listo, esperando la CPU
P2     ··████--░░                 - bloqueado esperando el dispositivo de E/S
                                  n nuevo, esperando que lo admitan (grado de multiprogramación)
```

Ojo: la columna que arranca en 0 es la unidad que va de 0 a 1. Algunos enunciados numeran las columnas desde 1: fijate cómo está el eje antes de leer un instante.

**Con desalojo y sin desalojo.** Un algoritmo **sin desalojo** (no apropiativo) solo elige cuando la CPU queda libre: el proceso termina, se bloquea o la cede. Uno **con desalojo** (apropiativo) además puede sacar al que ejecuta cuando llega uno nuevo, vuelve uno de E/S o vence el quantum.

**Criterios.** Orientados al usuario: tiempo de respuesta, tiempo de espera (en listos), tiempo de retorno (fin − llegada), cumplir deadlines. Orientados al sistema: uso de la CPU, throughput (procesos terminados por unidad de tiempo), equidad, respetar prioridades.

**FIFO (FCFS).** Ejecuta en orden de llegada a listos, sin desalojo. Es simple, pero un proceso largo hace esperar a todos los cortos (efecto convoy) y perjudica a los I/O bound.

**SJF y SRT.** Elige la ráfaga de CPU más corta. **SJF** es sin desalojo. **SRT** (SJF con desalojo) desaloja si llega uno con ráfaga menor que lo que **le resta** al que ejecuta. Minimiza el tiempo de espera promedio, pero puede producir inanición de los largos. Como no se sabe cuánto va a durar la próxima ráfaga, se estima con el promedio ponderado de la anterior:

$$Est_{n+1} = \alpha \cdot R_n + (1 - \alpha) \cdot Est_n \qquad \alpha \in [0, 1]$$

donde $R_n$ es lo que ejecutó de verdad la ráfaga anterior y $Est_n$ lo que se había estimado. Con $\alpha$ cerca de 1 pesa más la última ráfaga real; con $\alpha$ cerca de 0, la estimación anterior. Por ejemplo, con $\alpha = 0{,}5$, $Est_n = 4$ y $R_n = 5$: $Est_{n+1} = 0{,}5 \cdot 5 + 0{,}5 \cdot 4 = 4{,}5$. En SRT con estimación se compara la **estimación restante** del que ejecuta (estimación − lo que ya ejecutó).

**Prioridades.** Ejecuta al de mayor prioridad (en la cátedra, **número más chico = más prioridad**), con o sin desalojo. Puede producir inanición; se corrige con **aging** (envejecimiento): subirle la prioridad al que espera mucho.

**HRRN (Highest Response Ratio Next).** Sin desalojo. Elige al de mayor response ratio:

$$RR = \frac{W + S}{S} = 1 + \frac{W}{S}$$

con W el tiempo que lleva esperando **en listos** (desde que entró a listos por última vez) y S la duración de su próxima ráfaga. Favorece a los cortos, como SJF, pero la espera hace crecer el RR y evita la inanición. Ojo: se calcula en el instante en que hay que elegir, para todos los que están en listos.

**Round Robin (RR).** Cada proceso ejecuta como mucho un **quantum** Q; si no terminó la ráfaga, una interrupción del timer lo desaloja y va al final de la cola. Siempre con desalojo. Con n procesos listos, nadie espera más de $Q \cdot (n - 1)$. Si Q es muy grande, se comporta como FIFO; si es muy chico, el overhead de los cambios de contexto se come la CPU. Perjudica a los I/O bound: usan poco de su quantum, se bloquean y al volver hacen toda la cola.

**VRR (Virtual Round Robin).** Arregla eso con una **cola auxiliar**, más prioritaria que la de listos. El que se bloqueó sin usar todo su quantum, al volver de la E/S va a la auxiliar y ejecuta solo lo que le sobró:

$$Q' = Q - \text{lo que ejecutó antes de bloquearse}$$

Si agota Q', vuelve a la cola común. El que agota el quantum completo va a la cola común, como en RR.

**Multiprocesador.** Con dos o más CPU, cada una toma procesos de la cola de listos. Con **afinidad**, un proceso vuelve a la misma CPU donde ejecutó (aprovecha su caché), aunque otra esté libre; sin afinidad, lo toma la primera CPU libre.

**Convenciones de la cátedra.** Los enunciados suelen aclararlas; si no, estas son las que usan las resoluciones de la guía:
1. **Un solo dispositivo de E/S con cola FIFO.** Si está ocupado, el proceso queda bloqueado esperando (`-`) hasta que se libere.
2. **Si varios entran a listos en el mismo instante**, primero el que vuelve por fin de quantum, después el que vuelve de E/S y al final el nuevo.
3. **Los empates del algoritmo se desempatan por FIFO.** Con desalojo, el que llega desaloja solo si es **estrictamente** mejor.
4. **E/S en paralelo con la CPU:** mientras uno hace E/S, otro puede ejecutar.

**Métricas.** Se leen del Gantt ya hecho:

$$T_{\text{retorno}} = T_{\text{fin}} - T_{\text{llegada}} \qquad NTT = \frac{\sum T_{\text{listo}} + \sum \text{ráfagas de CPU}}{\sum \text{ráfagas de CPU}}$$

El NTT (normalized turnaround time) es la definición del recuperatorio de 2C 2022: cuántas veces más que su CPU tardó cada proceso sin contar la E/S. Cuanto más alto, más perjudicado.

**Los tipos de ejercicio que toman:**
1. **Hacer el Gantt** con un algoritmo dado (a veces con estimación, grado de multiprogramación o VRR), justificando los instantes de decisión.
2. **Calcular una métrica** (espera, retorno, NTT) y decir qué proceso fue el más perjudicado.
3. **Teoría sobre el algoritmo:** desventajas, qué algoritmo lo mejoraría, qué cambia si cambia un parámetro.
4. **Leer un Gantt dado:** qué algoritmo se usó, justificando con dos instantes (se ve en los ejercicios de hilos del bloque 1.4).

### 2. Ejemplo resuelto (recuperatorio 2C 2022, Ej 1)

> Se dispone de un sistema operativo con planificador de corto plazo RR con q = 3, para la siguiente traza de ejecución:
>
> ```
>       Llegada   CPU   E/S   CPU   E/S   CPU
> P1       0       2     5     2     4     1
> P2       1       8     1     5     -     -
> P3       2       8     -     -     -     -
> ```
>
> a) Realice el diagrama de Gantt. b) Calcule la métrica "Normalized turnaround time" (NTT) para cada proceso y en base a dicha métrica mencione cuál proceso fue el más perjudicado y por qué. c) Proponga otro algoritmo de planificación que priorice al proceso afectado en el punto anterior, justifique conceptualmente, sin volver a realizar el gantt o el cálculo de la métrica.

Es del tipo 1 y 2. RR con Q = 3, tiempos en unidades. P1 es I/O bound (ráfagas de 2, 2 y 1); P2 y P3 son CPU bound. Hay un solo dispositivo de E/S. Se avanza evento por evento, anotando la cola de listos.

```
Paso 1: t = 0 a 2
  t=0  llega P1 y ejecuta. t=1 llega P2.
  t=2  P1 termina su ráfaga (2 < Q) y va a E/S hasta t=7. Llega P3.
       Listos: P2, P3 → ejecuta P2.

Paso 2: t = 5, vence el quantum de P2 (ejecutó 3 de 8)
  Listos: P3, P2 → ejecuta P3.

Paso 3: t = 7 y 8
  t=7  P1 vuelve de E/S → listos: P2, P1.
  t=8  vence el quantum de P3 (3 de 8) → listos: P2, P1, P3 → ejecuta P2.

Paso 4: t = 11, vence el quantum de P2 (6 de 8)
  Listos: P1, P3, P2 → ejecuta P1 (ráfaga de 2).

Paso 5: t = 13, P1 va a E/S hasta t=17
  Listos: P3, P2 → ejecuta P3.

Paso 6: t = 16 a 21
  t=16 vence el quantum de P3 (6 de 8) → listos: P2, P3 → ejecuta P2 (le quedan 2).
  t=17 P1 vuelve de E/S → listos: P3, P1.
  t=18 P2 termina la ráfaga y va a E/S hasta t=19 → ejecuta P3 (le quedan 2).
  t=19 P2 vuelve → listos: P1, P2.
  t=20 P3 termina → ejecuta P1 (1). t=21 P1 termina → ejecuta P2 (5): 21 a 24,
       vence el quantum pero no hay nadie en listos y sigue hasta t=26.

Paso 7: el Gantt
     0         5         10        15        20        25
     |.........|.........|.........|.........|.........|..
P1   ████░░░░░░░░░░········████░░░░░░░░······██
P2     ··██████······██████··········████░░····██████████
P3       ······██████··········██████····████

Paso 8: NTT = (tiempo en listos + CPU) / CPU
  P1: listos 4 + 3 = 7   CPU 2 + 2 + 1 = 5    NTT = 12 / 5  = 2,40
  P2: listos 1+3+5+2 = 11  CPU 8 + 5 = 13     NTT = 24 / 13 ≈ 1,85
  P3: listos 3+5+2 = 10  CPU 8                NTT = 18 / 8  = 2,25

Paso 9: el más perjudicado
  P1 (NTT = 2,40). Es I/O bound: usa poco de su quantum, se bloquea y al volver
  de la E/S hace toda la cola detrás de los CPU bound, que la usan completa.

Paso 10: otro algoritmo (justificación conceptual)
  VRR: al volver de E/S, P1 iría a la cola auxiliar, más prioritaria, con el
  quantum que no usó. O SJF/SRT/HRRN, que favorecen las ráfagas cortas de P1.

Control: fines P1=21, P3=20, P2=26; la CPU nunca queda libre y suma 5+13+8 = 26 ✓
```

### 3. Ejercicio guiado (recuperatorio 1C 2023, Ej 1)

> Realice el diagrama correspondiente a la siguiente traza de ejecución utilizando el algoritmo HRRN y un **grado de multiprogramación máximo igual a 3**. Los procesos A, B, C y D son creados en los instantes t=1, t=0, t=2 y t=9, respectivamente.
>
> ```
> Proceso   Creación   CPU   E/S   CPU   E/S   CPU
>    A         1        3     2     3     -     -
>    B         0        2     4     2     2     2
>    C         2        2     2     1     -     -
>    D         9        1     -     -     -     -
> ```
>
> a) Realice el diagrama GANTT. b) Si el grado de multiprogramación máximo fuese igual a 4, ¿habría algún cambio en el diagrama? ¿A partir de qué instante?

Es del tipo 1. HRRN es sin desalojo: solo hay que decidir cuando la CPU queda libre, y en cada decisión calculás $RR = (W + S)/S$ de los que están en listos. Un solo dispositivo de E/S. El grado 3 es del planificador de largo plazo: con 3 procesos en el sistema, el cuarto espera en nuevo.

```
Paso 1: t=2, B se bloquea. ¿Quiénes están en listos, y cuánto da el RR de cada uno?
  → ________

Paso 2: t=5, A se bloquea. ¿Cuándo empieza su E/S (el dispositivo lo usa B)?
  ¿Quién ejecuta?
  → ________

Paso 3: t=7, C se bloquea. ¿Quién ejecuta, y hasta cuándo?
  → ________

Paso 4: t=9, B se bloquea y se crea D. ¿Puede entrar D a listos? ¿Quién ejecuta?
  → ________

Paso 5: t=12, A termina. ¿Qué pasa con D? RR de los que están en listos:
  → ________

Paso 6: t=13, C termina. RR de B y de D:
  → ________

Paso 7: el Gantt completo
  → ________

Paso 8: b) con grado 4, ¿cuándo entra D a listos? ¿Cambia alguna decisión?
  → ________
```

### 4. Práctica

#### Ejemplo resuelto 2: SRT con estimación (Guía de planificación, Ej 3a)

> Algoritmo SRT (SJF con desalojo) con estimación, α = 0,5.
>
> ```
>      Llegada  Est. ant.  Real ant.   CPU   E/S   CPU
> A       2        4          5         2     1     2
> B       0        4          8        10     2     2
> C       3        2          3         2     8     3
> ```

Primero se calculan las estimaciones de las dos ráfagas de cada proceso; el Gantt se planifica con las estimaciones, pero cada ráfaga dura lo real. Desalojo: se compara la estimación del que llega con la estimación restante del que ejecuta.

```
Paso 1: estimación de la 1ª ráfaga: Est = 0,5 · Real ant. + 0,5 · Est. ant.
  A: 0,5·5 + 0,5·4 = 4,5     B: 0,5·8 + 0,5·4 = 6     C: 0,5·3 + 0,5·2 = 2,5

Paso 2: estimación de la 2ª ráfaga (con la 1ª real)
  A: 0,5·2 + 0,5·4,5 = 3,25   B: 0,5·10 + 0,5·6 = 8   C: 0,5·2 + 0,5·2,5 = 2,25

Paso 3: t=0 a 5
  t=0  solo B → ejecuta B (est. 6).
  t=2  llega A (4,5). Restante de B: 6 − 2 = 4 < 4,5 → sigue B.
  t=3  llega C (2,5). Restante de B: 6 − 3 = 3 > 2,5 → C desaloja a B.
  t=5  C se bloquea (E/S 8, hasta 13). Listos: A (4,5), B (3) → ejecuta B.

Paso 4: t=12 a 16
  t=12 B termina la ráfaga real de 10 y va a E/S (el dispositivo lo tiene C:
       espera hasta 13, E/S de 13 a 15). Ejecuta A (4,5).
  t=13 C vuelve (2,25). Restante de A: 4,5 − 1 = 3,5 > 2,25 → C desaloja a A.
  t=15 B vuelve (8). Restante de C: 2,25 − 2 = 0,25 → sigue C.
  t=16 C termina. Listos: A (restante 3,5), B (8) → ejecuta A.

Paso 5: t=17 a 21
  t=17 A termina la ráfaga (real 2) y va a E/S hasta 18 → ejecuta B.
  t=18 A vuelve (3,25). Restante de B: 8 − 1 = 7 > 3,25 → A desaloja a B.
  t=20 A termina → B ejecuta 20 a 21 y termina.

Paso 6: el Gantt
     0         5         10        15        20
     |.........|.........|.........|.........|..
A        ····················██······██░░████
B    ██████····██████████████--░░░░····██····██
C          ████░░░░░░░░░░░░░░░░██████

Control: coincide con la resolución de la cátedra (desalojos en t=3, 13 y 18) ✓
```

#### Ejemplo resuelto 3: HRRN (Guía de planificación, Ej 5b)

> ```
>      Llegada   CPU   E/S   CPU
> A       1       4     4     2
> B       0       6     3     3
> C       3       3     1     7
> ```

HRRN, sin desalojo. Las decisiones son cuando la CPU queda libre; en cada una, el RR de los que están en listos.

```
Paso 1: t=0 solo B → ejecuta B hasta t=6 (sin desalojo).

Paso 2: t=6, B se bloquea (E/S hasta 9)
  A: W = 6 − 1 = 5, S = 4 → RR = 9/4 = 2,25
  C: W = 6 − 3 = 3, S = 3 → RR = 6/3 = 2
  → ejecuta A (6 a 10).

Paso 3: t=10, A se bloquea (E/S hasta 14)
  C: W = 10 − 3 = 7, S = 3 → RR = 10/3 ≈ 3,33
  B: W = 10 − 9 = 1, S = 3 → RR = 4/3 ≈ 1,33
  → ejecuta C (10 a 13).

Paso 4: t=13, C se bloquea (el dispositivo lo tiene A: E/S de 14 a 15). Solo B → B hasta 16.

Paso 5: t=16, B termina
  A: W = 16 − 14 = 2, S = 2 → RR = 2
  C: W = 16 − 15 = 1, S = 7 → RR = 8/7 ≈ 1,14
  → ejecuta A (16 a 18) y después C (18 a 25).

Paso 6: el Gantt
     0         5         10        15        20        25
     |.........|.........|.........|.........|.........|
A      ··········████████░░░░░░░░····████
B    ████████████░░░░░░········██████
C          ··············██████--░░······██████████████

Control: coincide con la resolución de la cátedra (decisiones en t=6, 10, 13 y 16) ✓
```

#### Ejercicio extra 1: SJF con estimación (hoja «1C 2017 TT» de la práctica adicional)

> SJF sin desalojo con α = 0,4. Calcule la estimación de la segunda ráfaga de cada proceso y realice el Gantt.
>
> ```
>      Llegada   Est. 1ª   CPU   E/S   CPU
> P1      0         2       5     1     6
> P2      0         3       4     1     4
> P3      8         1       2     2     1
> P4     17         1       6     6     4
> ```

#### Ejercicio extra 2: el mismo lote con tres algoritmos (Guía de planificación, Ej 5)

> Con los datos del ejemplo resuelto 3 (A, B y C), realice el Gantt con a) SJF sin desalojo y c) SRT. Compare en qué instante termina cada proceso con los tres algoritmos.

#### Ejercicio extra 3: prioridades con desalojo (Guía de planificación, Ej 4)

> Prioridades con desalojo (menor número = mayor prioridad).
>
> ```
>      Llegada   CPU   E/S   CPU   Prioridad
> A       1       2     1     5       1
> B       1      10     5     5       3
> C       0       2     2     3       2
> ```

#### Ejercicio extra 4: RR y VRR (Guía de planificación, Ej 6)

> Realice el Gantt con a) Round Robin con Q = 3 y b) Virtual Round Robin con Q = 3.
>
> ```
>      Llegada   CPU   E/S   CPU   E/S   CPU
> A       0       2     1     6     -     -
> B       1       2     3     4     -     -
> C       3       1     2     1     1     2
> D       9       5     -     -     -     -
> ```

#### Ejercicio extra 5: teoría (Práctica avanzada 1er parcial, "Aaah mirá vos", ítem b)

> Explique al menos dos posibles desventajas del algoritmo HRRN.

### 5. Cierre

**Fórmulas**

$$Est_{n+1} = \alpha \cdot R_n + (1 - \alpha) \cdot Est_n \qquad RR = \frac{W + S}{S} \qquad Q' = Q - \text{lo ejecutado}$$

$$T_{\text{retorno}} = T_{\text{fin}} - T_{\text{llegada}} \qquad NTT = \frac{\sum T_{\text{listo}} + \sum CPU}{\sum CPU}$$

```
Sin desalojo: FIFO, SJF, HRRN, prioridades (sin)     Con desalojo: SRT, RR, VRR, prioridades (con)
Mismo instante a listos: fin de quantum > fin de E/S > nuevo     Empates: FIFO
Un solo dispositivo de E/S con cola FIFO (salvo que el enunciado diga otra cosa)
```

**Trampas**
- **Hacer E/S en paralelo con un solo dispositivo.** Si el dispositivo está ocupado, el proceso espera bloqueado; revisá cuándo se libera.
- **Ordenar mal los que llegan juntos a listos.** Primero el de fin de quantum, después el de fin de E/S, después el nuevo.
- **En SRT, comparar con la ráfaga entera del que ejecuta.** Es con lo que le **resta** (o con la estimación restante).
- **En HRRN, contar W desde la llegada al sistema.** W es el tiempo en listos desde la última vez que entró; si el grado de multiprogramación no lo dejó entrar, W empieza cuando entra.
- **En VRR, darle quantum completo al que vuelve de E/S.** Ejecuta solo Q'; y el que agotó el quantum va a la cola común.
- **Desalojar en un empate.** Con desalojo, solo si el que llega es estrictamente mejor.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Por qué Round Robin perjudica a los procesos I/O bound y cómo lo corrige VRR?
2. (Ejercicio) RR con Q = 2 y un solo dispositivo de E/S. P1 llega en 0 (CPU 3, E/S 2, CPU 1); P2 llega en 1 (CPU 2, E/S 1, CPU 2). Hacé el Gantt y calculá el tiempo de retorno de cada uno. (material propio)

## 1.3 Colas multinivel ☆☆☆☆☆ (0 de 4)

Temas en Lumen: `u3-colas-multinivel-sin-realimentacion`

No apareció en los parciales relevados, pero tiene ejercicios propios en la guía (colas multinivel y feedback) y la planilla de colas multinivel viene de un TP. Se resuelve igual que el bloque 1.2, con más de una cola.

### 1. Conceptos

**Colas multinivel.** Hay varias colas de listos, cada una con su prioridad y su propio algoritmo (por ejemplo, RR en todas, o RR arriba y FIFO abajo). Entre colas se elige con **prioridades**: se atiende una cola solo si las de más prioridad están vacías. En las colas multinivel **sin realimentación**, cada proceso queda siempre en la misma cola.

```
 más prioridad   cola 0: RR Q=4   ──┐
                 cola 1: RR Q=2   ──┼──→ CPU
 menos           cola 2: FIFO     ──┘
```

**Realimentadas (feedback).** Los procesos cambian de cola según cómo usan la CPU. En la versión de la guía, todos entran a la cola de más prioridad; el que **agota el quantum** baja una cola; el que se bloquea antes de agotarlo, al volver de la E/S, entra otra vez **arriba**. Así los I/O bound quedan arriba y los CPU bound se van hundiendo.

**Lo que tiene que definir el enunciado.** Sin esto no se puede resolver:
1. Cuántas colas hay.
2. El algoritmo (y el quantum) de cada cola.
3. A qué cola llegan los nuevos, y a cuál vuelven los que salen de E/S.
4. El criterio para bajar o subir de cola.
5. El algoritmo entre colas: si una cola más prioritaria **desaloja** o no al que ejecuta de una cola más baja.

Ojo con el punto 5: puede ser mixto. En un ejercicio de la práctica adicional, las colas RR desalojan a la FIFO, pero la RR con Q = 2 no desaloja a la RR con Q = 4.

**Los tipos de ejercicio que toman:**
1. **Gantt con colas multinivel** fijas (prioridad por proceso, RR en cada cola).
2. **Gantt con feedback** (bajar de cola al agotar el quantum).
3. **Teoría:** qué hay que definir en un esquema multinivel; por qué el feedback favorece a los I/O bound.

### 2. Ejemplo resuelto (Guía de planificación, Ej 7)

> Colas multinivel realimentadas: la cola de mayor prioridad es Round Robin con Q = 2 y la de menor prioridad es FIFO. Los procesos nuevos entran a la cola RR; el que agota el quantum baja a la FIFO; al volver de E/S, el proceso entra a la cola RR. La cola RR desaloja a la FIFO.
>
> ```
>      Llegada   CPU   E/S   CPU   E/S   CPU
> A       0       4     3     2     -     -
> B       0       2     3     1     4     1
> C       3      10     2     5     -     -
> ```

Es del tipo 2. Se sigue en qué cola está cada proceso. Un solo dispositivo de E/S; empates por FIFO.

```
Paso 1: t=0 a 4 (cola RR)
  t=0  A y B en RR → ejecuta A. t=2 A agota Q=2 → baja a FIFO. Ejecuta B.
  t=3  llega C a RR.
  t=4  B termina su ráfaga (2, justo Q) y va a E/S hasta 7: no agotó el quantum
       por desalojo, se bloqueó → vuelve a RR. Ejecuta C (RR).

Paso 2: t=6, C agota Q=2 → baja a FIFO
  RR vacía. FIFO: A, C → ejecuta A (le quedan 2).

Paso 3: t=7, B vuelve de E/S a RR → desaloja a A (la RR desaloja a la FIFO)
  B ejecuta 7 a 8 y va a E/S (4) hasta 12. FIFO: C, A → ejecuta C.

Paso 4: t=12, B vuelve a RR → desaloja a C
  B ejecuta 12 a 13 y termina. FIFO: A, C → ejecuta A (1 que le quedaba).
  t=14 A va a E/S hasta 17 → ejecuta C.

Paso 5: t=17, A vuelve a RR → desaloja a C
  A ejecuta 17 a 19 y termina. Ejecuta C (FIFO) hasta 20, E/S de 20 a 22,
  vuelve a RR: ejecuta 22 a 24, agota Q → FIFO, sigue solo hasta 27.

Paso 6: el Gantt
     0         5         10        15        20        25
     |.........|.........|.........|.........|.........|....
A    ████········██············██░░░░░░████
B    ····████░░░░░░██░░░░░░░░██
C          ··████····████████····██████····██░░░░██████████

Control: coincide con la resolución de la cátedra (desalojos en t=7, 12 y 17) ✓
```

### 3. Ejercicio guiado (Ejercicios de colas multinivel, hoja «Básico»)

> Se tendrá una cola por cada nivel de prioridad (0 = más prioridad). El algoritmo entre colas es de prioridades **sin desalojo**. Cada cola usa Round Robin con Q = 2. Al llegar a listos, un proceso se pone al final de su cola. Ante un empate de llegada a listos: primero fin de quantum, después fin de E/S, después nuevo.
>
> ```
>      Prioridad   Llegada   CPU   E/S   CPU
> P1       0          0       3     9     2
> P2       1          1       3     4     3
> P3       1          2       3     -     -
> P4       2          0       3     -     -
> P5       2          0       3     -     -
> ```

Es del tipo 1. Las colas son fijas: cada proceso vive en la cola de su prioridad. Como entre colas es sin desalojo, un proceso de más prioridad que llega espera a que el que ejecuta termine su quantum o se bloquee. Un solo dispositivo de E/S.

```
Paso 1: t=0 a 3. ¿Quién ejecuta y qué pasa en t=2?
  → ________

Paso 2: t=3, P1 se bloquea (E/S 9, hasta 12). ¿Quién ejecuta, y qué pasa en t=5?
  → ________

Paso 3: t=7 y t=8. ¿Cuándo va P2 a E/S y cuándo la puede empezar?
  → ________

Paso 4: t=9 a 13. Cola 1 vacía: ¿cómo se reparten P4 y P5?
  → ________

Paso 5: t=12, P1 vuelve a la cola 0 mientras ejecuta P5. ¿Lo desaloja?
  → ________

Paso 6: el Gantt completo e instante en que termina cada proceso
  → ________
```

### 4. Práctica

#### Ejercicio extra 1: quantum distinto por cola (Ejercicios de colas multinivel, hoja «Avanzado»)

> Mismo esquema que el guiado (una cola por prioridad, prioridades sin desalojo entre colas, RR en cada cola), pero con quantum 4 en la cola 0, 2 en la cola 1 y 1 en la cola 2.
>
> ```
>      Prioridad   Llegada   CPU   E/S   CPU   E/S   CPU
> P1       0          0       4     3     5     -     -
> P2       1          1       1     1     3     -     -
> P3       2          0       3     -     -     -     -
> P4       0          2       2     5     1     3     1
> P5       1          0       3     1     2     2     1
> ```

#### Ejercicio extra 2: feedback con tres colas (Práctica adicional, hoja «Feedback»)

> Colas realimentadas: RR con Q = 2 (la de más prioridad), RR con Q = 4 y FIFO. Los nuevos y los que vuelven de E/S entran a la RR Q = 2; el que agota el quantum baja una cola. Las colas RR desalojan a la FIFO, pero la RR Q = 2 no desaloja a la RR Q = 4.
>
> ```
>      Llegada   CPU   E/S   CPU
> P1      0       3     3     2
> P2      0       1     7     1
> P3      1       4     8     4
> P4      2       1     2    10
> ```

#### Ejercicio extra 3: teoría (material propio, sobre la clase de planificación)

> ¿Qué hay que definir para especificar un algoritmo de colas multinivel? ¿Por qué con feedback los procesos I/O bound quedan en las colas de más prioridad?

### 5. Cierre

**Fórmulas**

```
Entre colas: prioridades (se atiende una cola solo si las de arriba están vacías)
Sin realimentación: cada proceso siempre en su cola
Feedback: agota el quantum → baja una cola; se bloquea antes → vuelve arriba
Definir: nº de colas, algoritmo de cada una, cola de entrada, criterio de cambio, desalojo entre colas
```

**Trampas**
- **Desalojar entre colas cuando es sin desalojo.** Si el enunciado dice "prioridades sin desalojo", el de más prioridad espera al fin del quantum o al bloqueo.
- **Bajar de cola al que se bloqueó.** Baja solo el que agota el quantum.
- **Suponer las reglas.** Leé a qué cola vuelven los que salen de E/S y quién desaloja a quién: cambian de un ejercicio a otro.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Qué diferencia hay entre colas multinivel con y sin realimentación? ¿Qué cinco cosas tiene que definir el esquema?
2. (Ejercicio) Feedback con dos colas: RR Q = 1 arriba y FIFO abajo, la RR desaloja a la FIFO. P1 llega en 0 (CPU 3); P2 llega en 1 (CPU 1, E/S 1, CPU 1). Hacé el Gantt. (material propio)

## 1.4 Planificación con hilos: ULT, KLT y jacketing ★★☆☆☆ (1 de 4)

Temas en Lumen: `u2-hilos-implementacion-ciclo-vida`

Entre los parciales con fecha apareció en el recuperatorio de 1C 2022. Pero los cuatro ejercicios de parcial sin fecha que dejó la cátedra (en "Ejercicios de parcial" y en la "Práctica avanzada 1er parcial") son de este tipo, así que es probable que lo tomen. Usa todo el bloque 1.2.

### 1. Conceptos

**Dos niveles de planificación.** El **SO** planifica KLTs (hilos de kernel): para él, un proceso con ULTs es **un solo KLT**. Dentro de ese KLT, la **biblioteca** de hilos planifica sus ULTs (hilos de usuario) con su propio algoritmo, que puede ser distinto del SO. En el Gantt se dibuja una fila por ULT, agrupadas por KLT.

**Cuándo planifica la biblioteca.** Solo cuando recupera el control: cuando un ULT termina, cede la CPU o hace una llamada a la biblioteca. La biblioteca **no se entera** de lo que hace el SO: si el SO desaloja al KLT por fin de quantum, al volver sigue el mismo ULT que estaba. Por eso, entre ULTs no hay desalojo por quantum del SO.

**E/S sin jacketing.** Si un ULT hace una E/S bloqueante, el SO bloquea **al KLT entero**: ningún otro ULT del proceso puede ejecutar hasta que termine esa E/S. Es la gran desventaja de los ULT. En la guía hay dos variantes, según quién maneje la E/S:
- **Por biblioteca** (la E/S pasa por un wrapper de la biblioteca): cuando la E/S termina, la biblioteca recupera el control y **replanifica** entre sus ULTs.
- **Por el SO** (llamada directa): al terminar la E/S sigue el **mismo ULT** que la pidió, sin replanificar.

**Jacketing.** La biblioteca convierte la E/S bloqueante en una no bloqueante: el ULT que pide la E/S queda bloqueado para la biblioteca, pero el KLT **sigue ejecutando** otro ULT listo. El KLT solo se bloquea si todos sus ULTs están bloqueados.

```
              sin jacketing                    con jacketing
t=2  UA2 pide E/S → se bloquea TODO KA     UA2 pide E/S → KA sigue con UA1
     el SO elige otro KLT                   (el SO no se entera)
```

**Ventajas y desventajas.** Los ULT tienen menos overhead (el cambio entre ULTs no pasa por el SO), son portables y cada proceso elige su algoritmo. Pero no aprovechan varios procesadores (un KLT ejecuta en una sola CPU a la vez) y, sin jacketing, una E/S bloquea a todos. Los KLT permiten paralelismo y que un hilo bloqueado no frene a los demás, a cambio de más overhead.

**Leer un Gantt de hilos.** Para deducir un algoritmo, buscá los instantes donde **hubo que elegir** entre dos o más candidatos y fijate si la elección cumple cada algoritmo (FIFO, SJF, HRRN, RR, VRR...). Descartá los que fallan en algún instante. Un instante con un solo candidato no dice nada.

**Los tipos de ejercicio que toman:**
1. **Gantt con KLTs y ULTs,** con o sin jacketing, algoritmo del SO y de la biblioteca dados.
2. **Leer una traza:** qué algoritmo usa el SO y qué algoritmo podría usar cada biblioteca, justificando con dos instantes.
3. **Encontrar un error** en un Gantt dado, o el valor de α para que pase algo.
4. **Qué cambiaría:** con jacketing, si los ULT fuesen KLT (o al revés), con otro algoritmo; sin rehacer el Gantt.

### 2. Ejemplo resuelto (Guía de planificación, Ej 9, sin jacketing)

> El SO planifica con FIFO. El proceso A tiene dos ULTs, planificados por la biblioteca con SJF sin desalojo, sin jacketing (la E/S pasa por la biblioteca, que replanifica al volver). Los procesos B (con dos KLTs) y C (un KLT) no tienen ULTs. Todas las E/S son al mismo disco.
>
> ```
>              Llegada   CPU   Disco   CPU
> A: ULT A1       0       3      4      1
> A: ULT A2       0       2      4      2
> KLT B1          4       4      2      2
> KLT B2          4       2      3      2
> KLT C           5       1      1      2
> ```

Es del tipo 1. Para el SO hay cuatro KLT: A, B1, B2 y C. Cuando A tiene la CPU, la biblioteca elige entre A1 y A2 por SJF. Sin jacketing, cualquier E/S de A1 o A2 bloquea a todo A.

```
Paso 1: t=0, solo A. La biblioteca elige por SJF: A2 (2) < A1 (3) → A2.
  t=2  A2 pide disco (hasta 6): sin jacketing, se bloquea todo A.
       A1 no puede ejecutar. La CPU queda libre hasta t=4.

Paso 2: t=4 llegan B1 y B2 → FIFO: B1 ejecuta 4 a 8.
  t=5 llega C. t=6 A vuelve (A2 terminó la E/S). Cola: B2, C, A.

Paso 3: t=8, B1 va a disco (8 a 10) → ejecuta B2 (8 a 10).
  t=10 B2 pide disco (B1 lo acaba de liberar) → disco de 10 a 13. Ejecuta C.
  t=11 C pide disco: ocupado → espera hasta 13, disco de 13 a 14. Ejecuta A.

Paso 4: t=11, A tiene la CPU: la biblioteca replanifica.
  A2 (le falta la 2ª ráfaga de 2) < A1 (3) → A2 ejecuta 11 a 13 y termina.
  t=13 A1 ejecuta 13 a 16 (A sigue: FIFO no desaloja) y pide disco (16 a 20).

Paso 5: t=16 a 23
  Cola: B1 (volvió en 10), B2 (13), C (14) → B1 16-18, B2 18-20, C 20-22.
  A vuelve en 20 → A1 ejecuta 22 y termina en 23.

Paso 6: el Gantt (en hilos solo se marcan CPU, E/S y espera del disco)
          0         5         10        15        20
          |.........|.........|.........|.........|......
A:UA1                               ██████░░░░░░░░    ██
A:UA2     ████░░░░░░░░          ████
B1                ████████░░░░            ████
B2                        ████░░░░░░          ████
C                             ██----░░            ████

Control: coincide con la resolución de la cátedra (en t=11 elige A2; en t=13, A1) ✓
```

### 3. Ejercicio guiado (Ejercicios de parcial de planificación, Ej 3, "¿Que el alfa qué?")

> Un estudiante realizó el siguiente Gantt. Se presupone que el sistema operativo, para planificar, utiliza RR con Q = 3 para los KLTs, y los ULTs se planifican mediante SJF con desalojo utilizando estimaciones.
>
> ```
>              Est. inicial   Llegada   CPU   E/S   CPU
> K1               -            0        2     3     2
> K2: ULT1         1            2        4     2     1
> K2: ULT2         4            5        3     3     4
>
>           0         5         10        15
>           |.........|.........|.........|..
> K1        ████░░░░░░      ████
> K2:U1         ██████          ██░░░░██
> K2:U2               ██████░░░░░░████  ████
> ```
>
> a) ¿Se puede determinar algún error en el Gantt? ¿A partir de qué instante? Justifique. b) Suponiendo una función de estimación $EST_{n+1} = R_n \cdot \alpha + EST_n \cdot (1 - \alpha)$ y sabiendo por el gráfico que ULT1 desaloja a ULT2 en el instante 13, ¿a qué valor tiende el coeficiente α? Justifique. c) ¿Cambiaría el Gantt en algún instante si decimos que no hay jacketing entre los ULTs?

Es del tipo 3. Es un Gantt ya hecho: hay que revisarlo instante por instante con las reglas. Ojo: en el enunciado original las columnas se numeran desde 1; acá se pasó al eje que arranca en 0.

```
Paso 1: a) Hasta t=5, ¿qué pasa en K2? ¿Cuál es la estimación restante de U1 en t=5?
  → ________

Paso 2: a) En t=5 llega U2 con estimación 4. ¿Debería desalojar a U1? ¿Dónde está el error?
  → ________

Paso 3: b) Estimación de la 2ª ráfaga de U1 en función de α (real anterior 4, est. 1)
  → ________

Paso 4: b) Estimación de la 2ª ráfaga de U2 en función de α, y cuánto le resta en t=13
  (ya ejecutó 2 de esa ráfaga)
  → ________

Paso 5: b) Condición para que U1 desaloje a U2, y a qué valor tiende α
  → ________

Paso 6: c) En t=8, U2 pide E/S. Sin jacketing, ¿qué pasa con K2? ¿Qué pasa en t=10?
  → ________
```

### 4. Práctica

#### Ejemplo resuelto 2: leer una traza (Práctica avanzada 1er parcial, "Aaah mirá vos")

> Sabiendo que los tiempos de arribo para la siguiente traza de ejecución son K1 → 1, K2 → 0, K3 → 2:
>
> ```
>            0         5         10        15
>            |.........|.........|.........|......
> K1           ████░░  ████░░                ████
> K2         ██░░  ████░░                ████
> K3:U31                   ██░░  ████
> K3:U32                     ████░░  ████
> ```
>
> a) ¿Cuál fue el algoritmo de planificación usado por el SO? Justifique indicando al menos dos instantes de tiempo que muestren el comportamiento de dicho algoritmo. b) Explique al menos dos posibles desventajas del algoritmo indicado en el punto a. c) ¿Qué algoritmos de planificación podría estar utilizando la biblioteca de hilos de K3?

Es del tipo 2. Primero se leen las ráfagas de cada KLT. K3 ejecuta de 7 a 14 sin cortar: cuando U31 hace E/S, sigue U32, así que tiene jacketing, y para el SO K3 es una sola ráfaga de 7. Después se prueban los algoritmos en los instantes donde hubo que elegir.

```
Paso 1: ráfagas vistas por el SO
  K2: CPU 1, E/S 1, CPU 2, E/S 1, CPU 2      K1: CPU 2, E/S 1, CPU 2, E/S 1, CPU 2
  K3: una ráfaga de 7 (de 7 a 14)

Paso 2: instantes de decisión (con más de un candidato)
  t=3: K2 (volvió en 2, S=2) o K3 (llegó en 2, S=7) → eligió K2
  t=5: K1 (volvió en 4, S=2) o K3 (S=7) → eligió K1
  t=7: K3 o K2 (volvió en 6, S=2) → eligió K3
  t=14: K2 (volvió en 6) o K1 (volvió en 8) → eligió K2

Paso 3: descartar
  FIFO: en t=5 elegiría K3 (espera desde 2) → ✗
  SJF:  en t=7 elegiría K2 (2 < 7) → ✗
  RR:   K3 ejecuta 7 seguidas con K1 y K2 en listos → ✗ (salvo Q ≥ 7, que es FIFO)

Paso 4: HRRN, RR = (W + S) / S
  t=3:  K2 = (1 + 2)/2 = 1,5    K3 = (1 + 7)/7 ≈ 1,14  → K2 ✓
  t=5:  K1 = (1 + 2)/2 = 1,5    K3 = (3 + 7)/7 ≈ 1,43  → K1 ✓
  t=7:  K3 = (5 + 7)/7 ≈ 1,71   K2 = (1 + 2)/2 = 1,5   → K3 ✓
  t=14: K2 = (8 + 2)/2 = 5      K1 = (6 + 2)/2 = 4     → K2 ✓
  a) El SO usa HRRN (sin desalojo).

Paso 5: b) desventajas de HRRN
  Necesita conocer o estimar la duración de la próxima ráfaga; recalcula el RR de
  todos en cada decisión (overhead); y como no desaloja, uno largo retiene la CPU
  (K3 hizo esperar 7 unidades a K1 y K2), lo que empeora el tiempo de respuesta.

Paso 6: c) biblioteca de K3
  La única elección real es en t=7: U31 (ráfaga 1) antes que U32 (ráfaga 2).
  Después siempre hay un solo ULT listo (t=8 solo U32, t=10 solo U31, t=12 solo U32).
  Sirve cualquiera que en t=7 elija a U31: FIFO (si U31 llegó primero), SJF, SRT
  o HRRN (U31 es más corto), o RR con Q ≥ 2.

Control: con HRRN se reproduce toda la traza del SO, sin CPU ociosa ✓
```

#### Ejercicio extra 1: RR con KLTs y ULTs mezclados (recuperatorio 1C 2022, Ej 1)

> En un SO que utiliza Round Robin con Q = 2 ejecutan 3 procesos. Uno de ellos implementa una biblioteca ULT que utiliza FIFO como algoritmo de planificación. Para las E/S, uno de los ULT utiliza un wrapper que implementa jacketing (ULT2.2) y el otro no (ULT2.1).
>
> ```
>                  Arribo   CPU   E/S   CPU
> P1: KLT1.1         0       3     1     5
> P1: KLT1.2         1       1     2     1
> P2: ULT2.1         2       3     1     2
> P2: ULT2.2         3       1     1     1
> ```
>
> a) Realice el diagrama Gantt. b) Si los hilos del proceso 2 fuesen KLTs, ¿en qué instante y por qué motivo cambiaría el orden de ejecución de los procesos? c) Si los hilos del proceso 1 fuesen ULTs, ¿en qué instante y por qué motivo cambiaría el orden de ejecución de los procesos?

#### Ejercicio extra 2: leer una traza con bibliotecas (Ejercicios de parcial de planificación, Ej 2)

> Sabiendo que los tiempos de arribo de los KLTs son KA = 0, KC = 1 y KB = 3, indique: a) ¿Qué algoritmo podría estar usando el SO? b) ¿Qué algoritmo podría estar usando la biblioteca de KA? c) ¿Y la de KC? d) (Sin volver a resolver el ejercicio) Indique qué cambios hubiesen ocurrido si las bibliotecas hubiesen usado jacketing. e) En caso de utilizar otro algoritmo el SO, ¿se podría haber terminado la ejecución total antes? En a, b y c, justifique mostrando al menos 2 instantes.
>
> ```
>            0         5         10        15        20
>            |.........|.........|.........|.........|....
> KA:UA1                               ████    ████
> KA:UA2     ██░░              ██
> KA:UA3           ██    ██░░                        ████
> KB                 ████        ██░░░░░░░░██
> KC:UC1                             ██      ██░░░░██
> KC:UC2       ████░░      ████    ██
> ```

#### Ejercicio extra 3: el mismo ejercicio con jacketing (Guía de planificación, Ej 9)

> Resuelva el ejemplo resuelto de este bloque suponiendo que la biblioteca de A usa jacketing. ¿En qué instante aparece la primera diferencia?

### 5. Cierre

**Fórmulas**

```
El SO planifica KLTs (un proceso con ULTs = 1 KLT); la biblioteca planifica sus ULTs
La biblioteca decide solo cuando recupera el control; no ve el quantum del SO
Sin jacketing: E/S de un ULT → se bloquea todo el KLT
Con jacketing: E/S de un ULT → el KLT sigue con otro ULT (se bloquea si no queda ninguno)
Leer una traza: instantes con 2 o más candidatos → descartar algoritmos
```

$$Est_{n+1} = \alpha \cdot R_n + (1 - \alpha) \cdot Est_n$$

**Trampas**
- **Hacer que la biblioteca desaloje por el quantum del SO.** El SO desaloja al KLT; al volver, sigue el mismo ULT.
- **Dejar ejecutar a otro ULT durante una E/S sin jacketing.** Se bloquea el KLT entero.
- **Tratar a los ULT como procesos separados en la cola del SO.** En la cola del SO hay un solo KLT por proceso con ULTs.
- **Justificar un algoritmo con un instante de un solo candidato.** No prueba nada: buscá instantes con elección.
- **Mezclar el eje que empieza en 1 con el que empieza en 0.** Revisá cómo numera el enunciado antes de nombrar un instante.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Qué es el jacketing y qué problema de los ULT resuelve? Nombrá una ventaja de los ULT y una de los KLT.
2. (Ejercicio) SO con FIFO. KLT K1 llega en 0 (CPU 2). El proceso P tiene dos ULTs con biblioteca FIFO, sin jacketing (la E/S pasa por la biblioteca): U1 llega en 0 (CPU 1, E/S 3, CPU 1) y U2 llega en 0 (CPU 2). La cola del SO arranca P, K1. Hacé el Gantt. (material propio)

## Respuestas del capítulo 1

### 1.1 Ejercicio guiado

```
Paso 1: el primer fork() duplica al original → 2 procesos.

Paso 2: el segundo fork() lo ejecutan los 2 → 4 procesos.
  Los 2 nuevos son hijos de ese fork (reciben 0); los 2 viejos reciben un PID.

Paso 3: el fork() del if lo ejecutan solo esos 2 hijos → 2 procesos más → 6 en total.

Paso 4: todos llegan al printf → "hola" se imprime 6 veces.

Control: árbol (H1 nace del 1er fork; H2 y H1a, del 2º; H2' y H1a', del if)
  P ──┬── H1 ──── H1a ──── H1a'
      └── H2 ──── H2'
  Procesos: P, H1, H2, H1a, H2', H1a' = 6 ✓
```

### 1.1 Práctica

```
1. Largo plazo: nuevo → listo (admitir) y salida a finalizado. Mediano plazo: listo o
   bloqueado ⇄ suspendido (swap). Corto plazo: listo → ejecutando.
2. Verdadero: pasar de usuario a kernel (o al revés) implica guardar el contexto del
   que ejecutaba y cargar el del SO (o restaurar el del proceso).
3. Comparten código, datos, heap y archivos abiertos (los recursos del proceso).
   Cada uno tiene su PC, sus registros, su pila y su estado (TCB).
4. Porque comparten el espacio de direcciones: no hay que cambiar la memoria ni los
   recursos, solo el contexto de CPU. Si son ULT, ni siquiera interviene el SO.
5. De usuario a kernel, con una interrupción o una syscall. De kernel a usuario, con
   una instrucción privilegiada (o restaurando el contexto del proceso).
6. Ventaja: es más robusto y modular (un driver que falla no tira el sistema).
   Desventaja: es más lento, porque los servicios se piden por mensajes entre procesos.
```

### 1.1 Autoevaluación

```
1. Cambio de modo: usuario ⇄ kernel. Cambio de contexto: guardar un contexto y
   cargar otro. Cambio de proceso: pasa a ejecutar otro proceso. Ejemplo de cambio
   de contexto sin cambio de proceso: una syscall (read) que, al terminar, vuelve
   al mismo proceso.

2. 3 forks seguidos → 2^3 = 8 procesos; se imprimen 8 "x".
   En el hijo, fork() devuelve 0 (en el padre, el PID del hijo).
```

### 1.2 Ejercicio guiado

```
Paso 1: t=2 listos: A (llegó en 1: W=1, S=3) y C (llegó en 2: W=0, S=2)
  RR(A) = (1 + 3)/3 ≈ 1,33    RR(C) = (0 + 2)/2 = 1   → ejecuta A (2 a 5).
  B hace E/S de 2 a 6.

Paso 2: t=5, A pide E/S, pero el dispositivo lo tiene B hasta 6: A espera y hace
  E/S de 6 a 8. Solo C en listos → C ejecuta 5 a 7.

Paso 3: t=7, C pide E/S: el dispositivo lo tiene A hasta 8 → E/S de 8 a 10.
  Solo B (volvió en 6) → B ejecuta 7 a 9.

Paso 4: t=9, B pide E/S (el dispositivo lo tiene C: E/S de 10 a 12). Se crea D,
  pero hay 3 procesos en el sistema (A, B, C) → D queda en nuevo.
  Solo A (volvió en 8) → A ejecuta 9 a 12.

Paso 5: t=12, A termina → baja a 2 el número de procesos y D entra a listos (W empieza acá).
  C: volvió en 10 → W=2, S=1 → RR = 3
  B: volvió en 12 → W=0, S=2 → RR = 1
  D: entró en 12  → W=0, S=1 → RR = 1
  → ejecuta C (12 a 13) y termina.

Paso 6: t=13
  B: W=1, S=2 → RR = 1,5     D: W=1, S=1 → RR = 2   → ejecuta D (13 a 14).
  Después B ejecuta 14 a 16 y termina.

Paso 7: el Gantt (n = D esperando que el grado de multiprogramación lo deje entrar)
     0         5         10        15
     |.........|.........|.........|..
A      ··██████--░░░░··██████
B    ████░░░░░░░░··████--░░░░····████
C        ······████--░░░░····██
D                      nnnnnn··██

Paso 8: b) Con grado 4, D entra a listos al crearse (t=9). La primera diferencia es
  en t=12: D tiene W=3, S=1 → RR = 4, más que C (3) → ejecuta D (12 a 13), después
  C (13 a 14) y B (14 a 16). Cambia a partir del instante 12.
```

### 1.2 Ejercicio extra 1

```
Estimaciones de la 2ª ráfaga (α = 0,4): Est = 0,4 · real + 0,6 · est
  P1: 0,4·5 + 0,6·2 = 3,2    P2: 0,4·4 + 0,6·3 = 3,4
  P3: 0,4·2 + 0,6·1 = 1,4    P4: 0,4·6 + 0,6·1 = 3

Decisiones: t=0 P1 (2) < P2 (3). t=5 solo P2. t=9 P3 (1) < P1 (3,2).
  t=11 P1 (3,2) < P2 (3,4). t=17 P4 (1) < P3 (1,4) < P2 (3,4). t=23 P3, después P2.

     0         5         10        15        20        25        30
     |.........|.........|.........|.........|.........|.........|......
P1   ██████████░░··········████████████
P2   ··········████████░░····························████████
P3                   ··████░░░░····················██
P4                                     ████████████░░░░░░░░░░░░████████

Fines: P1=17, P3=24, P2=28, P4=33. (La cátedra muestra el Gantt hasta t=23.)
```

### 1.2 Ejercicio extra 2

```
a) SJF sin desalojo
     0         5         10        15        20        25
     |.........|.........|.........|.........|.........|
A      ······················████████░░░░░░░░······████
B    ████████████░░░░░░██████
C          ······██████░░············██████████████
   Fines: B=12, C=23, A=25.

b) HRRN (ejemplo resuelto 3): B=16, A=18, C=25.

c) SRT
     0         5         10        15        20        25
     |.........|.........|.........|.........|.........|
A      ████████░░░░░░░░████
B    ██··············██····████████░░░░░░██████
C          ····██████--░░··········██████······████████
   Desalojos: t=1 A (4) a B (5); t=9 A (2) a B (4); t=18 B (3) a C (4).
   Fines: A=11, B=21, C=25.
```

### 1.2 Ejercicio extra 3

```
     0         5         10        15        20        25        30
     |.........|.........|.........|.........|.........|.........|....
A      ████░░██████████
B      ······················████████████████████░░░░░░░░░░██████████
C    ██····██░░░░······██████

t=1 A (prioridad 1) desaloja a C (2). t=3 A va a E/S → C (2) antes que B (3).
t=4 C va a E/S y A vuelve → A. t=9 A termina → C (2) antes que B. t=12 B.
Fines: A=9, C=12, B=32.
```

### 1.2 Ejercicio extra 4

```
a) RR, Q = 3
     0         5         10        15        20
     |.........|.........|.........|.........|......
A    ████░░··██████··██████
B      ··████░░░░░░········██████········██
C          ········██░░░░··············██░░····████
D                      ··········██████····████
   t=7: A agota el quantum y B vuelve de E/S → A va antes que B en la cola.

b) VRR, Q = 3
     0         5         10        15        20
     |.........|.........|.........|.........|......
A    ████░░··██··██████····████
B      ··████░░░░░░····██··············██████
C          ····██--░░░░··██░░··██············██
D                      ··········██████········████
   t=4: A vuelve de E/S con Q' = 3 − 2 = 1 a la cola auxiliar → ejecuta 1 y baja.
   t=9: B vuelve con Q' = 1 → ejecuta antes que A, C y D. t=10: C con Q' = 2.
```

### 1.2 Ejercicio extra 5

```
1. Necesita conocer (o estimar) la duración de la próxima ráfaga, que no se sabe.
2. Hay que recalcular el RR de todos los listos en cada decisión: overhead.
3. Es sin desalojo: un proceso con ráfaga larga retiene la CPU y los demás esperan
   (peor tiempo de respuesta, no sirve para sistemas interactivos).
```

### 1.2 Autoevaluación

```
1. En RR, el I/O bound usa poco de su quantum, se bloquea y al volver va al final de
   la cola, detrás de los CPU bound que usan el quantum entero. VRR le da una cola
   auxiliar más prioritaria para ejecutar lo que le sobró del quantum (Q' = Q − usado).

2. RR, Q = 2
     0         5
     |.........|......
P1   ████····██░░░░██
P2     ··████░░████
   t=2 P1 agota Q (2 de 3) → cola: P2, P1. P2 ejecuta 2 a 4 (termina la ráfaga,
   E/S de 4 a 5). P1 ejecuta 4 a 5 y va a E/S hasta 7. t=5 P2 vuelve y ejecuta
   5 a 7. t=7 P1 vuelve y ejecuta 7 a 8.
   Retorno: P1 = 8 − 0 = 8;  P2 = 7 − 1 = 6.
```

### 1.3 Ejercicio guiado

```
Paso 1: t=0 están P1 (cola 0), P4 y P5 (cola 2) → ejecuta P1. t=2 P1 agota Q=2 y
  vuelve al final de la cola 0; sigue siendo el único de la cola 0 → ejecuta P1 (2 a 3).

Paso 2: t=3 P1 pide E/S (3 a 12). Cola 1: P2, P3 → P2 ejecuta 3 a 5.
  t=5 P2 agota Q → cola 1: P3, P2 → P3 ejecuta 5 a 7.

Paso 3: t=7 P3 agota Q → cola 1: P2, P3 → P2 ejecuta 7 a 8 (le quedaba 1).
  t=8 P2 pide E/S, pero el dispositivo lo tiene P1 hasta 12 → espera; E/S de 12 a 16.
  P3 ejecuta 8 a 9 y termina.

Paso 4: t=9 solo cola 2: P4 ejecuta 9 a 11, P5 11 a 13 (RR, Q=2).

Paso 5: t=12 P1 vuelve a la cola 0, pero es sin desalojo entre colas: P5 termina su
  quantum (13). t=13 ejecuta P1 (13 a 15) y termina.

Paso 6: t=15 P4 (15 a 16, termina). t=16 P2 vuelve a la cola 1 → P2 16 a 19 (el
  quantum vence en 18 pero su cola está vacía) y termina. P5 19 a 20 y termina.
     0         5         10        15        20
     |.........|.........|.........|.........|
P1   ██████░░░░░░░░░░░░░░░░░░··████
P2     ····████····██--------░░░░░░░░██████
P3       ······████··██
P4   ··················████········██
P5   ······················████············██
   Fines: P3=9, P1=15, P4=16, P2=19, P5=20.
```

### 1.3 Ejercicio extra 1

```
     0         5         10        15        20        25
     |.........|.........|.........|.........|.........|..
P1   ████████░░░░░░··██████████
P2     ··························██----░░████····██
P3   ································██············██··██
P4       ····████--░░░░░░░░░░··██░░░░░░██
P5   ············████··············██----░░··████░░░░██
Fines: P1=13, P4=18, P2=23, P5=25, P3=26.
Ojo en t=12: P1 agota su quantum de 4 y P4 vuelve de E/S, los dos a la cola 0;
primero el de fin de quantum → P1 sigue (le queda 1).
```

### 1.3 Ejercicio extra 2

```
     0         5         10        15        20        25
     |.........|.........|.........|.........|.........|......
P1   ████········██----------░░░░░░······████
P2   ····██░░░░░░░░░░░░░░██
P3     ····████····████------------░░░░░░░░░░░░░░░░████████
P4       ······██--------░░░░████████████····██████········██
Fines: P2=11, P1=20, P3=27, P4=28.
t=5 P3 agota Q=2 y baja a RR4. t=12 P4 (en RR Q=2) agota Q en 14 y baja a RR4.
t=18 P4 agota Q=4 y baja a FIFO → ejecuta P1. t=23 P3 vuelve de E/S a RR2 y
desaloja a P4 (FIFO).
```

### 1.3 Ejercicio extra 3

```
Hay que definir: cuántas colas, el algoritmo de cada una, a qué cola entran los
nuevos, el criterio para pasar de una cola a otra y el algoritmo entre colas (si
desaloja o no). Con feedback, el que agota el quantum baja: los CPU bound lo agotan
y se hunden; los I/O bound se bloquean antes, no bajan y vuelven arriba, así que
reciben la CPU rápido.
```

### 1.3 Autoevaluación

```
1. Sin realimentación, cada proceso queda siempre en su cola; con realimentación
   cambia de cola según su uso de CPU (baja si agota el quantum). Definir: nº de
   colas, algoritmo de cada una, cola de entrada, criterio de cambio y algoritmo
   entre colas.

2.   0         5
     |.........|
P1   ██··██··██
P2     ██░░██
   t=0 P1 (RR) ejecuta 1 y agota Q → FIFO. t=1 P2 (RR) ejecuta 1 y va a E/S hasta 3.
   t=2 P1 (FIFO) ejecuta. t=3 P2 vuelve a RR y desaloja a P1 → P2 ejecuta 3 a 4 y
   termina. P1 sigue 4 a 5 y termina. Fines: P2=4, P1=5.
```

### 1.4 Ejercicio guiado

```
Paso 1: K2 ejecuta de 2 a 8 (en t=5 vence su quantum, pero K1 vuelve de E/S en el
  mismo instante y el fin de quantum va primero en la cola). De 2 a 5 ejecuta U1,
  el único ULT. En t=5 U1 ya ejecutó 3 con estimación 1: le resta 1 − 3 < 0 (≈ 0).

Paso 2: U2 llega con estimación 4 > estimación restante de U1 → no debería desalojar.
  El error está a partir del instante 5: U2 desaloja a U1, pero tendría que seguir U1.
  (Pudo ser una confusión con las estimaciones.)

Paso 3: U1, 2ª ráfaga: EST = 4·α + 1·(1 − α) = 1 + 3α

Paso 4: U2, 2ª ráfaga: EST = 3·α + 4·(1 − α) = 4 − α;
  en t=13 ya ejecutó 2 → le resta 2 − α

Paso 5: U1 desaloja a U2 si 1 + 3α < 2 − α → 4α < 1 → α < 0,25.
  α tiende a 0: se le da más peso a la estimación anterior. Con α = 0: U1 = 1, U2 = 2 ✓

Paso 6: c) Sin jacketing, la E/S de U2 (8 a 11) bloquea a todo K2. En t=10 K1 termina,
  pero U1 no puede ejecutar porque K2 está bloqueado: la CPU queda ociosa.
  El Gantt cambia a partir del instante 10.
```

### 1.4 Ejercicio extra 1

```
a) Para el SO hay 3 KLT: KLT1.1, KLT1.2 y P2 (con sus dos ULTs). Un solo dispositivo.
              0         5         10        15
              |.........|.........|.........|....
KLT1.1        ████  ██--░░    ████    ████    ██
KLT1.2            ██░░░░  ██
P2:ULT2.1             ████  ██░░    ██    ██
P2:ULT2.2                       ██░░      ██

   t=2  KLT1.1 agota Q y llega P2 → cola: KLT1.2, KLT1.1, P2.
   t=4  KLT1.1 pide E/S; el dispositivo lo tiene KLT1.2 hasta 5 → espera.
   t=6  P2 agota Q y KLT1.1 vuelve de E/S: primero el fin de quantum.
   t=8  ULT2.1 (sin jacketing) pide E/S → se bloquea todo P2.
   t=10 la biblioteca (FIFO) elige ULT2.2 (esperaba desde 3) antes que ULT2.1.
   t=11 ULT2.2 pide E/S con jacketing → P2 sigue con ULT2.1.
   Fines: KLT1.2=7, ULT2.1=15, ULT2.2=16, KLT1.1=17.

b) (resolución propia) En t=6. Como KLT, ULT2.2 entra solo a la cola del SO al
   llegar (t=3) y queda antes que KLT1.2, que vuelve de E/S en 5: en t=6 ejecuta
   ULT2.2 en lugar de KLT1.2.

c) (resolución propia, suponiendo que la biblioteca de P1 también es FIFO) En t=2.
   P1 sería un solo KLT: en t=2 vence su quantum y llega P2; el fin de quantum va
   primero en la cola, así que P1 vuelve a ejecutar, y como la biblioteca no se
   entera del quantum del SO, sigue ULT1.1 (su 3ª unidad). Antes, en t=2 ejecutaba
   KLT1.2 como hilo aparte.
```

### 1.4 Ejercicio extra 2

```
(resolución propia)
a) SO: VRR con Q = 2. Se ve en los KLT que vuelven de E/S sin haber usado todo el
   quantum: ejecutan solo lo que les sobró y antes que los de la cola común.
   t=3: KA volvió de E/S con Q' = 2 − 1 = 1 → ejecuta 1 sola unidad (RR le daría 2).
   t=9: KA vuelve con Q' = 1 y ejecuta antes que KB, que esperaba desde 6.
   t=15: KB vuelve con Q' = 1 y ejecuta antes que KC y KA.

b) Biblioteca de KA: HRRN (replanifica cuando termina una E/S o un ULT).
   t=0:  los tres tienen RR = 1 (W = 0): empate; eligió UA2, la ráfaga más corta.
   t=3:  UA1 (4+3)/4 = 1,75   UA2 (1+1)/1 = 2   UA3 (2+3)/2 = 2,5  → UA3 ✓
         (SJF elegiría UA2: descartado)
   t=9:  UA1 (4+9)/4 = 3,25   UA2 (1+7)/1 = 8   UA3 (2+1)/2 = 1,5  → UA2 ✓
         (FIFO elegiría UA1: descartado)
   t=13: UA1 (4+13)/4 = 4,25  UA3 (2+5)/2 = 3,5 → UA1 ✓

c) Biblioteca de KC: hay pocas decisiones. En t=1 elige UC2 (empatan en ráfaga 2) y
   en t=7, al volver UC2 de su E/S, sigue UC2 aunque UC1 espera desde 1. Eso cumple
   prioridades (UC2 más prioritario), o cualquier algoritmo si la E/S de UC2 la
   maneja el SO directamente (entonces sigue el mismo ULT, sin replanificar).
   FIFO, SJF y HRRN elegirían UC1 en t=7 si la biblioteca replanificara.

d) Con jacketing, la E/S de un ULT no bloquea al KLT: en t=1, KA seguiría con otro
   ULT (UA3 o UA1) en lugar de ceder la CPU a KC. El Gantt cambia desde t=1.

e) No. La CPU está ocupada todo el tiempo, de 0 a 22, y la suma de las ráfagas de
   CPU es 22: con un solo procesador, ningún algoritmo termina antes.
```

### 1.4 Ejercicio extra 3

```
          0         5         10        15        20
          |.........|.........|.........|.........|..
A:UA1         ██████--░░░░░░░░    ██
A:UA2     ████░░░░░░░░              ████
B1                  ████████--░░░░      ████
B2                          ████--░░░░░░    ████
C                               ██------░░      ████

La primera diferencia es en t=2: A2 pide disco y, con jacketing, A sigue con A1
(2 a 5) en lugar de bloquearse. En t=12 la biblioteca elige A1 (ráfaga 1) antes que
A2 (2). Todo termina en 21, contra 23 sin jacketing.
```

### 1.4 Autoevaluación

```
1. El jacketing convierte la E/S bloqueante de un ULT en no bloqueante: la biblioteca
   bloquea solo a ese ULT y el KLT sigue con otro. Resuelve que una E/S de un ULT
   bloquee a todo el proceso. Ventaja de los ULT: menos overhead (cambian sin pasar
   por el SO). Ventaja de los KLT: paralelismo real y un hilo bloqueado no frena a
   los otros.

2.   0         5
     |.........|..
P:U1 ██░░░░░░    ██
P:U2         ████
K1     ████
   t=0 P ejecuta U1 (1). t=1 U1 pide E/S sin jacketing → se bloquea todo P (hasta 4);
   U2 no puede ejecutar. K1 ejecuta 1 a 3 y termina. CPU ociosa de 3 a 4.
   t=4 P vuelve; la biblioteca (FIFO) elige U2 (esperaba desde 0) → U2 4 a 6,
   después U1 6 a 7.
```
