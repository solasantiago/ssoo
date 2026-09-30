# Capítulo 5: Memoria virtual (clase 6)

## 5.1 Paginación bajo demanda y fallos de página ★★★★☆ (estimado)

Temas en Lumen: `u5-memoria-virtual-paginacion-demanda`, `u5-fallo-pagina`, `u5-segmentacion-paginacion-demanda`

Las estrellas son una estimación: no hay parciales con fecha del 2do parcial. Los "Ejercicios de parcial" de memoria y el final del 20/02/2024 usan este bloque en todos sus ejercicios de memoria virtual (TLB, fallos de página, accesos).

### 1. Conceptos

**Memoria virtual.** No hace falta que todo el proceso esté en RAM: sus páginas pueden estar en memoria principal o en disco (swap), y se traducen en tiempo de ejecución. Se gana en tres cosas: entran más procesos (sube el grado de multiprogramación), un proceso puede ser más grande que la RAM, y es transparente para el programador (no hacen falta overlays).

**Paginación bajo demanda.** En lugar de mover procesos enteros, se mueven páginas, y solo cuando se necesitan ("swapping perezoso"). Cada entrada de la tabla de páginas tiene un bit de **presencia** (P): 1 si la página está en un marco, 0 si no.

```
Pág   Marco   P   U   M
 0      5     1   1   0     ← en RAM, en el marco 5, usada, sin modificar
 1      -     0   -   -     ← nunca se cargó
 2      2     0   -   -     ← estuvo en el marco 2, pero la reemplazaron
```

**Fallo de página (page fault, PF).** Si se referencia una página con P = 0, la MMU lanza una interrupción y el SO:
1. Verifica que la dirección sea válida (que esté en el espacio del proceso). Si no, finaliza el proceso o le avisa del error.
2. Busca un marco libre. Si no hay, elige una **víctima** con el algoritmo de sustitución (bloque 5.2) y, si la víctima tiene M = 1, la escribe en disco.
3. Pide la lectura de la página al disco (el proceso queda bloqueado: es E/S).
4. Cuando termina, actualiza la tabla (P = 1, marco) y la TLB.
5. Reinicia la instrucción que causó el fallo.

Ojo: un fallo de página **siempre** lee el disco al menos una vez (para traer la página); si la víctima estaba modificada, escribe otra vez.

**Bits de la tabla.** Además de P y el marco: **uso** (U), que se pone en 1 cuando se referencia la página, y **modificado** (M, "dirty"), que se pone en 1 cuando se escribe. Si una víctima tiene M = 0, no hace falta escribirla en disco: su copia en swap está al día.

**Traducción con memoria virtual.** El camino completo de una referencia:

```
DL → ¿está en la TLB? ── hit ──→ DF
            │ miss
            ↓
     tabla de páginas: ¿P = 1? ── sí ──→ se agrega a la TLB → DF
            │ no
            ↓
     fallo de página: ¿marco libre? no → víctima (si M = 1, se escribe) → se lee la página
     → P = 1, se agrega a la TLB → se reinicia la instrucción
```

**Contar accesos.** En la guía, cada referencia cuenta así: con **hit** en la TLB, 1 acceso a la TLB y 1 a memoria (el dato); con **miss**, 2 accesos a la TLB (antes y después de cargar la entrada) y 2 a memoria (tabla y dato); y cada fallo de página suma un acceso a disco (más otro si la víctima estaba modificada).

**Asignación y sustitución.** Dos decisiones independientes:
- **Asignación fija o dinámica:** si cada proceso tiene siempre la misma cantidad de marcos o puede ganar y perder.
- **Sustitución local o global:** si la víctima sale de los marcos del mismo proceso o de cualquiera.

**Los tipos de ejercicio que toman:**
1. **Traducir direcciones** con memoria virtual (con fallo de página o error de dirección).
2. **Contar accesos** a TLB, memoria y disco para una secuencia de referencias.
3. **Bits y tamaños** con memoria virtual (el proceso puede ser más grande que la RAM).
4. **Teoría:** pasos de la atención de un fallo de página; qué pasa con M = 0 o M = 1.

### 2. Ejemplo resuelto (Guía de memoria, Ej 10)

> Dos procesos generan las siguientes referencias (números de página):
>
> ```
> P1: 10 11 0 3 4 11 0 3 4 11 0 3 4
> P2: 10 11 12 13 14 15 16 17 18
> ```
>
> Cada proceso tiene 4 marcos, la sustitución es LRU, y hay una TLB de 4 entradas con sustitución FIFO. a) En cada caso, ¿cuántos accesos a la TLB, a memoria y a disco se producen? b) ¿En alguno de los casos sirve tener una caché? Justifique (tenga en cuenta el concepto de localidad).

Es del tipo 2. Todas las referencias son lecturas. Se cuenta con la convención de la guía: hit = 1 TLB + 1 memoria; miss = 2 TLB + 2 memoria; cada fallo, 1 disco.

