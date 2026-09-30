# Capítulo 3: Deadlock (clase 4)

## 3.1 Condiciones y estrategias ★★★☆☆ (estimado)

Temas en Lumen: `u4-deadlock-condiciones-grafo-asignacion`, `u4-estrategias-tratar-deadlocks`

No hay parciales con fecha donde se conozca este tema, así que las estrellas son una estimación. En el final del 20/02/2024 aparece como verdadero o falso, y la "Práctica avanzada 1er parcial" tiene dos ejercicios que combinan deadlock con sincronización (bloque 3.2).

### 1. Conceptos

**Deadlock (interbloqueo).** Un conjunto de procesos está en deadlock cuando cada uno espera un evento que solo puede producir otro proceso del conjunto. Ninguno avanza, nunca terminan y los recursos quedan tomados.

```
      asignado            solicita
  R1 ─────────→ P1 ─────────────→ R2
  ↑                                │
  │ solicita                       │ asignado
  P2 ←─────────────────────────────┘
```

**Starvation y livelock.** No son lo mismo que deadlock:
- **Inanición (starvation):** un proceso espera indefinidamente porque siempre le ganan otros, pero el sistema avanza.
- **Livelock:** los procesos no progresan, pero **siguen ejecutando** (por ejemplo, con espera activa o pedidos no bloqueantes que se reintentan). Consumen CPU y es más difícil de detectar. En el deadlock, en cambio, están bloqueados y no usan CPU.

**Recursos.** Pueden ser **reutilizables** (memoria, archivos, semáforos: se piden y se devuelven) o **consumibles** (mensajes, señales: se producen y se consumen). Pueden tener varias instancias, y cualquiera de ellas sirve igual. Se piden y se liberan con syscalls: `malloc`/`free`, `open`/`close`, `wait`/`signal`.

**Condiciones necesarias.** Para que haya deadlock tienen que darse **las cuatro a la vez**:
1. **Mutua exclusión:** al menos un recurso no se puede compartir.
2. **Retención y espera:** un proceso retiene un recurso mientras espera otro.
3. **Sin desalojo:** los recursos solo los libera voluntariamente quien los tiene.
4. **Espera circular:** hay un ciclo de procesos, cada uno esperando un recurso que tiene el siguiente.

**Grafo de asignación de recursos.** Los procesos son círculos y los recursos, cuadrados con un punto por instancia. Una flecha de proceso a recurso es un pedido; de recurso a proceso, una asignación. Si cada recurso tiene **una sola instancia**, un ciclo en el grafo **es** deadlock. Si hay varias instancias, el ciclo es necesario pero no alcanza: hay que verificar con el algoritmo de detección (bloque 3.3).

**Estrategias.** Hay cuatro formas de encarar el problema:
- **Ignorarlo** (algoritmo del avestruz): se asume que no pasa. Es lo que hacen los SO de uso general.
- **Prevención:** políticas definidas de antemano para que **nunca** se cumpla alguna de las cuatro condiciones.
- **Evasión:** ante cada pedido, se simula si asignarlo deja al sistema en un **estado seguro** (algoritmo del banquero, bloque 3.3). Los procesos declaran sus pedidos máximos.
- **Detección y recuperación:** se deja que ocurra, se detecta cada tanto y se recupera (matando procesos o desalojando recursos).

**Cómo prevenir cada condición.**

```
Mutua exclusión:   usar recursos compartibles cuando se pueda (abrir en solo lectura)
Retención y espera: pedir todo junto al principio, o liberar todo antes de pedir algo nuevo
Sin desalojo:      si un proceso pide algo ocupado, se le quita lo que tiene (o se le quita al que espera)
Espera circular:   numerar los recursos y pedirlos siempre en orden creciente
```

La más usada en los ejercicios es la última: si todos piden en el mismo orden, no puede cerrarse un ciclo.

**Comparación de estrategias.**

```
                  Prevención             Evasión                    Detección
Cuándo actúa      al pedir (política)    en cada asignación         cuando ya ocurrió
Flexibilidad      restringida            intermedia (declarar máx.) total
¿Puede haber DL?  no                     no                         sí
Overhead          poco                   alto (banquero cada vez)   intermedio (según frecuencia)
Uso de recursos   puede ser ineficiente  pesimista: niega pedidos   pierde trabajo al recuperar
```

**Recuperación.** Dos opciones:
- **Matar procesos:** todos los del deadlock (caro) o de a uno hasta que se resuelva (hay que elegir la víctima y volver a correr la detección).
- **Desalojar recursos:** hay que volver al proceso a un estado desde el que pueda seguir, y cuidar que no se elija siempre la misma víctima (inanición).

Para elegir víctima se mira la prioridad, cuánto ejecutó, cuántos recursos tiene y cuántos le faltan.

**Los tipos de pregunta que toman:**
1. **Verdadero o falso:** condiciones necesarias, livelock contra deadlock, ciclo en el grafo.
2. **Elegir estrategia** para un sistema descripto (y justificar por descarte).
3. **Mostrar que hay deadlock:** armar el ciclo y chequear las cuatro condiciones.
4. **Prevenir:** qué condición romper y cómo.

### 2. Ejemplo resuelto (Guía de deadlock, Ej 5)