```
Paso 1: P1, marcos (LRU, 4)
  10, 11, 0, 3 → 4 fallos (marcos vacíos)
  4 → fallo, víctima 10 (la menos usada) → quedan 11, 0, 3, 4
  El resto (11 0 3 4 11 0 3 4) está en memoria → 5 fallos en total

Paso 2: P1, TLB (FIFO, 4)
  10, 11, 0, 3 → miss;  4 → miss, sale 10 → TLB: 11, 0, 3, 4
  Las 8 referencias siguientes son hits → 5 miss y 8 hits

Paso 3: P1, accesos
  TLB: 5 · 2 + 8 · 1 = 18    Memoria: 5 · 2 + 8 · 1 = 18    Disco: 5

Paso 4: P2
  Las 9 páginas son distintas: 9 fallos y 9 miss en la TLB
  TLB: 9 · 2 = 18    Memoria: 9 · 2 = 18    Disco: 9

Paso 5: b) localidad
  P1 tiene localidad: repite 4 páginas (11, 0, 3, 4), que entran en la TLB, y después
  de las primeras referencias todo es hit. A P2 la TLB no le sirve: nunca repite
  una página (sin localidad), todo es miss.

Control: coincide con la resolución de la cátedra (18, 18, 5 y 18, 18, 9) ✓
```

### 3. Ejercicio guiado (Guía de memoria, Ej 7 y Ej 5)

> 7) Un esquema de memoria virtual tiene páginas de 1024 bytes y la memoria física tiene 4 marcos. La tabla de páginas de un proceso es: página 0 → marco 3, página 1 → marco 1, página 4 → marco 2, página 6 → marco 0; las páginas 2, 3, 5 y 7 no están en memoria. ¿A qué direcciones físicas van las direcciones virtuales (en decimal) 0, 3728, 1024, 1025, 4099 y 7800?
> 5) Una máquina con memoria virtual tiene 128 KiB de RAM y páginas de 8 KiB. ¿Cuál sería el tamaño mínimo (en bits) de la dirección si queremos que un proceso pueda direccionar hasta 1 MiB?

Son del tipo 1 y 3. Para cada DL: página = DL / 1024 (parte entera), offset = resto.

```
Paso 1: 0 y 3728 → página, offset, ¿está? DF
  → ________

Paso 2: 1024 y 1025
  → ________

Paso 3: 4099 y 7800
  → ________

Paso 4: 5) ¿de qué depende el tamaño de la DL con memoria virtual? ¿Cuántos bits?
  → ________
```

### 4. Práctica

#### Ejercicio extra 1: segmentación paginada con TLB (Ejercicios de final de memoria, Ej 2)

> Un SO usa segmentación paginada con memoria virtual, punteros de 16 bits, marcos de 4 KB y una TLB de 4 entradas. Los procesos no pueden tener más de 4 segmentos; este proceso tiene solo estos tres:
>
> ```
> Segmento 0 (RW-)       Segmento 1 (--X)       Segmento 2 (R--)
> Marco  P  U            Marco  P  U            Marco  P  U
>   6    1  0              9    1  0              A    0  0
>   9    0  0              B    1  1              1    0  0
>  11    1  1              7    1  0              C    0  0
> (tiene más páginas)    (tiene más páginas)    (tiene más páginas)
>
> TLB: Dir B → marco 8; Dir 3 → marco 1 (el resto vacío)
> ```
>
> Indique las direcciones físicas que generarán las siguientes **escrituras**: 3C38h, FFACh, AA00h, sabiendo que el algoritmo de reemplazo es Clock, con reemplazo global y asignación dinámica.

#### Ejercicio extra 2: teoría (final del 20/02/2024, teoría 4)

> Verdadero o falso, justificando: "En un sistema con una alta tasa de TLB hits, es posible que un page fault no genere accesos a disco."

#### Ejercicio extra 3: teoría (material propio)

> a) Ordene los pasos de la atención de un fallo de página. b) ¿Por qué conviene elegir como víctima una página con M = 0? c) ¿Qué diferencia hay entre sustitución local y global?

### 5. Cierre

**Fórmulas**

```
Referencia: TLB hit → DF.  TLB miss → tabla: P = 1 → DF;  P = 0 → fallo de página
Fallo: validar → marco libre o víctima (si M = 1, escribirla) → leer de disco → P = 1 → reiniciar
Conteo (guía): hit = 1 TLB + 1 mem; miss = 2 TLB + 2 mem; fallo = +1 disco (+1 si la víctima tiene M = 1)
Con memoria virtual, la DL puede ser más grande que la DF
```

**Trampas**
- **Decir que un fallo de página puede no ir a disco.** Siempre lee la página faltante.
- **Olvidar la escritura de la víctima.** Si tenía M = 1, hay que escribirla antes de reemplazarla.
- **Confundir "no válida" con "no presente".** Fuera del espacio del proceso es un error; dentro pero con P = 0 es un fallo de página.
- **Con memoria virtual, limitar el proceso a la RAM.** El tamaño lo da la DL, no la memoria física.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) Enumerá los pasos de la atención de un fallo de página y qué cambia si la víctima tiene M = 1.
2. (Ejercicio) Páginas de 2 KiB. Tabla: página 0 → marco 4, página 1 → no presente, página 2 → marco 1. ¿Qué pasa con las DL 1500, 3000 y 4200? (material propio)

## 5.2 Algoritmos de sustitución de páginas ★★★★★ (estimado)

Temas en Lumen: `u5-algoritmos-reemplazo-paginas`, `u5-conjunto-residente-politicas-asignacion`

Es el ejercicio más frecuente del tema: los tres "Ejercicios de parcial" de memoria virtual de la cátedra y el de final piden aplicar o deducir un algoritmo de sustitución.

### 1. Conceptos

**Cómo se evalúan.** Se toma una secuencia de referencias (números de página) y una cantidad de marcos, y se cuentan los fallos de página. Los primeros fallos, con los marcos vacíos, son inevitables. Lo esperable es que con más marcos haya igual o menos fallos.

**FIFO.** La víctima es la página que **se cargó** hace más tiempo (cola, o el menor instante de carga). Es simple, pero puede sacar una página muy usada. Sufre la **anomalía de Belady**: para algunas secuencias, con más marcos hay **más** fallos.

**Óptimo.** La víctima es la página que **no se va a usar** por más tiempo (mirando el futuro). Da la mínima cantidad de fallos y no sufre Belady, pero no se puede implementar: sirve para comparar.

**LRU (Least Recently Used).** La víctima es la página **usada** hace más tiempo (el menor instante de última referencia). Usa el pasado reciente como aproximación del futuro. No sufre Belady. Es caro: hay que registrar cada referencia (instante de uso, o una pila donde cada página referenciada pasa al final).

**Clock (segunda oportunidad).** FIFO con un bit de uso, en una cola circular con un puntero. Al buscar víctima:

```
mientras U(puntero) = 1:  U = 0 y avanzar       (segunda oportunidad)
víctima = la del puntero (U = 0); se reemplaza y el puntero avanza al siguiente
Al cargar o referenciar una página: U = 1
```

**Clock modificado (mejorado).** Mira el par (U, M) para evitar escrituras a disco:

```
a) buscar (0, 0) dando una vuelta, SIN cambiar los U
b) si no hay, buscar (0, 1) dando una vuelta y poniendo U = 0 a las que pasa
c) si no hay, volver a a) (ahora todas tienen U = 0)
```

Al reemplazar, el puntero queda en el marco siguiente a la víctima. Si la víctima tenía M = 1, hay que escribirla en disco.

**Notación de las tablas.** En esta guía, cada columna es una referencia; `3*` es la página 3 con U = 1, y `>` marca dónde está el puntero **después** de esa referencia. F es fallo de página.

**Deducir el algoritmo.** Cuando dan una traza o una tabla con instantes de carga (TC), de última referencia (TUR) y bits, se prueba cada algoritmo con la víctima que eligió el sistema: FIFO elige el menor TC; LRU, el menor TUR; Clock, el primero con U = 0 desde el puntero; Clock modificado, el primer (0, 0). Se descartan los que habrían elegido otra.

**Los tipos de ejercicio que toman:**
1. **Contar fallos** con varios algoritmos para una secuencia y comparar.
2. **Referencias con direcciones:** pasar cada dirección a página, marcar lectura o escritura, aplicar el algoritmo y contar las escrituras a disco.
3. **Sustitución global** con varios procesos y un puntero compartido.
4. **Deducir el algoritmo** a partir de una traza o de la víctima elegida.

### 2. Ejemplo resuelto (Guía de memoria, Ej 8)

> Un proceso de 8 páginas ejecuta con memoria virtual, asignación fija de 4 marcos por proceso y alcance local. La memoria está inicialmente vacía. Determine el número de fallos de página para la secuencia 0, 1, 7, 2, 3, 2, 7, 1, 0, 3, 0, 2, 3, 1 con Óptimo, FIFO, LRU y Clock.

Es del tipo 1. Los primeros 4 fallos (0, 1, 7, 2) son inevitables en todos. Después, en cada fallo se aplica el criterio de la víctima.

```
Paso 1: Óptimo (la que no se usa por más tiempo)
  ref:   0  1  7  2  3  2  7  1  0  3  0  2  3  1
  fr0:   0  0  0  0  3  3  3  3  3  3  3  3  3  3
  fr1:   -  1  1  1  1  1  1  1  1  1  1  1  1  1
  fr2:   -  -  7  7  7  7  7  7  0  0  0  0  0  0
  fr3:   -  -  -  2  2  2  2  2  2  2  2  2  2  2
  PF:    F  F  F  F  F           F                   → 4 + 2 = 6
  (en ref 3 sale 0, que vuelve recién en la posición 9; en ref 0 sale 7, que no vuelve)

Paso 2: FIFO (la que se cargó primero)
  ref:   0  1  7  2  3  2  7  1  0  3  0  2  3  1
  fr0:   0  0  0  0  3  3  3  3  3  3  3  3  3  3
  fr1:   -  1  1  1  1  1  1  1  0  0  0  0  0  0
  fr2:   -  -  7  7  7  7  7  7  7  7  7  7  7  1
  fr3:   -  -  -  2  2  2  2  2  2  2  2  2  2  2
  PF:    F  F  F  F  F           F              F    → 4 + 3 = 7

Paso 3: LRU (la usada hace más tiempo)
  ref:   0  1  7  2  3  2  7  1  0  3  0  2  3  1
  fr0:   0  0  0  0  3  3  3  3  0  0  0  0  0  0
  fr1:   -  1  1  1  1  1  1  1  1  1  1  1  1  1
  fr2:   -  -  7  7  7  7  7  7  7  7  7  2  2  2
  fr3:   -  -  -  2  2  2  2  2  2  3  3  3  3  3
  PF:    F  F  F  F  F           F  F     F          → 4 + 4 = 8

Paso 4: Clock (U = 1 → segunda oportunidad)
  ref:   0    1    7    2    3    2    7    1    0    3    0    2    3    1
  fr0:   0*   0*   0*   0*>  3*   3*   3*   3*   3    3*   3*   3*   3*   3*
  fr1:   ->   1*   1*   1*   1>   1>   1>   1*>  0*   0*   0*   0*   0*   0*
  fr2:   -    ->   7*   7*   7    7    7*   7*   7>   7>   7>   7>   7>   1*
  fr3:   -    -    ->   2*   2    2*   2*   2*   2    2    2    2*   2*   2*>
  PF:    F    F    F    F    F                   F                        F   → 4 + 3 = 7
  (en ref 3 todas tienen U = 1: el puntero da la vuelta poniendo U = 0 y saca a 0)

Paso 5: comparación
  Óptimo 6 < FIFO 7 = Clock 7 < LRU 8. Acá LRU fue el peor: la secuencia no
  repite las páginas recientes.

Control: coincide con la resolución de la cátedra (6, 7, 8 y 7) ✓
```