> En un laboratorio de robótica, tres robots (R1, R2 y R3) deben completar una tarea. Cada uno necesita herramientas específicas, y hay una sola instancia de cada una: destornillador (D), llave inglesa (L) y soldador (S). R1 toma D y luego L; R2 toma L y luego S; R3 toma S y luego D. Cada herramienta la usa un robot a la vez, y los robots no sueltan una herramienta hasta obtener la segunda. a) Explique por qué los robots pueden quedar en deadlock y dibuje el ciclo de espera. b) ¿Cuáles de las cuatro condiciones necesarias están presentes? c) Si el deadlock ya ocurrió, ¿cómo podríamos detectarlo y solucionarlo con detección y recuperación?

Es del tipo 3. Hay una instancia de cada recurso, así que alcanza con encontrar un ciclo.

```
Paso 1: a) un orden que lleva al deadlock
  R1 toma D, R2 toma L, R3 toma S (cada uno su primera herramienta).
  Ahora R1 espera L (la tiene R2), R2 espera S (R3), R3 espera D (R1).

Paso 2: a) el ciclo
  R1 ──espera──→ L ──asignada──→ R2 ──espera──→ S ──asignada──→ R3
   ↑                                                             │
   └──────────asignada────── D ←──────────espera─────────────────┘

Paso 3: b) las cuatro condiciones
  Mutua exclusión: cada herramienta la usa un robot por vez.
  Retención y espera: cada robot tiene una y espera otra sin soltarla.
  Sin desalojo: no se les puede quitar la herramienta.
  Espera circular: R1 → R2 → R3 → R1.
  Están las cuatro → hay deadlock.

Paso 4: c) detección y recuperación
  Detección: armar el grafo de asignación y buscar ciclos (con una instancia por
  recurso, ciclo = deadlock).
  Recuperación: abortar un robot (por ejemplo, el que menos avanzó), que libera su
  herramienta; o quitarle la herramienta a uno para que otro termine.

Control: coincide con la resolución de la cátedra ✓
```

### 3. Ejercicio guiado (Guía de deadlock, Ej 2)

> Indique la o las mejores estrategias contra la posible ocurrencia de deadlock para cada caso. Justifique cada decisión, ya sea por ser la mejor opción o por descarte de las otras.
> a) Sistema usado en un puesto administrativo de una empresa, donde el operador usa planillas de cálculo, imprime documentos y navega por internet.
> b) Sistema computarizado de vuelo de aeronaves que tiene un grado alto de overhead debido a que el procesador no es muy potente.
> c) Base de datos transaccional usada en un sistema web de redes sociales, con cientos de usuarios programando aplicaciones para dicho sistema y una alta carga de transacciones en horas pico.
> d) Servidor de juegos online no gratuito con baja carga de usuarios, donde se desea no tener que devolverle el dinero a los usuarios a causa de un deadlock, pero se desea que los programadores de juegos tengan alta flexibilidad en la solicitud de los recursos.

Es del tipo 2. Para cada caso preguntate: ¿puede permitirse un deadlock? ¿Puede pagar overhead? ¿Necesita flexibilidad en los pedidos?

```
Paso 1: a) puesto administrativo. ¿Es grave un deadlock? ¿Qué estrategia?
  → ________

Paso 2: b) sistema de vuelo. ¿Puede haber deadlock? ¿Puede correr el banquero?
  → ________

Paso 3: c) base de datos con mucha carga. ¿Por qué no evasión?
  → ________

Paso 4: d) juegos pagos con poca carga y flexibilidad. ¿Qué estrategia?
  → ________
```

### 4. Práctica

#### Ejercicio extra 1: ¿deadlock o livelock? (Guía de deadlock, Ej 3)

> Siendo administrador de un sistema financiero, lo llaman a las 3 a. m.: un conjunto A de procesos lleva ejecutando mucho más de lo normal y se sospecha que están bloqueados. Pronto empieza el conjunto B, que tiene que estar listo a primera hora. El conjunto B usa recursos distintos de A, salvo el único procesador. El resultado de A se usa recién la semana que viene. Usted pregunta si es deadlock o livelock; el operador responde "al parecer es un XXXX" y usted dice: "entonces no hay nada de qué preocuparse, mañana lo arreglamos". ¿Cuál fue la respuesta del operador? Justifique.

#### Ejercicio extra 2: recursos al azar (Guía de deadlock, Ej 1)

> N procesos comparten recursos (una sola instancia de cada uno) y ejecutan:
>
> ```
> while(true) {
>   t_buffer rec_id[3] = get_recursos(); // devuelve al azar tres IDs de recursos
>   syscall_pedir(rec_id[0]);            // bloqueante si el recurso no está disponible
>   syscall_pedir(rec_id[1]);
>   syscall_pedir(rec_id[2]);
>   usar_recursos(rec_id);
>   syscall_devolver(rec_id[0]); syscall_devolver(rec_id[1]); syscall_devolver(rec_id[2]);
> }
> ```
>
> a) Demuestre que los procesos podrían quedar en deadlock. b) Proponga una solución para prevenirlo usando semáforos. c) Proponga una solución para prevenirlo sin usar soporte del sistema operativo (ni modificar el pseudocódigo del recuadro).

#### Ejercicio extra 3: teoría (final del 20/02/2024, teoría 1)