### 3. Ejercicio guiado (Guía de memoria, Ej 9)

> Un procesador de 32 bits usa páginas de 8 KB, con paginación bajo demanda, asignación fija de 4 marcos por proceso y sustitución local. Un proceso de 159 KB tiene esta asignación:
>
> ```
> Puntero   Marco   Página   Uso   Modificado   Instante de referencia
>             1       14      1        1                28
>             3       17      1        0                 3
>             5       19      1        1                15
>   -->       8       --      -        -                --
> ```
>
> Las próximas referencias son: 100 (L), 122950 (E), 98306 (L), 139264 (E), 122880 (L), 155650 (E), 172100 (L), 100 (L). Para LRU y Clock modificado: a) indique el estado de las páginas luego de cada referencia, los fallos y las páginas escritas a disco; b) ¿cuál de los dos rinde mejor con esta secuencia? ¿Qué criterio usa?

Es del tipo 2. Primero pasá cada dirección a página (dividir por 8192) y verificá que sea válida: el proceso de 159 KB tiene páginas de la 0 a la 19.

```
Paso 1: páginas de cada referencia, y cuál es inválida
  → ________

Paso 2: LRU: víctimas, fallos y escrituras (usá los instantes de referencia)
  → ________

Paso 3: Clock modificado, referencias 1 a 3 (puntero en el marco 8)
  → ________

Paso 4: Clock modificado, referencias 4 a 7
  → ________

Paso 5: b) comparación y criterio
  → ________
```

### 4. Práctica

#### Ejemplo resuelto 2: sustitución global (Ejercicios de parcial de memoria, Ej 2)

> Un SO con 64 KB de memoria física usa paginación por demanda, Clock modificado y sustitución global. Todos los marcos están asignados a 4 procesos de 100 KB (páginas 0 a 12). Las tablas (solo las entradas con P = 1; U = uso, M = modificado) son:
>
> ```
> Proceso 1: pág 0 → marco 5 (U, M);  pág 1 → marco 2 (U)
> Proceso 2: pág 1 → marco 7 (-);     pág 2 → marco 4 (U)
> Proceso 3: pág 0 → marco 3 (M);     pág 2 → marco 6 (M);    pág 3 → marco 1 (U)
> Proceso 4: pág 3 → marco 0 (-)
> ```
>
> a) Indique la traza de ejecución para las lecturas P2 − 7800, P1 − 18010 y P4 − 83045, sabiendo que el puntero está en el marco 5. b) Indique el tamaño de página y de marco, y cuál fue la referencia inmediatamente anterior, sabiendo que la sentencia ejecutada fue "variable = 1".

Es del tipo 3. Hay 8 entradas presentes y toda la memoria está asignada: 8 marcos de 64 KB / 8 = 8 KB. Con eso se pasan las direcciones a páginas.

```
Paso 1: tamaño de página y marcos
  8 marcos en 64 KB → 8 KB = 8192 bytes

Paso 2: páginas de las referencias
  P2 − 7800  → pág 0 (P = 0 → fallo)
  P1 − 18010 → 18010 / 8192 = 2 → pág 2 (P = 0 → fallo)
  P4 − 83045 → 83045 / 8192 = 10 → pág 10 (P = 0 → fallo)

Paso 3: estado inicial (marco: página, U M), puntero en 5
  0: P4p3 00   1: P3p3 10   2: P1p1 10   3: P3p0 01
  4: P2p2 10   5: P1p0 11   6: P3p2 01   7: P2p1 00

Paso 4: P2 pág 0
  Busca (0,0) desde 5: 5 (1,1), 6 (0,1), 7 (0,0) ✓ → sale P2p1 (sin escribir)
  Marco 7 ← P2p0 (1,0). Puntero → 0.

Paso 5: P1 pág 2
  Busca (0,0) desde 0: 0 (0,0) ✓ → sale P4p3 (sin escribir)
  Marco 0 ← P1p2 (1,0). Puntero → 1.

Paso 6: P4 pág 10
  a) (0,0) desde 1: nadie (1 y 2 tienen U = 1; 3 y 6 tienen M = 1).
  b) (0,1) desde 1, bajando U: 1 → U = 0; 2 → U = 0; 3 (0,1) ✓ → sale P3p0,
     que tiene M = 1: se escribe en disco.
  Marco 3 ← P4p10 (1,0). Puntero → 4.
  Total: 3 fallos, 3 lecturas y 1 escritura.

Paso 7: b) referencia anterior
  "variable = 1" es una escritura: la última referencia puso U = 1 y M = 1. La única
  página con (1,1) es la página 0 del proceso 1: fue una escritura en P1, pág 0.

Control: coincide con la resolución de la cátedra (marcos 7, 0 y 3; escritura de P3p0) ✓
```

#### Ejercicio extra 1: deducir el algoritmo (Ejercicios de parcial de memoria, Ej 3)

> Los marcos asignados a procesos de usuario son el 20, 30, 40 y 50; la asignación es dinámica y la sustitución global. Las DL son de 32 bits y la fragmentación interna máxima por proceso es de casi 1 MiB. (TUR: instante de última referencia; TC: instante de carga.)
>
> ```
> Proceso A                               Proceso B
> Pág  Marco  P  TUR  TC   U  M           Pág  Marco  P  TUR  TC   U  M
>  0    30    1  105   50  0  0            0    30    0    5    5  0  0
>  1    20    0   20   10  0  0            1    20    0   92   30  0  0
>  2    40    1  200   90  1  0            2    20    1  100  100  0  1
>  3    50    1  300   95  1  1            3    50    0   33   20  0  0
> ```
>
> Después, A referencia la DL 00BB1233h (lectura), que genera la DF 14B1233h. a) ¿Qué algoritmo de sustitución se podría estar usando? Justifique los que aplican y los descartados. b) Con ese algoritmo, si después B referencia la DL 02111111h, ¿cuál sería la DF y qué accesos a RAM haría sin TLB?

#### Ejercicio extra 2: deducir desde una traza (Ejercicios de final de memoria, Ej 1)

> Un sistema tiene 6 marcos, paginación por demanda, asignación dinámica y alcance global. Los marcos se asignan en orden ascendente. Traza reciente de los procesos A, B y C (letra y página):
>
> ```
> Ref:     A1  A2  B1  B2  A3  B1  B0  C2  C1  A1  A3  A2  B2
> Marco 0: A1  A1  A1  A1  A1  A1  A1  A1  C1  C1  C1  C1  ?
> Marco 1: C3  A2  A2  A2  A2  A2  A2  A2  A2  A1  A1  A1  ?
> Marco 2: B1  B1  B1  B1  A3  A3  A3  A3  A3  A3  A3  A2  ?
> Marco 3: B2  B2  B2  B2  B2  B1  B1  B1  B1  B1  B1  B1  ?
> Marco 4: C0  C0  C0  C0  C0  C0  B0  B0  B0  B0  B0  B0  ?
> Marco 5: C1  C1  C1  C1  C1  C1  C1  C2  C2  C2  C2  C2  ?
> ```
>
> a) ¿Qué algoritmo se puede estar usando? Complete la última columna (pedido B2). b) ¿Hay indicios de thrashing, sabiendo que la localidad de cada proceso es siempre de 3 páginas?

#### Ejercicio extra 3: la secuencia de la clase (diapositivas de memoria virtual)

> Con 3 marcos y la secuencia 2, 3, 2, 1, 5, 2, 4, 5, 3, 2, 5, 2, cuente los fallos con FIFO, Óptimo, LRU y Clock.

### 5. Cierre

**Fórmulas**

```
FIFO: menor instante de carga (Belady).   Óptimo: el que más tarda en volver a usarse.
LRU: menor instante de última referencia.  Clock: primer U = 0 desde el puntero (U = 1 → U = 0 y sigue).
Clock modificado: (0,0) sin tocar U → (0,1) bajando U → repetir.  Víctima con M = 1 → escritura a disco.
Óptimo ≤ cualquier otro.  LRU y Óptimo no sufren Belady.
```

**Trampas**
- **Contar el hit como fallo o cargar sin avisar.** Marcá la F solo cuando la página no está.
- **En Clock, no avanzar el puntero** después de reemplazar, o no poner U = 1 al cargar.
- **En Clock modificado, bajar U en la primera vuelta.** En a) no se toca nada; los U se bajan en b).
- **Olvidar las escrituras.** Si la víctima tenía M = 1, suma un acceso a disco.
- **Pasar mal la dirección a página.** Dividí por el tamaño de página y verificá que la página sea válida para el proceso.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Qué es la anomalía de Belady? ¿Qué algoritmos la sufren?
2. (Ejercicio) 3 marcos, secuencia 1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5. Contá los fallos con FIFO y con LRU. (material propio)

## 5.3 Thrashing y conjunto de trabajo ★★★☆☆ (estimado)

Temas en Lumen: `u5-thrashing-tratamiento-prevencion`, `u5-bloqueo-paginas-page-buffering`

Apareció en el final del 20/02/2024 (ejercicio 2) y en el ejercicio de final de la cátedra con la traza de A, B y C.

### 1. Conceptos

**Localidad.** En un intervalo de tiempo, un proceso usa activamente un conjunto chico de páginas: su **localidad**. Si tiene marcos para toda su localidad, casi no genera fallos.

**Thrashing (sobrepaginación).** Si un proceso tiene menos marcos que su localidad, vive generando fallos: cada página que trae saca otra que va a necesitar enseguida. Pasa más tiempo paginando que ejecutando.

```
Asignación fija y sustitución local: un proceso con 2 marcos que en cada instrucción
usa 3 páginas → fallo en cada referencia (thrashing de ese proceso).

Asignación dinámica y sustitución global (el círculo vicioso):
  poco uso de CPU → el SO sube la multiprogramación → los procesos necesitan más
  marcos → se los roban entre sí → más fallos → procesos bloqueados esperando el
  disco → baja más el uso de CPU → el SO sube otra vez la multiprogramación...
```

La solución es **bajar el grado de multiprogramación** (suspender procesos) para que los que quedan tengan marcos suficientes.

**Conjunto de trabajo.** Es una aproximación de la localidad: las páginas distintas referenciadas en las últimas Δ referencias (la **ventana**). Si la suma de los conjuntos de trabajo de todos los procesos supera la cantidad de marcos, hay riesgo de thrashing y hay que suspender alguno:

$$\sum_{i} |CT_i| \le \text{marcos totales}$$