> Verdadero o falso, justificando: "Si un recurso puede ser accedido a la vez (en paralelo) por un conjunto de procesos, el mismo no puede ser causa de un deadlock entre ellos, pero sí de un livelock."

### 5. Cierre

**Fórmulas**

```
Condiciones (las 4 a la vez): mutua exclusión, retención y espera, sin desalojo, espera circular
Una instancia por recurso: ciclo en el grafo ⇔ deadlock.   Varias instancias: ciclo es necesario, no suficiente
Prevenir espera circular: pedir en orden creciente.   Retención y espera: pedir todo junto
Deadlock: bloqueados, no usan CPU.   Livelock: ejecutan sin avanzar, usan CPU.   Starvation: el sistema avanza, uno no
```

**Trampas**
- **Confundir deadlock con starvation.** En la inanición el resto avanza; en el deadlock, el conjunto entero está trabado.
- **Decir que un ciclo siempre es deadlock.** Solo si cada recurso tiene una instancia.
- **Olvidar alguna condición.** Tienen que estar las cuatro; alcanza con romper una para prevenir.
- **Decir que un recurso compartible puede causar livelock.** Sin mutua exclusión no hay ni deadlock ni livelock.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) Nombrá las cuatro condiciones necesarias y explicá cómo se previene la espera circular.
2. (Pregunta) ¿Qué diferencia hay entre deadlock, livelock e inanición? ¿En cuál los procesos consumen CPU?

## 3.2 Deadlock en código con semáforos ★★★★☆ (estimado)

Temas en Lumen: `u4-deadlock-condiciones-grafo-asignacion`, `u4-semaforos-espera-activa-bloqueo`

Es la forma en que suele aparecer en la práctica: un pseudocódigo con semáforos donde el orden de los wait, junto con el planificador, lleva a un deadlock. Dos de los seis ejercicios de la "Práctica avanzada 1er parcial" y tres de la guía de deadlock son de este tipo.

### 1. Conceptos

**De dónde sale el deadlock.** Dos procesos piden los mismos semáforos en **distinto orden**, y el planificador los corta justo entre un wait y el otro:

```
mutexX = 1, mutexY = 1
P1: wait(X); ...; wait(Y); ...        P2: wait(Y); ...; wait(X); ...
       ↑ corte                               ↑ corte
P1 tiene X y espera Y; P2 tiene Y y espera X → deadlock
```

**El planificador importa.** Con un algoritmo **con desalojo** (RR, prioridades con desalojo), el corte puede caer entre los dos wait. Con uno **sin desalojo** en un monoprocesador, si los procesos no se bloquean por otra cosa, cada uno hace todos sus wait y signal seguidos y no hay deadlock. En un **multiprocesador**, en cambio, pueden ejecutar a la vez y el deadlock vuelve a ser posible.

**Cómo se resuelve un ejercicio.**
1. **Gantt:** se ejecuta línea por línea con el algoritmo y la duración de cada línea, anotando el valor de cada semáforo y quién lo tiene.
2. **Grafo de asignación** al final: quién tiene qué semáforo y quién espera cuál.
3. **Ciclo:** si hay un ciclo con semáforos mutex (una instancia), hay deadlock. Los procesos bloqueados que no están en el ciclo sufren inanición, pero no son parte del deadlock.
4. **Corrección:** pedir en el mismo orden (rompe la espera circular), o liberar un semáforo antes de pedir el otro (rompe la retención y espera), o cambiar a un planificador sin desalojo.

**Los tipos de ejercicio que toman:**
1. **Gantt con semáforos** y decidir si hay deadlock (con el grafo).
2. **Mostrar un orden de ejecución** que lleve a deadlock o a una condición de carrera.
3. **Corregir el pseudocódigo** para prevenirlo, respetando reglas (liberar lo que no se usa).
4. **Qué pasa** con otro planificador o con varios procesadores.

### 2. Ejemplo resuelto (Guía de deadlock, Ej 6)

> Un sistema monoprocesador usa Round Robin con Q = 3. Cada WAIT y SIGNAL emplea 1 UT de ejecución. S1 = 1 y S2 = 1. Hay 3 procesos en Ready, en el orden P1, P2, P3.
>
> ```
> P1              P2              P3
> WAIT(S1)        WAIT(S2)        WAIT(S1)
> CPU (2 UT)      CPU (3 UT)      CPU (2 UT)
> WAIT(S2)        WAIT(S1)        WAIT(S2)
> SIGNAL(S1)      SIGNAL(S2)      CPU (1 UT)
> CPU (2 UT)      CPU (1 UT)      SIGNAL(S1)
> SIGNAL(S2)      SIGNAL(S1)      SIGNAL(S2)
> ```
>
> 1) ¿Están los procesos en deadlock? Realice el Gantt y el grafo de asignación para justificar. 2) Proponga una modificación para prevenir el deadlock, si lo hay. 3) ¿Ocurriría con un algoritmo sin desalojo? ¿Y en un multiprocesador?

Es del tipo 1 y 4. P1 y P2 piden S1 y S2 en orden inverso: hay que ver si el quantum los corta entre los dos wait.