Por ejemplo, con Δ = 5 y la secuencia de un proceso "3 4 4 3 4", su conjunto de trabajo es {3, 4}, de tamaño 2.

**Frecuencia de fallos.** Otra forma de controlarlo: si la tasa de fallos de un proceso supera un umbral, se le dan más marcos; si baja de otro umbral, se le quitan.

**Bloqueo (lockeo) de páginas.** Si un proceso se bloquea esperando una E/S sobre un marco (por ejemplo, el DMA va a escribir ahí), otro proceso podría elegir ese marco como víctima. Se marca el marco con un bit de **lock** mientras dura la E/S para que no pueda reemplazarse.

**Page buffering.** Se mantiene un pool de marcos libres: ante un fallo, la página se carga enseguida en un marco del pool, y la víctima se escribe a disco después, sin que el proceso la espere. Además, si la víctima se vuelve a pedir antes de reutilizar su marco, se recupera sin ir a disco.

**Los tipos de ejercicio que toman:**
1. **¿Hay thrashing?** Comparar la localidad (o el conjunto de trabajo) con los marcos asignados, y cómo solucionarlo.
2. **Conjunto de trabajo:** calcularlo con una ventana y decidir si hay que suspender.
3. **Teoría:** el círculo vicioso de la sustitución global, lockeo, page buffering.

### 2. Ejemplo resuelto (final del 20/02/2024, práctica 2)

> Dos procesos, P1 y P2, generan las siguientes secuencias de referencias (número de página), que se repiten indefinidamente:
>
> ```
> P1: 10 11 12 13 14 15 16 17 ... (repite desde el principio)
> P2: 10 11 0 3 4 3 11 4 0 3 4 3 0 11 ... (repite desde el principio)
> ```
>
> Cada proceso tiene 4 marcos, la sustitución es local con LRU y hay una TLB de 2 entradas con sustitución FIFO. Para cada proceso, de forma aislada: a) Si se actualizara el sistema con una TLB de 4 entradas, ¿mejoraría en algo su ejecución? b) ¿Podría generarse thrashing? En caso afirmativo, indique cómo solucionarlo.

Es del tipo 1. Hay que ver el tamaño de la localidad de cada proceso y compararlo con los marcos y con las entradas de la TLB.

```
Paso 1: localidad de P1
  Recorre 8 páginas distintas en ciclo (10 a 17): su localidad es de 8 páginas.

Paso 2: localidad de P2
  Salvo el 10, que aparece una vez por vuelta, usa todo el tiempo 0, 3, 4 y 11:
  una localidad de 4 páginas.

Paso 3: a) TLB de 4 entradas
  P1: con 8 páginas en ciclo, ni 2 ni 4 entradas alcanzan → todo sigue siendo miss.
  P2: sus 4 páginas entran en una TLB de 4 → casi todo pasa a ser hit y se ahorra
  el acceso a la tabla de páginas. Mejora solo P2.

Paso 4: b) thrashing
  P1: 8 páginas en ciclo con 4 marcos y LRU → cada referencia saca justo la página
  que se va a pedir 4 referencias después: fallo en todas → thrashing.
  Solución: darle 8 marcos (su localidad) o, si no hay, suspenderlo.
  P2: su localidad de 4 entra en sus 4 marcos → pocos fallos (unos 2 por vuelta
  de 14 referencias, por el 10) → no hay thrashing.

Control: coincide con la resolución de la cátedra (mejora P2; thrashing en P1, se
soluciona con 8 marcos) ✓
```

### 3. Ejercicio guiado (diapositivas de memoria virtual, conjunto de trabajo)

> Hay 8 marcos para tres procesos, y la ventana del conjunto de trabajo es de 5 referencias. Las secuencias son:
>
> ```
> P1: 3 4 4 3 4 4 3 3 4 1 4 3 5 3 6 4 6
> P2: 1 1 1 1 3 2 1 3 3 1 6 6 5 3 7 4 6
> P3: 8 4 7 7 8 4 3 3 4 8 4 3 8 3 8 4 6
> ```
>
> a) Calcule el conjunto de trabajo de cada proceso después de la referencia 5 (referencias 1 a 5). b) Ídem después de la referencia 10 (referencias 6 a 10). c) ¿En qué momento hay riesgo de thrashing y qué debería hacer el SO?

Es del tipo 2. En cada ventana, el conjunto de trabajo son las páginas **distintas**.

```
Paso 1: a) CT de P1, P2 y P3 (referencias 1 a 5) y la suma
  → ________

Paso 2: b) CT de P1, P2 y P3 (referencias 6 a 10) y la suma
  → ________

Paso 3: c) comparación con los 8 marcos y qué hacer
  → ________
```

### 4. Práctica

Respondé cada una en dos o tres líneas antes de mirar las respuestas.

1. ¿Por qué con sustitución global y asignación dinámica el thrashing se realimenta? ¿Qué hace mal el planificador de largo plazo?
2. ¿Qué problema resuelve el bloqueo de páginas? Dá un ejemplo.
3. ¿Qué ventaja tiene el page buffering?
4. Verdadero o falso: "Para reducir el thrashing conviene aumentar el grado de multiprogramación".

### 5. Cierre

**Fórmulas**

$$\sum_{i} |CT_i| \le \text{marcos totales} \quad \text{(si no, riesgo de thrashing: suspender)}$$

```
Localidad > marcos asignados → fallo casi en cada referencia → thrashing
Solución: más marcos al proceso, o bajar el grado de multiprogramación (suspender)
Lockeo: el marco con E/S en curso no se puede reemplazar. Page buffering: pool de marcos libres
```

**Trampas**
- **Subir la multiprogramación para usar más la CPU** cuando la CPU está ociosa por thrashing: lo empeora.
- **Contar páginas repetidas en el conjunto de trabajo.** Son las distintas dentro de la ventana.
- **Pensar que una TLB más grande arregla el thrashing.** La TLB acelera la traducción; los fallos de página dependen de los marcos.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Qué es el thrashing, por qué ocurre y cómo se soluciona?
2. (Ejercicio) Un proceso repite la secuencia 1, 2, 3, 4, 5 con 4 marcos y LRU. ¿Cuántos fallos genera por vuelta, ya en régimen? ¿Cuántos con 5 marcos? (material propio)

## Respuestas del capítulo 5

### 5.1 Ejercicio guiado

```
Paso 1: 0 → pág 0, offset 0 → marco 3 → DF = 3 · 1024 + 0 = 3072
        3728 → pág 3, offset 656 → no está → fallo de página
Paso 2: 1024 → pág 1, offset 0 → marco 1 → DF 1024
        1025 → pág 1, offset 1 → DF 1025
Paso 3: 4099 → pág 4, offset 3 → marco 2 → DF = 2048 + 3 = 2051
        7800 → pág 7, offset 632 → no está → fallo de página
Paso 4: con memoria virtual la DL depende del espacio que queremos que direccione el
  proceso, no de la RAM: 1 MiB = 2^20 → 20 bits (13 de offset, por las páginas de
  8 KiB, y 7 de página). La DF sigue siendo de 17 bits (128 KiB).
```

### 5.1 Ejercicio extra 1

```
(resolución propia; la de la cátedra resuelve la primera y la segunda)
DL de 16 bits = seg (2 bits) | pág (2 bits) | offset (12 bits, por los marcos de 4 KB).
La TLB está indexada por el primer dígito hexa (seg | pág).

3C38h: "3" está en la TLB → marco 1. 3 = 00|11 → seg 0 (RW): se puede escribir.
       DF = 1C38h.
FFACh: F = 11|11 → segmento 3, que el proceso no tiene → segmentation fault.
AA00h: A = 10|10 → seg 2, pág 2 (no está en la TLB). El segmento 2 es R--: una
       escritura viola la protección y no se atiende. (Si fuera una lectura: P = 0 →
       fallo de página; con Clock global la víctima saldría de las presentes con U = 0,
       pero falta saber dónde está el puntero.)
```

### 5.1 Ejercicio extra 2

```
Falso. Un fallo de página significa que la página no está en memoria: siempre hay
que leerla de disco (la TLB solo acelera la traducción de las páginas presentes).
```

### 5.1 Ejercicio extra 3

```
a) Verificar que la dirección sea válida → buscar marco libre o elegir víctima (si
   tiene M = 1, escribirla) → leer la página de disco (el proceso se bloquea) →
   actualizar tabla (P = 1) y TLB → reiniciar la instrucción.
b) Porque su copia en disco está al día: se reemplaza sin escribir (un acceso a
   disco menos).
c) Local: la víctima sale de los marcos del mismo proceso. Global: de cualquier
   proceso (un proceso puede robarle marcos a otro).
```

### 5.1 Autoevaluación

```
1. Validar la dirección, conseguir un marco (libre o víctima), leer la página de disco,
   actualizar la tabla y la TLB, reiniciar la instrucción. Si la víctima tiene M = 1,
   antes hay que escribirla en disco (un acceso más).

2. 1500 → pág 0, offset 1500 → marco 4 → DF = 4 · 2048 + 1500 = 9692
   3000 → pág 1, offset 952 → no presente → fallo de página
   4200 → pág 2, offset 104 → marco 1 → DF = 2048 + 104 = 2152
```

### 5.2 Ejercicio guiado

```
Paso 1: 100 → pág 0 (L). 122950 → pág 15 (E). 98306 → pág 12 (L).
  139264 → pág 17 (E). 122880 → pág 15 (L). 155650 → pág 19 (E).
  172100 → pág 21: inválida (el proceso tiene páginas 0 a 19) → error, no es fallo.
  100 → pág 0 (L).

Paso 2: LRU (marcos 1: 14, 3: 17, 5: 19, 8: libre)
  0  → fallo, marco 8 libre
  15 → fallo, víctima 17 (instante 3), sin escribir
  12 → fallo, víctima 19 (instante 15), tenía M = 1 → escritura
  17 → fallo, víctima 14 (instante 28), M = 1 → escritura
  15 → hit
  19 → fallo, víctima 0, sin escribir
  0  → fallo, víctima 12, sin escribir
  Total: 6 fallos, 2 escrituras. Queda: 17, 15, 0, 19.

Paso 3: Clock modificado (marco: pág U M, en orden 1, 3, 5, 8)
  0  → fallo, marco 8 libre → 0 (1,0). Puntero → 1.
  15 → (0,0): nadie. (0,1) bajando U: 1, 3, 5, 8 quedan con U = 0; nadie.
       (0,0) otra vez desde 1: 1 (0,1), 3 (0,0) ✓ → sale 17 sin escribir.
       Marco 3 ← 15 (1,1). Puntero → 5.
  12 → (0,0) desde 5: 5 (0,1), 8 (0,0) ✓ → sale 0. Marco 8 ← 12 (1,0). Puntero → 1.

Paso 4:
  17 → (0,0): nadie. (0,1) desde 1: 1 (0,1) ✓ → sale 14, M = 1 → escritura.
       Marco 1 ← 17 (1,1). Puntero → 3.
  15 → hit.   19 → hit (U = 1, M = 1).   21 → acceso inválido.
  0  → (0,0) desde 3: nadie. (0,1) bajando U: 3, 5, 8, 1 → U = 0; nadie.
       (0,0) desde 3: 3 (0,1), 5 (0,1), 8 (0,0) ✓ → sale 12. Marco 8 ← 0.
  Total: 5 fallos, 1 escritura.

Paso 5: rinde mejor Clock modificado: menos fallos (5 contra 6) y menos escrituras
  a disco (1 contra 2). El criterio es la cantidad de accesos a disco (fallos más
  escrituras de víctimas modificadas).
```