```
Paso 1: t=0 a 3, ejecuta P1
  t=0 WAIT(S1) → S1 = 0, lo tiene P1.  t=1-2 CPU.  t=3 vence el quantum.

Paso 2: t=3 a 6, ejecuta P2
  t=3 WAIT(S2) → S2 = 0, lo tiene P2.  t=4-5 CPU (2 de 3).  t=6 vence el quantum.

Paso 3: t=6, ejecuta P3
  WAIT(S1): lo tiene P1 → P3 se bloquea.

Paso 4: t=7, ejecuta P1
  WAIT(S2): lo tiene P2 → P1 se bloquea (con S1 tomado).

Paso 5: t=8, ejecuta P2
  t=8 CPU (la 3ª unidad).  t=9 WAIT(S1): lo tiene P1 → P2 se bloquea (con S2 tomado).
  Los tres quedan bloqueados.

Paso 6: Gantt (después de su última unidad, cada uno queda bloqueado)
     0         5         10
     |.........|.........|
P1   ██████········██
P2   ······██████····████
P3   ············██

Paso 7: grafo
  P1 ──tiene── S1 ←──espera── P3
  P1 ──espera─→ S2 ──tiene──→ P2 ──espera─→ S1
  Ciclo P1 → S2 → P2 → S1 → P1, con una instancia de cada semáforo → DEADLOCK.
  P3 no retiene nada: no forma parte del deadlock, pero queda esperando (inanición).

Paso 8: 2) prevención
  Que todos pidan en el mismo orden (S1 y después S2) rompe la espera circular.
  O liberar el primer semáforo antes de pedir el segundo (P1: SIGNAL(S1) antes de
  WAIT(S2)), si la sección no necesita los dos a la vez: rompe retención y espera.

Paso 9: 3) sin desalojo y multiprocesador
  Sin desalojo, cada proceso hace todos sus WAIT y SIGNAL sin que lo corten: no hay
  deadlock. En un multiprocesador pueden ejecutar a la vez: sí puede haberlo.

Control: coincide con la resolución de la cátedra (deadlock P1-P2, P3 en inanición) ✓
```

### 3. Ejercicio guiado (Guía de deadlock, Ej 4)

> Un sistema monoprocesador usa Round Robin con Q = 2. Hay 2 procesos en Ready, P1 y P2, que comparten dos recursos protegidos por semáforos mutexX y mutexY. Cada línea demora una unidad de tiempo.
>
> ```
> P1                  P2
> Wait(mutexX);       Wait(mutexY);
> A++;                B++;
> Wait(mutexY);       Wait(mutexX);
> B++;                A++;
> Signal(mutexY);     Signal(mutexX);
> Signal(mutexX);     Signal(mutexY);
> ```
>
> a) Explique cómo estos procesos pueden quedar en deadlock. b) Proponga una solución para evitarlo sin modificar el orden del pseudocódigo. c) Modifique el pseudocódigo de uno de los procesos para eliminar el riesgo y justifique.

Es del tipo 1 y 3. Hacé el Gantt con Q = 2, anotando quién tiene cada mutex.

```
Paso 1: t=0 y 1, ¿qué ejecuta P1 y qué tiene al vencer el quantum?
  → ________

Paso 2: t=2 y 3, ¿qué ejecuta P2 y qué tiene?
  → ________

Paso 3: t=4 y 5, ¿qué pasa con cada uno? ¿Cuál es el ciclo?
  → ________

Paso 4: b) sin tocar el código, ¿qué se puede cambiar?
  → ________

Paso 5: c) el nuevo código de P2 y qué condición rompe
  → ________
```

### 4. Práctica

#### Ejercicio extra 1: prioridades y semáforos (Práctica avanzada 1er parcial, "¿Es o no es?")

> Se ejecutan 3 procesos planificados por prioridades con desalojo (a menor número, mayor prioridad). Semáforos: A = 1, B = 1, C = 1. Cada línea consume dos unidades de tiempo, y wait y signal se consideran atómicas. Los procesos llegan a ready en: P1 → t0, P3 → t3, P2 → t5.
>
> ```
> Proceso 1 (prioridad 10)   Proceso 2 (prioridad 5)   Proceso 3 (prioridad 1)
> WAIT(A)                    WAIT(C)                   WAIT(B)
> WAIT(B)                    WAIT(B)                   WAIT(A)
> WAIT(C)                    c = c + b                 a++
> a = b + c                  SIGNAL(C)                 b++
> SIGNAL(A)                  SIGNAL(B)                 SIGNAL(B)
> SIGNAL(B)                                            SIGNAL(A)
> SIGNAL(C)
> ```
>
> a) Realice el Gantt. b) Si queda en deadlock, realice el grafo de asignación e indique qué procesos participan. Si no, proponga un cambio en el pseudocódigo para que ocurra y demuestre cómo.

#### Ejercicio extra 2: Deadlock Empire (Práctica avanzada 1er parcial)

> Tres procesos concurrentes, sincronizados con semáforos. Valores iniciales: mutexAcum = 1, valorGenerado = 0, valorLeido = 2, acum = 0, ultValor = 0.
>
> ```
> Proceso A                  Proceso B                     Proceso C
> while(true) {              while(true) {                 while(true) {
>   wait(mutexAcum)            wait(valorLeido)              wait(valorLeido)
>   wait(valorGenerado)        ultValor = generarValor()     wait(mutexAcum)
>   acum += ultValor           signal(valorGenerado)         printf("Acumulado: %d", acum)
>   ultValor = 0             }                               signal(mutexAcum)
>   signal(valorLeido) x 2                                 }
>   signal(mutexAcum)
> }
> ```
>
> a) Indique un orden de ejecución, línea por línea, que genere un deadlock. b) Indique un orden de ejecución que muestre una condición de carrera sobre una sección crítica.