### 5.2 Ejercicio extra 1

```
a) Páginas de 1 MiB (20 bits de offset). 00BB1233h → pág 00Bh = 11, offset B1233h.
   DF 14B1233h → marco 14h = 20. El marco 20 lo tenía B, pág 2 → fue la víctima.
   FIFO: no; habría elegido la de menor TC, A pág 0 (TC 50).
   LRU: sí; B pág 2 tiene el menor TUR entre las presentes (100 < 105, 200, 300).
   Clock: no seguro; B pág 2 tiene U = 0, pero en orden de carga A pág 0 (U = 0)
   está antes.
   Clock modificado: no; B pág 2 tiene (0,1) y A pág 0 tiene (0,0).
   → LRU.
b) 02111111h → pág 021h = 33 de B, offset 11111h. No está → fallo. Con LRU la víctima
   es A pág 0 (TUR 105), en el marco 30 = 1Eh → DF = 01E11111h.
   Accesos a RAM (según la cátedra): leer la tabla de B (fallo), escribir la tabla de
   A (pág 0 ya no presente), escribir la página traída en el marco, escribir la tabla
   de B (presente), volver a leer la tabla de B para traducir y acceder al dato.
```

### 5.2 Ejercicio extra 2

```
(resolución propia)
a) Las víctimas van rotando en orden de marco: 1, 2, 3, 4, 5, 0, 1, 2 → FIFO.
   LRU queda descartado: en A3 saca a B1 del marco 2, que se acababa de usar (ref 3).
   En A2 (penúltima) FIFO saca a A3 aunque se acababa de referenciar: LRU no lo haría.
   B2 → fallo; la más vieja cargada es B1, en el marco 3 → marco 3 = B2.
   Última columna: C1, A1, A2, B2, B0, C2.
b) Sí: en 13 referencias hubo 9 fallos. Los tres procesos necesitan 3 páginas cada uno
   (9 en total) y hay 6 marcos, con sustitución global: se roban marcos entre sí.
   Habría que suspender un proceso (bajar la multiprogramación).
```

### 5.2 Ejercicio extra 3

```
FIFO 9, Óptimo 6, LRU 7, Clock 8 (resultados de la clase).
```

### 5.2 Autoevaluación

```
1. Que con más marcos haya más fallos de página para la misma secuencia. La sufre
   FIFO (y Clock, que se basa en FIFO); LRU y Óptimo no.

2. FIFO: 9 fallos.  LRU: 10 fallos.
   (Con 4 marcos, FIFO da 10: es la secuencia clásica de la anomalía de Belady.)
```

### 5.3 Ejercicio guiado

```
Paso 1: P1: 3 4 4 3 4 → {3, 4} = 2. P2: 1 1 1 1 3 → {1, 3} = 2.
  P3: 8 4 7 7 8 → {8, 4, 7} = 3. Suma = 7 ≤ 8 → sin riesgo.

Paso 2: P1: 4 3 3 4 1 → {4, 3, 1} = 3. P2: 2 1 3 3 1 → {2, 1, 3} = 3.
  P3: 4 3 3 4 8 → {4, 3, 8} = 3. Suma = 9 > 8.

Paso 3: después de la referencia 10 la suma de los conjuntos de trabajo supera los
  8 marcos: hay riesgo de thrashing. El SO debería suspender un proceso (bajar el
  grado de multiprogramación) hasta que la suma vuelva a entrar.
```

### 5.3 Práctica

```
1. Porque los procesos le roban marcos a otros, que empiezan a fallar y a bloquearse
   esperando el disco; baja el uso de CPU y el planificador de largo plazo, al ver la
   CPU ociosa, admite más procesos, que necesitan más marcos. Tendría que hacer lo
   contrario: suspender.
2. Que se elija como víctima un marco con una E/S en curso. Ejemplo: A espera que el
   DMA escriba en su página 6 (marco 11); B tiene un fallo y saca el marco 11: la E/S
   termina en una página de otro proceso. Con lock, el marco 11 no se puede elegir.
3. El proceso no espera la escritura de la víctima: la página se carga en un marco
   libre del pool y la víctima se escribe después. Además, una víctima reciente se
   puede recuperar del pool sin ir a disco.
4. Falso: hay que bajarlo, para que los procesos que quedan tengan más marcos.
```

### 5.3 Autoevaluación

```
1. Un proceso (o el sistema) pasa más tiempo resolviendo fallos de página que
   ejecutando, porque tiene menos marcos que su localidad. Con sustitución global se
   realimenta al subir la multiprogramación. Se soluciona dándole más marcos o
   bajando el grado de multiprogramación (suspender), controlando el conjunto de
   trabajo o la frecuencia de fallos.

2. Con 4 marcos y LRU, cada referencia saca a la que viene 4 después: 5 fallos por
   vuelta (todas). Con 5 marcos entra toda la localidad: 0 fallos en régimen.
```