#### Ejercicio extra 3: puzzle de mutex (Práctica avanzada 1er parcial)

> Tres procesos acceden a variables compartidas sincronizados con mutex. No se generan inconsistencias, pero a veces dejan de avanzar.
>
> ```
> PROCESO 1               PROCESO 2               PROCESO 3
> while (TRUE) {          while (TRUE) {          while (TRUE) {
>   wait(mutex_a);          wait(mutex_a);          wait(mutex_b);
>   wait(mutex_b);          wait(mutex_b);          wait(mutex_d);
>   wait(mutex_c);          wait(mutex_c);          wait(mutex_a);
>   wait(mutex_d);          wait(mutex_d);          wait(mutex_c);
>   a = a * b;              a = a * b;              b = b + d;
>   a = a + c + d;          b = c * b;              b = a * b;
>   a = a + c + 1;          a = a * b;              b = c * b;
>   signal(a,b,c,d);        signal(a,b,c,d);        signal(a,b,c,d);
> }                       }                       }
> ```
>
> Proponga una solución moviendo, agregando o eliminando wait y signal para que: no haya deadlocks, y un recurso asignado se libere si la próxima operación no lo usa. Explique el motivo de cada semáforo eliminado y de cada wait y signal.

### 5. Cierre

**Fórmulas**

```
Mismo orden de wait en todos los procesos → no hay espera circular
Liberar antes de pedir el siguiente → no hay retención y espera
Monoprocesador sin desalojo (y sin bloqueos por otra cosa) → los wait/signal no se intercalan
Bloqueado fuera del ciclo = inanición, no deadlock
```

**Trampas**
- **Contar como parte del deadlock a un proceso que no retiene nada.** Está bloqueado, pero no en el ciclo.
- **Suponer que sin desalojo nunca hay deadlock.** Vale en monoprocesador si nadie se bloquea con un semáforo tomado; en multiprocesador no.
- **Corregir cambiando el orden sin revisar las reglas del enunciado.** Si pide liberar lo que no se usa, a veces hay que liberar y volver a pedir en orden.
- **Olvidar que las variables que solo se leen no necesitan mutex.** Sacar esos semáforos también reduce el riesgo.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Por qué con Round Robin dos procesos que piden dos mutex en orden inverso pueden quedar en deadlock, y con FIFO en un monoprocesador no?
2. (Ejercicio) RR con Q = 1, cada línea 1 UT, mutex M = 1 y N = 1. P1: wait(M); wait(N); signal(N); signal(M). P2: wait(N); wait(M); signal(M); signal(N). Ready: P1, P2. ¿Hay deadlock? Mostrá el Gantt. (material propio)

## 3.3 Algoritmo del banquero y detección ★☆☆☆☆ (estimado)

Temas en Lumen: `u4-estrategias-tratar-deadlocks`

Está en la teoría de la clase (se resuelve en el pizarrón), pero no hay ejercicios de la cátedra en el material relevado. Los ejemplos de este bloque son material propio, con el método de la clase.

### 1. Conceptos

**Estado seguro.** Un estado es seguro si existe **al menos un orden** (secuencia segura) en que todos los procesos pueden recibir lo que les falta hasta su máximo y terminar. Si el estado es seguro, no hay ni habrá deadlock. Si es inseguro, **podría** haberlo (no es seguro que lo haya).

**Estructuras.** Para evasión (banquero):

```
Vector de recursos totales       T
Matriz de asignados              Asig[P][R]
Matriz de máximos                Max[P][R]
Necesidad = Max − Asig           lo que le falta pedir a cada uno
Disponibles = T − Σ Asig
```

Para detección se usa lo mismo, pero con la matriz de **pedidos actuales** en lugar de la necesidad.

**Algoritmo de seguridad.** Se busca un proceso cuya necesidad sea menor o igual a lo disponible; se supone que termina y devuelve todo lo que tiene (Disponibles += Asig de ese proceso); se repite. Si terminan todos, el estado es seguro y el orden encontrado es una secuencia segura.

**Banquero ante un pedido.** Cuando un proceso pide:
1. ¿El pedido es menor o igual a su necesidad? Si no, es un error (pide más de lo declarado): se lo finaliza.
2. ¿Es menor o igual a lo disponible? Si no, espera.
3. Se **simula** la asignación (Disp −= pedido, Asig += pedido, Nec −= pedido) y se corre el algoritmo de seguridad. Si el estado es seguro, se asigna; si no, espera.

**Detección.** Con los pedidos actuales: se marca como que puede terminar a cada proceso cuyo pedido entra en lo disponible, y se le suman sus recursos a lo disponible. Los que quedan sin poder terminar están en deadlock. Cuesta recorrer las matrices, así que hay que decidir cada cuánto correrlo.

**Los tipos de ejercicio que toman:**
1. **¿El estado es seguro?** Encontrar una secuencia segura.
2. **¿Se le asigna el pedido?** Banquero con simulación.
3. **Detección:** qué procesos están en deadlock y cómo recuperarse.

### 2. Ejemplo resuelto (material propio, con el método de la clase)

> Un sistema tiene 9 instancias del recurso A y 6 del recurso B, y usa el algoritmo del banquero.
>
> ```
>        Asignados   Máximos
>          A  B       A  B
> P1       2  1       5  3
> P2       3  2       4  3
> P3       1  1       7  4
> ```
>
> a) ¿El estado es seguro? b) P3 pide (3, 1). ¿Se le asigna?

Es del tipo 1 y 2. Primero necesidad y disponibles; después la secuencia; al final, la simulación del pedido.

```
Paso 1: necesidad = máximos − asignados
  P1 (3, 2)    P2 (1, 1)    P3 (6, 3)

Paso 2: disponibles = totales − Σ asignados
  A: 9 − (2 + 3 + 1) = 3      B: 6 − (1 + 2 + 1) = 2   → (3, 2)

Paso 3: a) secuencia segura
  P1 necesita (3, 2) ≤ (3, 2) ✓ → termina, devuelve (2, 1) → Disp (5, 3)
  P2 necesita (1, 1) ≤ (5, 3) ✓ → devuelve (3, 2) → Disp (8, 5)
  P3 necesita (6, 3) ≤ (8, 5) ✓ → devuelve (1, 1) → Disp (9, 6)
  Estado seguro: <P1, P2, P3>.

Paso 4: b) P3 pide (3, 1)
  ¿≤ necesidad (6, 3)? ✓   ¿≤ disponibles (3, 2)? ✓

Paso 5: simular la asignación
  Disp = (0, 1)   Asig P3 = (4, 2)   Nec P3 = (3, 2)

Paso 6: seguridad del estado simulado
  P1 necesita (3, 2) > (0, 1) ✗   P2 (1, 1) > (0, 1) ✗   P3 (3, 2) > (0, 1) ✗
  Nadie puede terminar → estado inseguro.

Paso 7: respuesta
  No se asigna: P3 espera (se deshace la simulación). Hay recursos, pero darlos
  podría llevar a un deadlock.

Control: Σ asignados + disponibles = totales en cada paso (6 + 3 = 9; 4 + 2 = 6) ✓
```

### 3. Ejercicio guiado (material propio)

> Con el mismo estado inicial del ejemplo (antes del pedido de P3), P1 pide (1, 1). ¿Se le asigna?

Es del tipo 2. Seguí los mismos pasos: validar, simular y buscar una secuencia segura.

```
Paso 1: ¿el pedido es ≤ la necesidad de P1 y ≤ los disponibles?
  → ________

Paso 2: simulación: nuevos disponibles, asignados y necesidad de P1
  → ________

Paso 3: secuencia segura (o que no la hay)
  → ________

Paso 4: respuesta
  → ________
```

### 4. Práctica

#### Ejercicio extra 1: detección (material propio)

> Un sistema tiene 2 instancias de A y 3 de B, y usa detección y recuperación.
>
> ```
>        Asignados   Pedidos actuales
>          A  B        A  B
> P1       1  1        1  0
> P2       1  1        1  0
> P3       0  1        0  0
> ```
>
> a) ¿Hay deadlock? ¿Qué procesos participan? b) Proponga cómo recuperarse.

#### Ejercicio extra 2: teoría (material propio)

> Verdadero o falso, justificando: a) "Si el estado es inseguro, hay deadlock". b) "La evasión requiere que los procesos declaren de antemano sus pedidos máximos". c) "La detección tiene menos overhead que la evasión".

### 5. Cierre

**Fórmulas**

```
Necesidad = Máx − Asig        Disponibles = Totales − Σ Asig
Seguridad: buscar Nec_i ≤ Disp → Disp += Asig_i → repetir. Todos terminan → seguro
Pedido: ≤ Nec (si no, error) → ≤ Disp (si no, espera) → simular → seguro: asigna / inseguro: espera
Detección: igual, con pedidos actuales en lugar de necesidad; los que no terminan están en deadlock
```

**Trampas**
- **Decir que inseguro es deadlock.** Inseguro significa que podría haberlo; seguro, que no lo habrá.
- **Olvidar devolver lo asignado** al suponer que un proceso termina (Disp += Asig, no Disp += Nec).
- **Comparar el pedido solo con los disponibles.** Primero con la necesidad: si pide más de lo declarado, es un error.
- **Usar la necesidad en la detección.** La detección usa los pedidos actuales.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Qué es un estado seguro? ¿Qué diferencia hay entre el banquero y el algoritmo de detección?
2. (Ejercicio) Totales A = 5. Asignados: P1 = 2, P2 = 1. Máximos: P1 = 4, P2 = 3. ¿Es seguro? Si P2 pide 2, ¿se le asigna? (material propio)

## Respuestas del capítulo 3

### 3.1 Ejercicio guiado

```
Paso 1: a) Detección y recuperación (o no hacer nada). Un deadlock en un puesto
  administrativo no es grave: se reinicia la aplicación. No vale la pena el overhead
  ni las restricciones de prevenir o evadir.

Paso 2: b) Prevención. Un sistema de vuelo no puede permitirse un deadlock (descarta
  detección) y el procesador no aguanta el overhead de correr el banquero en cada
  pedido (descarta evasión). Se previene con políticas fijas (pedir en orden).

Paso 3: c) Detección y recuperación. Con cientos de usuarios programando
  aplicaciones no se pueden declarar los máximos ni imponer un orden (descarta
  evasión y prevención), y con alta carga el banquero sería muy caro. Perder o
  reintentar alguna transacción es tolerable.

Paso 4: d) Evasión. No se quiere que ocurra (descarta detección), pero se necesita
  flexibilidad (descarta prevención). Con poca carga, el overhead del banquero es
  aceptable.
```

### 3.1 Ejercicio extra 1

```
Deadlock. Los procesos de A están bloqueados: no usan CPU, y retienen recursos que
B no necesita, así que B puede ejecutar sin problemas. Si fuera un livelock, los
procesos de A seguirían ejecutando y consumiendo el único procesador, lo que sí
afectaría a B.
```

### 3.1 Ejercicio extra 2

```
a) Dos procesos obtienen, por ejemplo, P1: [1, 2, 3] y P2: [2, 1, 3]. P1 pide 1 y
   P2 pide 2; después P1 espera 2 (lo tiene P2) y P2 espera 1 (lo tiene P1). Hay
   mutua exclusión (una instancia), retención y espera, sin desalojo y espera
   circular → deadlock.
b) Un mutex (mutex_recursos = 1) alrededor de los tres syscall_pedir: los pedidos
   se hacen de a un proceso por vez, sin intercalarse.
c) Que get_recursos() devuelva los IDs ordenados: todos piden en orden creciente y
   no se puede formar la espera circular.
```

### 3.1 Ejercicio extra 3

```
Falso. Si el recurso se puede usar en paralelo, no hay mutua exclusión, que es una
condición necesaria tanto para el deadlock como para el livelock.
```

### 3.1 Autoevaluación

```
1. Mutua exclusión, retención y espera, sin desalojo y espera circular. La espera
   circular se previene numerando los recursos y haciendo que todos los pidan en
   orden creciente.
2. Deadlock: un conjunto de procesos bloqueados que se esperan entre sí. Livelock:
   no progresan, pero siguen ejecutando (consumen CPU). Inanición: un proceso espera
   indefinidamente mientras el resto avanza. Consumen CPU en el livelock.
```

### 3.2 Ejercicio guiado

```
Paso 1: t=0 Wait(mutexX) → lo tiene P1. t=1 A++. Vence el quantum con mutexX tomado.

Paso 2: t=2 Wait(mutexY) → lo tiene P2. t=3 B++. Vence el quantum con mutexY tomado.

Paso 3: t=4 P1 hace Wait(mutexY) → se bloquea. t=5 P2 hace Wait(mutexX) → se bloquea.
  Ciclo: P1 tiene X y espera Y; P2 tiene Y y espera X → deadlock (espera circular).

Paso 4: b) cambiar el planificador por uno sin desalojo (por ejemplo, FIFO): P1
  ejecuta todas sus líneas sin corte, libera los dos y después ejecuta P2.

Paso 5: c) P2 pide en el mismo orden que P1:
  Wait(mutexX); B++; Wait(mutexY); A++; Signal(mutexY); Signal(mutexX);
  (o, mejor, los dos wait al principio). Rompe la espera circular: el que tenga X
  va a poder conseguir Y.
```

### 3.2 Ejercicio extra 1

```
(resolución propia) Supuesto: como wait y signal son atómicas, una línea de 2 UT no
se interrumpe; el desalojo ocurre al terminar la línea en curso.

Un WAIT que encuentra el semáforo en 0 bloquea al proceso en ese momento.

a) t=0-1  P1 WAIT(A) → tiene A.
   t=2-3  P1 WAIT(B) → tiene B (P3 llega en t=3, pero la línea no se interrumpe).
   t=4    P3 (prioridad 1) desaloja a P1: WAIT(B) → B lo tiene P1 → P3 se bloquea.
   t=4-5  P1 WAIT(C) → tiene A, B y C (P2 llega en t=5).
   t=6    P2 (prioridad 5) desaloja a P1: WAIT(C) → lo tiene P1 → P2 se bloquea.
   t=6-11 P1: a = b + c, SIGNAL(A), SIGNAL(B) → se desbloquea P3, que recibe B.
   t=12   P3 desaloja a P1: WAIT(A) (libre), a++, b++, SIGNAL(B), SIGNAL(A), termina.
   Después P1 hace SIGNAL(C) → se desbloquea P2, que desaloja a P1 y termina
   (WAIT(B), c = c + b, SIGNAL(C), SIGNAL(B)). No hay deadlock: cuando P3 y P2
   piden, P1 ya tiene todo lo que necesita y lo libera.

b) Un cambio que lo produce: en P1, pedir A, C y B (en ese orden).
   P1 tiene A y C cuando llega P3; P3 toma B y espera A (la tiene P1); P2 espera C
   (la tiene P1); P1 pide B (la tiene P3) → ciclo P1 → B → P3 → A → P1: deadlock
   entre P1 y P3. P2 queda bloqueado esperando C, fuera del ciclo.
```

### 3.2 Ejercicio extra 2

```
(resolución propia)
a) C: wait(valorLeido) → 1; wait(mutexAcum); printf; signal(mutexAcum).
   C: wait(valorLeido) → 0; wait(mutexAcum); printf; signal(mutexAcum).
   C: wait(valorLeido) → se bloquea.
   A: wait(mutexAcum) → lo toma; wait(valorGenerado) → se bloquea (vale 0).
   B: wait(valorLeido) → se bloquea (vale 0).
   A espera a B, B espera que A haga signal(valorLeido), C espera lo mismo: nadie
   puede seguir → deadlock. (C se "comió" los dos valorLeido que eran de B.)

b) B: wait(valorLeido) → 1; ultValor = v1; signal(valorGenerado).
   A: wait(mutexAcum); wait(valorGenerado).
   B: wait(valorLeido) → 0; ultValor = v2   (pisa v1 antes de que A lo lea)
   A: acum += ultValor (suma v2); ultValor = 0 (borra v2).
   v1 se perdió: ultValor lo escribe B sin mutex mientras A lo lee y lo modifica.
   El resultado depende del orden → condición de carrera.
```

### 3.2 Ejercicio extra 3

```
(resolución propia)
Se eliminan mutex_c y mutex_d: c y d solo se leen (nadie los escribe), así que por
Bernstein no hace falta protegerlos. Quedan mutex_a y mutex_b, que se piden siempre
en el orden a → b (sin espera circular). Cuando la próxima línea no usa un recurso,
se libera; si después hay que volver a pedir a teniendo b, se suelta b y se piden
los dos en orden.

PROCESO 1                 PROCESO 2                 PROCESO 3
wait(mutex_a)             wait(mutex_a)             wait(mutex_b)
wait(mutex_b)             wait(mutex_b)             b = b + d
a = a * b                 a = a * b                 signal(mutex_b)
signal(mutex_b)           signal(mutex_a)           wait(mutex_a)
a = a + c + d             b = c * b                 wait(mutex_b)
a = a + c + 1             signal(mutex_b)           b = a * b
signal(mutex_a)           wait(mutex_a)             signal(mutex_a)
                          wait(mutex_b)             b = c * b
                          a = a * b                 signal(mutex_b)
                          signal(mutex_b)
                          signal(mutex_a)
```

### 3.2 Autoevaluación

```
1. Con RR el quantum puede vencer entre el primer y el segundo wait: cada uno queda
   con un mutex y esperando el otro (espera circular). Con FIFO en un monoprocesador,
   cada proceso ejecuta todos sus wait y signal sin que lo corten.

2.   0         5
     |.........|
P1   ██··██
P2   ··██··██
   t=0 P1 wait(M) → tiene M. t=1 P2 wait(N) → tiene N. t=2 P1 wait(N) → se bloquea.
   t=3 P2 wait(M) → se bloquea. Deadlock: P1 tiene M y espera N; P2 tiene N y espera M.
```

### 3.3 Ejercicio guiado

```
Paso 1: (1, 1) ≤ necesidad de P1 (3, 2) ✓ y ≤ disponibles (3, 2) ✓.

Paso 2: Disp = (2, 1)   Asig P1 = (3, 2)   Nec P1 = (2, 1)

Paso 3: P1 necesita (2, 1) ≤ (2, 1) ✓ → Disp (5, 3)
  P2 (1, 1) ≤ (5, 3) ✓ → Disp (8, 5)
  P3 (6, 3) ≤ (8, 5) ✓ → Disp (9, 6)
  Secuencia segura: <P1, P2, P3>.

Paso 4: el estado es seguro → se le asigna (1, 1) a P1.
```

### 3.3 Ejercicio extra 1

```
a) Disponibles = (2 − 2, 3 − 3) = (0, 0).
   P3 no pide nada → puede terminar y devuelve (0, 1) → Disp (0, 1).
   P1 pide (1, 0) > (0, 1) ✗   P2 pide (1, 0) > (0, 1) ✗
   P1 y P2 están en deadlock: cada uno tiene una A y espera la del otro.
b) Matar a uno de los dos (por ejemplo, el de menor prioridad o el que menos
   ejecutó): libera su A y el otro puede terminar. O desalojarle la A a uno, que
   tendrá que volver a un estado anterior.
```

### 3.3 Ejercicio extra 2

```
a) Falso: inseguro significa que puede haber deadlock según cómo se pidan los
   recursos; no que ya lo haya.
b) Verdadero: el banquero necesita la matriz de máximos para calcular la necesidad.
c) Depende, pero en general sí: la evasión corre el algoritmo en cada pedido; la
   detección, cada tanto (el overhead depende de la frecuencia elegida).
```

### 3.3 Autoevaluación

```
1. Un estado es seguro si hay un orden en que todos pueden conseguir lo que les falta
   hasta su máximo y terminar. El banquero (evasión) simula antes de asignar, con los
   máximos declarados; la detección se corre cada tanto con los pedidos actuales para
   ver si ya hay deadlock.

2. Disponibles = 5 − 3 = 2. Necesidad: P1 = 2, P2 = 2. P1 (2 ≤ 2) termina → Disp 4;
   P2 (2 ≤ 4) termina → seguro.
   P2 pide 2: ≤ necesidad y ≤ disponibles. Simulación: Disp = 0, Nec P2 = 0 → P2
   termina y devuelve 3 → Disp 3 → P1 (2 ≤ 3) termina. Seguro → se asigna.
```
