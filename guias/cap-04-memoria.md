# Capítulo 4: Memoria (clase 5)

## 4.1 Asignación contigua y particiones ★★☆☆☆ (estimado)

Temas en Lumen: `u5-funciones-administrador-memoria`, `u5-particiones-fijas-variables`

No hay parciales con fecha relevados para el 2do parcial, así que las estrellas de los capítulos 4 a 6 son estimaciones hechas con los "Ejercicios de parcial" de la cátedra (sin fecha) y el final del 20/02/2024. Este bloque no tiene ejercicios de parcial en el material, pero la teoría aparece en las comparaciones (fragmentación, compactación). Los ejercicios son material propio. El buddy system, que está en el programa, no se dio en la clase.

### 1. Conceptos

**Jerarquía de memoria.** Registros, caché, RAM y disco: de más rápida y chica a más lenta y grande. Todo lo que se ejecuta y todos los datos que se usan tienen que estar en la memoria principal (RAM).

**Dirección lógica y física.** El proceso genera **direcciones lógicas** (DL); la memoria se accede con **direcciones físicas** (DF). La traducción la hace la **MMU** (Memory Management Unit), en hardware. Se puede fijar la dirección al compilar o al cargar (DL = DF) o en tiempo de ejecución (DL ≠ DF): solo la última permite mover el proceso.

**Requerimientos del administrador de memoria.** Reubicación (poder cargar el proceso en cualquier lugar y moverlo), protección (que un proceso no acceda al espacio de otro), compartir (varios procesos usando las mismas páginas, como el código de una biblioteca), organización lógica (cómo ve el proceso su memoria) y organización física (cómo se guarda de verdad).

**Asignación contigua con base y límite.** Cada proceso ocupa un bloque contiguo. La MMU tiene un registro **base** (dónde empieza) y uno **límite** (cuánto mide):

$$DF = \text{base} + DL \qquad \text{si } DL < \text{límite; si no, error de direccionamiento}$$

**Particiones fijas.** La memoria se divide de antemano en N particiones. Es simple y tiene poco overhead, pero un proceso no puede ser más grande que la partición, no puede haber más de N procesos y el espacio que sobra dentro de cada partición se pierde: **fragmentación interna**.

**Particiones dinámicas.** Cada partición se crea del tamaño exacto del proceso. No hay fragmentación interna, pero al irse liberando quedan huecos chicos separados: **fragmentación externa** (hay memoria libre suficiente, pero no contigua). Se atenúa de dos formas:
- **Consolidación:** cuando se liberan dos huecos vecinos, se unen en uno.
- **Compactación:** mover los procesos para juntar todos los huecos en uno. Es cara y solo se puede si la reubicación es en tiempo de ejecución.

**Algoritmos de ubicación.** Qué hueco elegir para un proceso nuevo:

```
Primer ajuste (first fit):     el primer hueco donde entra, desde el principio
Siguiente ajuste (next fit):   el primero donde entra, desde donde quedó la última búsqueda
Mejor ajuste (best fit):       el hueco más chico donde entra (deja sobrantes chicos)
Peor ajuste (worst fit):       el hueco más grande (deja sobrantes grandes, reutilizables)
```

**Los tipos de ejercicio que toman:**
1. **Ubicar procesos** con cada algoritmo en una lista de huecos y decir cuál falla.
2. **Fragmentación:** interna o externa, según el esquema, y cuánto como máximo.
3. **Comparar esquemas:** ventajas y desventajas (particiones fijas, dinámicas, segmentación, paginación).

### 2. Ejemplo resuelto (material propio)

> Una memoria con particiones dinámicas tiene estos huecos libres, en orden de dirección: 150 KiB, 400 KiB, 250 KiB, 100 KiB y 500 KiB. Llegan, en este orden, procesos de 230 KiB, 90 KiB, 480 KiB y 350 KiB. Ubíquelos con primer ajuste y con mejor ajuste. ¿Alguno no entra? ¿Por qué?

Es del tipo 1. Se recorre la lista de huecos para cada proceso, se achica el hueco elegido y se sigue con la lista actualizada.

```
Paso 1: primer ajuste
  230 → 150 no; 400 sí → queda 170     Huecos: 150, 170, 250, 100, 500
  90  → 150 sí → queda 60              Huecos:  60, 170, 250, 100, 500
  480 → 60, 170, 250, 100 no; 500 sí → queda 20
  350 → ningún hueco alcanza (60, 170, 250, 100, 20) → no entra

Paso 2: por qué no entra
  Hay 60 + 170 + 250 + 100 + 20 = 600 KiB libres, más que 350, pero ninguno
  contiguo: es fragmentación externa. Se podría compactar.

Paso 3: mejor ajuste (el hueco más chico donde entra)
  230 → 250 → queda 20                 Huecos: 150, 400, 20, 100, 500
  90  → 100 → queda 10                 Huecos: 150, 400, 20, 10, 500
  480 → 500 → queda 20                 Huecos: 150, 400, 20, 10, 20
  350 → 400 → queda 50                 Entran los cuatro.

Control: la memoria libre total baja en 230 + 90 + 480 + 350 = 1150 KiB con mejor
ajuste: 1400 − 1150 = 250 = 150 + 50 + 20 + 10 + 20 ✓
```

### 3. Ejercicio guiado (material propio)

> Con los mismos huecos y procesos del ejemplo, ubíquelos con peor ajuste y con siguiente ajuste.

Es del tipo 1. En siguiente ajuste, la búsqueda arranca desde el hueco donde se ubicó el proceso anterior y da la vuelta si hace falta.

```
Paso 1: peor ajuste, proceso de 230 y de 90
  → ________

Paso 2: peor ajuste, proceso de 480 y de 350
  → ________

Paso 3: siguiente ajuste, procesos de 230 y 90
  → ________

Paso 4: siguiente ajuste, procesos de 480 y 350
  → ________

Paso 5: ¿qué algoritmo aprovechó mejor la memoria en este caso?
  → ________
```

### 4. Práctica

Respondé cada una en dos o tres líneas antes de mirar las respuestas.

1. ¿Qué diferencia hay entre fragmentación interna y externa? ¿Cuál tienen las particiones fijas y cuál las dinámicas?
2. ¿Qué diferencia hay entre consolidación y compactación? ¿Cuándo no se puede compactar?
3. Con registros base = 3000 y límite = 1200, ¿a qué DF va la DL 500? ¿Y la DL 1300?
4. ¿Por qué el peor ajuste podría fragmentar menos que el mejor ajuste?

### 5. Cierre

**Fórmulas**

$$DF = \text{base} + DL \quad (DL < \text{límite})$$

```
Particiones fijas: fragmentación interna, límite de procesos y de tamaño
Particiones dinámicas: fragmentación externa → consolidación y compactación
First fit: el primero desde el inicio. Next fit: desde la última búsqueda.
Best fit: el más chico donde entra. Worst fit: el más grande.
```

**Trampas**
- **Decir que las particiones dinámicas tienen fragmentación interna.** Tienen externa; las fijas, interna.
- **Olvidar achicar el hueco** después de ubicar un proceso: el siguiente busca en la lista actualizada.
- **Confundir consolidación con compactación.** Consolidar une huecos vecinos al liberar; compactar mueve procesos.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Qué es la fragmentación externa y qué dos cosas se hacen para atenuarla?
2. (Ejercicio) Huecos: 300, 120, 200 KiB. Procesos: 110, 190, 280 KiB. Ubicalos con mejor ajuste y con primer ajuste. (material propio)

## 4.2 Paginación ★★★★☆ (estimado)

Temas en Lumen: `u5-paginacion-pura`

Es la base de todos los ejercicios de memoria: pasar de dirección lógica a física, calcular bits y tamaños, y la TLB. La guía de memoria tiene un ejercicio de parcial sin memoria virtual, y los de memoria virtual (capítulo 5) arrancan siempre con esta cuenta.

### 1. Conceptos

**Páginas y marcos.** El proceso se divide en **páginas** y la memoria, en **marcos** (frames) del mismo tamaño. Cualquier página puede ir en cualquier marco, así que el proceso no necesita estar contiguo. No hay fragmentación externa; sí hay fragmentación interna, solo en la **última página** de cada proceso (como máximo, una página menos un byte).

**Tabla de páginas.** Hay una por proceso y dice en qué marco está cada página. Cada entrada tiene el número de marco y bits de control: **validez** (si la página es del proceso), permisos (rwx) y, con memoria virtual, presencia, uso y modificado. El registro **PTBR** apunta a la tabla del proceso en ejecución, y se guarda en el PCB en cada cambio de proceso. Los marcos libres se administran, por ejemplo, con un **bitmap** (un bit por marco).

**Dirección lógica y física.** Con páginas de $2^k$ bytes, los k bits de abajo son el **desplazamiento** (offset) y el resto, el número de página. La traducción cambia el número de página por el de marco y deja el offset igual:

```
DL = | nº de página | offset (k bits) |   →   DF = | nº de marco | offset (k bits) |
```

$$\text{página} = \left\lfloor \frac{DL}{\text{tam. pág.}} \right\rfloor \qquad \text{offset} = DL \bmod \text{tam. pág.} \qquad DF = \text{marco} \cdot \text{tam. pág.} + \text{offset}$$

Por ejemplo, con páginas de 1 KiB y la página 1 en el marco 6: DL 2045 = página 1, offset 1021 → DF = 6 · 1024 + 1021 = 7165. En binario es lo mismo: los 10 bits de abajo (offset) se copian y los de arriba se reemplazan por el marco.

**Cantidad de bits.** Se sale de las potencias de 2:

$$\text{bits de DL} = \log_2(\text{espacio lógico}) \qquad \text{bits de offset} = \log_2(\text{tam. pág.}) \qquad \text{bits de marco} = \log_2(\text{cant. de marcos})$$

$$\text{cant. de páginas} = \frac{2^{\text{bits DL}}}{\text{tam. pág.}} \qquad \text{cant. de marcos} = \frac{\text{tam. RAM}}{\text{tam. pág.}}$$

**Tamaño de la tabla.** Con direcciones de 32 bits y páginas de 1 KiB, la tabla puede tener $2^{32}/2^{10} = 2^{22}$ entradas; con 4 bytes por entrada, ocupa 16 MiB contiguos. Por eso se usan:
- **Paginación jerárquica:** se pagina la tabla de páginas (dos o más niveles). La DL se parte en índice de primer nivel, índice de segundo nivel y offset; cada nivel es un acceso más a memoria.
- **Tabla invertida:** una sola tabla para todo el sistema, con una entrada por marco (qué página de qué proceso tiene). Ocupa poco, pero hay que buscar (se mejora con hash) y complica compartir memoria.

**TLB.** Sin ayuda, cada acceso a memoria cuesta dos: uno a la tabla de páginas y otro al dato. La **TLB** es una caché asociativa en hardware con las últimas traducciones. Si la página está (hit), la traducción es inmediata; si no (miss), se va a la tabla y se agrega la entrada. Puede guardar el identificador del proceso, para no vaciarla en cada cambio de proceso.

$$T_{\text{efectivo}} = P_{\text{hit}} \cdot (T_{\text{TLB}} + T_{\text{mem}}) + P_{\text{miss}} \cdot (T_{\text{TLB}} + 2\,T_{\text{mem}})$$

Con 98 % de aciertos, TLB de 20 ns y memoria de 100 ns: 0,98 · 120 + 0,02 · 220 = 122 ns.

**Protección y memoria compartida.** Los bits rwx de cada entrada protegen las páginas. Para compartir (por ejemplo, el código de dos instancias del mismo programa), las tablas de los dos procesos apuntan al mismo marco.

**Los tipos de ejercicio que toman:**
1. **Bits y tamaños:** bits de DL y DF, tamaño de página, cantidad de páginas y marcos, tamaño máximo de un proceso.
2. **Traducir direcciones** de DL a DF (y al revés) con una tabla de páginas, en decimal o en hexa.
3. **Fragmentación:** interna máxima y promedio; externa (cero).
4. **TLB:** tiempo efectivo de acceso; tabla jerárquica o invertida.

### 2. Ejemplo resuelto (guía de memoria resuelta, hoja «Parcial (sin MV)»)

> En un sistema de direcciones de 20 bits (tanto físicas como lógicas) y un direccionamiento de hasta 128 páginas por proceso, sin memoria virtual, hay dos procesos en ejecución que corresponden a distintos ejecutables. Sus tablas de páginas completas son:
>
> ```
> Proceso 1 (pág → marco): 0→9  1→2  2→12  3→14  4→11  5→1
> Proceso 2 (pág → marco): 0→8  1→3  2→13  3→15  4→10  5→0  6→4  7→5
> ```
>
> Responda en decimal: a) Tamaño de la página. b) Cantidad de marcos en memoria. c) A qué marco hacen referencia las direcciones P1: 04234h y P2: 08345h. d) Fragmentación interna promedio, si suele haber un nivel de multiprogramación de 4 procesos. e) Fragmentación externa máxima.

Es del tipo 1, 2 y 3. Primero se reparte la DL entre página y offset; con eso sale todo lo demás.

```
Paso 1: bits de página
  128 páginas por proceso = 2^7 → 7 bits para el número de página

Paso 2: a) tamaño de página
  20 − 7 = 13 bits de offset → 2^13 = 8192 bytes (8 KiB)

Paso 3: b) cantidad de marcos (DF de 20 bits)
  2^20 / 2^13 = 2^7 = 128 marcos

Paso 4: c) P1: 04234h, en 20 bits
  0000 010|0 0010 0011 0100  → página 0000010 = 2 → marco 12
  (offset = 0 0010 0011 0100 = 564 → DF = 12 · 8192 + 564 = 98868 = 18234h)

Paso 5: c) P2: 08345h
  0000 100|0 0011 0100 0101  → página 4 → marco 10
  (offset = 837 → DF = 10 · 8192 + 837 = 82757 = 14345h)

Paso 6: d) fragmentación interna promedio
  Cada proceso desperdicia en promedio media página en la última:
  (8192 / 2) · 4 = 16384 bytes en todo el sistema

Paso 7: e) fragmentación externa máxima
  0 bytes: cualquier marco libre sirve para cualquier página.

Control: coincide con la resolución de la cátedra (8192 bytes, 128 marcos, marcos 12 y 10) ✓
```

### 3. Ejercicio guiado (Guía de memoria, Ej 1 y 2)

> 1) Considere un espacio de direccionamiento lógico de 8 páginas de 1024 bytes cada una, mapeado en una memoria física de 32 marcos. ¿Cuántos bits hay en la dirección lógica? ¿Y en la física? Sin memoria virtual, ¿cómo tendría que ser la relación entre esos tamaños?
> 2) Un sistema con paginación simple (sin memoria virtual) tiene 256 KiB de memoria real, 20 bits de direccionamiento lógico y páginas de 4 KiB. ¿Cuál es el tamaño máximo de un programa (ignorando el SO)? ¿Cuál es la fragmentación interna máxima por proceso y la externa?

Son del tipo 1 y 3. Pasá todo a potencias de 2 y sumá bits: página + offset para la DL, marco + offset para la DF.

```
Paso 1: 1) bits de offset (páginas de 1024 bytes) y de página (8 páginas)
  → ________

Paso 2: 1) bits de marco (32 marcos) y bits de la DF
  → ________

Paso 3: 1) sin memoria virtual, ¿DL ≤ DF o DL ≥ DF? ¿Por qué?
  → ________

Paso 4: 2) espacio lógico (20 bits) contra memoria real (256 KiB): tamaño máximo
  → ________

Paso 5: 2) fragmentación interna máxima y externa
  → ________
```

### 4. Práctica

#### Ejercicio extra 1: tamaño de la tabla (material propio, con los datos de la clase)

> Direcciones de 32 bits y páginas de 4 KiB, entradas de 4 bytes. a) ¿Cuántas entradas tiene la tabla de páginas de un proceso y cuánto ocupa? b) Con paginación de dos niveles de 10 bits cada uno, ¿cuánto ocupa cada tabla de segundo nivel?

#### Ejercicio extra 2: TLB (material propio, con los datos de la clase)

> La TLB tarda 10 ns y la memoria 80 ns. a) ¿Cuál es el tiempo efectivo con 95 % de aciertos? b) ¿Y sin TLB?

#### Ejercicio extra 3: teoría (material propio)

> Verdadero o falso, justificando: a) "La paginación no tiene fragmentación". b) "Dos procesos pueden compartir una página de código si sus tablas apuntan al mismo marco". c) "La tabla de páginas invertida tiene una entrada por página de cada proceso".

### 5. Cierre

**Fórmulas**

$$\text{página} = \left\lfloor \frac{DL}{\text{tam}} \right\rfloor \qquad \text{offset} = DL \bmod \text{tam} \qquad DF = \text{marco} \cdot \text{tam} + \text{offset}$$

$$\text{bits}_{DL} = \text{bits}_{\text{pág}} + \text{bits}_{\text{offset}} \qquad \text{bits}_{DF} = \text{bits}_{\text{marco}} + \text{bits}_{\text{offset}} \qquad T_{\text{ef}} = P_{h}(T_{TLB} + T_m) + P_{m}(T_{TLB} + 2T_m)$$

```
2^10 = 1 KiB   2^20 = 1 MiB   2^30 = 1 GiB   2^13 = 8 KiB   2^12 = 4 KiB
1 hexa = 4 bits. Fragmentación: interna en la última página; externa, cero
```

**Trampas**
- **Cortar mal el hexa.** Pasalo a binario con la cantidad total de bits y recién ahí separá página y offset (el corte no siempre cae en un dígito hexa).
- **Traducir el offset.** El offset se copia igual; solo cambia la página por el marco.
- **Decir que la paginación no fragmenta.** Tiene fragmentación interna (última página).
- **Olvidar el acceso a la tabla.** Sin TLB, cada acceso a un dato cuesta dos accesos a memoria.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Para qué sirve la TLB y por qué hace falta? ¿Qué problema resuelve la paginación jerárquica?
2. (Ejercicio) DL de 16 bits, páginas de 4 KiB. La página 3 está en el marco 9. ¿A qué DF va la DL 3A7Fh? (material propio)

## 4.3 Segmentación y segmentación paginada ★★★★☆ (estimado)

Temas en Lumen: `u5-segmentacion-simple`

El primero de los "Ejercicios de parcial" de memoria de la cátedra es de segmentación paginada, y la guía tiene tres ejercicios de segmentación.

### 1. Conceptos

**Segmentación.** El proceso se divide en **segmentos** de tamaño variable que siguen su estructura lógica: código, datos, pila. Cada segmento está contiguo en memoria, pero los segmentos no necesitan estar juntos. Cada uno puede tener sus permisos (código: lectura y ejecución; datos: lectura y escritura). No hay fragmentación interna, pero sí **externa** (como las particiones dinámicas).

**Tabla de segmentos.** Por cada segmento, la **base** (dónde empieza en memoria), el **límite** (cuánto mide) y los permisos. La DL es número de segmento más offset:

$$DF = \text{base}_{s} + \text{offset} \qquad \text{si offset} < \text{límite}_{s}\text{; si no, segmentation fault}$$

Además se valida el permiso: escribir en un segmento de solo lectura da una interrupción por modo de acceso inválido.

```
Ejemplo: segmento 0 con base 1024 y tamaño 1024
DL (seg 0, offset 100) → DF = 1024 + 100 = 1124
DL (seg 0, offset 1500) → 1500 ≥ 1024 → segmentation fault
```

**Segmentación paginada.** Cada segmento se divide en páginas y tiene su propia tabla de páginas. La memoria queda dividida en marcos, así que **no hay fragmentación externa**; hay algo de interna, en la última página de **cada segmento**.

```
DL = | nº segmento | nº página | offset |   →   DF = | nº marco | offset |
```

**Comparación de esquemas.**

```
Esquema               Fragmentación              Ventaja principal
Particiones fijas     interna                    simple, poco overhead
Particiones dinámicas externa                    usa la memoria justa
Segmentación          externa                    visión lógica, permisos por segmento
Paginación            interna (última página)    sin fragmentación externa, no contigua
Segmentación paginada interna (última de c/seg)  lo mejor de las dos, más estructuras
```

**Los tipos de ejercicio que toman:**
1. **Traducir direcciones** con una tabla de segmentos, detectando segmentation fault y violaciones de permisos.
2. **Reconstruir la tabla** a partir de pares DL → DF.
3. **Segmentación paginada:** DF a DL, cargar otra instancia compartiendo páginas, tamaño máximo de proceso, fragmentación.

### 2. Ejemplo resuelto (Ejercicios de parcial de memoria, Ej 1)

> Un sistema de 16 bits sin memoria virtual y con 64 KiB de memoria usa segmentación paginada. Hay dos procesos: PID1, del Programa 1 (que nunca varía su tamaño), y PID2, del Programa 2. Cada proceso usa un segmento para las páginas que pueden modificarse y otro para las que no. Cada segmento puede tener hasta 8 páginas. Las tablas de páginas son (marco, protección):
>
> ```
> PID1 seg 0: 7 RX, 6 RX, 10 RX          PID1 seg 1: 5 RW, 11 RW
> PID2 seg 0: 14 RX, 1 RX, 2 RX, 3 RX, 4 RX    PID2 seg 1: 8 RW, 9 RW, 12 RW
> ```
>
> a) ¿A qué direcciones lógicas corresponden las físicas 5111h, B333h, 8111h y 7444h? b) Con el estado actual de la memoria, ¿es posible cargar otra instancia del Programa 1 sin finalizar ni descargar los procesos actuales? ¿Cómo? c) ¿Cuál es el tamaño máximo teórico y real de un proceso? d) Determine la fragmentación máxima externa e interna por proceso.

Es del tipo 3. Primero hay que repartir los 16 bits de la DL: 2 segmentos (1 bit) y 8 páginas por segmento (3 bits).

```
Paso 1: formato
  DL = seg (1 bit) | pág (3 bits) | offset (12 bits) → páginas de 2^12 = 4 KiB
  DF = marco (4 bits) | offset (12 bits) → 64 KiB / 4 KiB = 16 marcos

Paso 2: a) cada DF: el primer dígito hexa es el marco
  5111h → marco 5 = PID1 seg 1 pág 0 → DL = 1|000|111h = 8111h
  B333h → marco 11 = PID1 seg 1 pág 1 → DL = 1|001|333h = 9333h
  8111h → marco 8 = PID2 seg 1 pág 0 → DL = 8111h
  7444h → marco 7 = PID1 seg 0 pág 0 → DL = 0|000|444h = 0444h

Paso 3: b) marcos libres
  Usados: PID1 3 + 2 = 5, PID2 5 + 3 = 8 → 13 de 16 → libres: 0, 13 y 15.
  Otra instancia necesitaría 5 marcos, pero el segmento 0 es de solo lectura
  (código): se comparte. Solo hay que cargar las 2 páginas del segmento 1.
  PID nuevo seg 0: 7, 6, 10 (compartidos)   seg 1: 13, 15 → sí se puede.

Paso 4: c) tamaño máximo
  Teórico: 2 segmentos · 8 páginas · 4 KiB = 64 KiB (= 2^16, lo que da la DL).
  Real: la RAM es de 64 KiB → 64 KiB, menos lo que ocupe el SO.

Paso 5: d) fragmentación
  Externa: 0 (la memoria está en marcos).
  Interna: en la última página de cada segmento → como máximo casi 2 páginas
  por proceso: 2 · (4 KiB − 1 byte) ≈ 8 KiB.

Control: coincide con la resolución de la cátedra (8111h, 9333h; marcos 13 y 15) ✓
```

### 3. Ejercicio guiado (Guía de memoria, Ej 4)

> Una máquina tiene direcciones de 18 bits: los primeros 2 identifican el segmento y los últimos 16, el offset. La tabla de segmentos es:
>
> ```
> Segmento   Base     Largo    Protección
>    0       00000h   0ABCDh   Read-only
>    1       1B000h   007FFh   Exec-only
>    2       1B800h   00FFFh   Read-write
>    3       30000h   01234h   Read-write
> ```
>
> ¿Qué sucede cuando el proceso intenta **escribir** en cada una de estas direcciones: 20000h, 10000h, 0BEEFh, 00ACEh?

Es del tipo 1. Pasá cada dirección a 18 bits: los 2 de arriba son el segmento. Después chequeá el límite y el permiso de escritura.

```
Paso 1: 20000h → segmento, offset, límite y permiso
  → ________

Paso 2: 10000h
  → ________

Paso 3: 0BEEFh
  → ________

Paso 4: 00ACEh
  → ________
```

### 4. Práctica

#### Ejercicio extra 1: traducir (Guía de memoria, Ej 3)

> Con la tabla de segmentos siguiente, determine las direcciones físicas de las lógicas (0, 430), (1, 10) y (2, 500).
>
> ```
> Segmento   Base   Largo
>    0        219    600
>    1       2300     14
>    2         90    100
>    3       1327    580
> ```

#### Ejercicio extra 2: reconstruir la tabla (Guía de memoria, Ej 11)

> Una computadora con 64 KB de memoria usa segmentación pura. Un proceso tiene 3 segmentos (código, pila y datos). Los segmentos 0 y 1 están cargados en forma adyacente y el segmento 2 está al final de la memoria. Se sabe que: la DL 200Ah referencia al segmento 1; la DL 000Eh genera la DF 0FAFh; la DL 4077h genera la DF FFF7h; la DL 201Eh genera la DF 0FFFh; la DL 201Fh produciría un segmentation fault; y una escritura sobre la DL 200Ch produciría una interrupción por modo de acceso inválido. a) Reconstruya la tabla de segmentos (base y límite de cada uno). b) ¿Cuál es posiblemente el segmento de código? c) ¿Qué fragmentación genera este esquema?

### 5. Cierre

**Fórmulas**

$$DF = \text{base}_s + \text{offset} \quad (\text{offset} < \text{límite}_s) \qquad \text{base} = DF - \text{offset}$$

```
Segmentación: DL = seg | offset. Fragmentación externa. Permisos por segmento
Segmentación paginada: DL = seg | pág | offset → DF = marco | offset. Fragmentación interna (última pág. de c/seg)
Chequeos al traducir: segmento válido → offset < límite → permiso
```

**Trampas**
- **Chequear solo el límite.** También el permiso: escribir en un segmento de código es una violación aunque el offset sea válido.
- **Suponer la cantidad de bits de segmento.** Sacala de los datos (cantidad de segmentos, o de qué segmento es una DL dada).
- **Decir que la segmentación paginada tiene fragmentación externa.** Divide la memoria en marcos: solo tiene interna.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Qué fragmentación tiene la segmentación y cuál la segmentación paginada? ¿Por qué?
2. (Ejercicio) DL de 16 bits: 2 bits de segmento y 14 de offset. Segmento 1: base 8000h, límite 0400h, RW. ¿A qué DF va 4123h? ¿Y 4500h? (material propio)

## Respuestas del capítulo 4

### 4.1 Ejercicio guiado

```
Paso 1: peor ajuste
  230 → el más grande, 500 → queda 270    Huecos: 150, 400, 250, 100, 270
  90  → 400 → queda 310                   Huecos: 150, 310, 250, 100, 270

Paso 2: 480 → el más grande es 310 → no entra.
  350 → tampoco (310 < 350). Fallan dos.

Paso 3: siguiente ajuste
  230 → desde el inicio: 150 no, 400 sí → queda 170 (la búsqueda queda en el 2º hueco)
  90  → desde el 2º: 170 sí → queda 80

Paso 4: 480 → desde el 2º: 80, 250, 100 no; 500 sí → queda 20
  350 → desde el 5º: 20, (vuelta) 150, 80, 250, 100 → no entra.

Paso 5: mejor ajuste: fue el único que ubicó los cuatro. Peor ajuste partió los
  huecos grandes y después no tuvo lugar para 480.
```

### 4.1 Práctica

```
1. Interna: espacio desperdiciado dentro de lo asignado (el proceso no llena su
   partición). Externa: hay memoria libre suficiente, pero en huecos no contiguos.
   Fijas: interna. Dinámicas: externa.
2. Consolidar es unir dos huecos vecinos cuando se liberan; compactar es mover los
   procesos para juntar todos los huecos. No se puede compactar si las direcciones
   se fijaron al compilar o al cargar (sin reubicación en ejecución).
3. 500 < 1200 → DF = 3000 + 500 = 3500. 1300 ≥ 1200 → error de direccionamiento.
4. Porque deja sobrantes grandes, que después pueden usar otros procesos; el mejor
   ajuste deja sobrantes muy chicos que no sirven para nada.
```

### 4.1 Autoevaluación

```
1. Hay memoria libre suficiente para un proceso, pero dividida en huecos no
   contiguos. Se atenúa consolidando huecos vecinos y compactando.

2. Mejor ajuste: 110 → 120 (queda 10); 190 → 200 (queda 10); 280 → 300 (queda 20).
   Entran todos.
   Primer ajuste: 110 → 300 (queda 190); 190 → ese mismo hueco de 190 (queda 0);
   280 → no entra (los huecos son 0, 120 y 200).
```

### 4.2 Ejercicio guiado

```
Paso 1: 1024 = 2^10 → 10 bits de offset; 8 = 2^3 → 3 bits de página → DL de 13 bits.

Paso 2: 32 = 2^5 → 5 bits de marco → DF de 5 + 10 = 15 bits.

Paso 3: sin memoria virtual todo el proceso tiene que caber en la memoria física:
  DL ≤ DF (acá, 13 ≤ 15).

Paso 4: espacio lógico 2^20 = 1 MiB; memoria real 256 KiB. Sin memoria virtual el
  programa tiene que entrar entero en la RAM → máximo 256 KiB (el menor de los dos).

Paso 5: interna máxima por proceso: casi una página, 4 KiB − 1 byte (4095 bytes).
  Externa: 0.
```

### 4.2 Ejercicio extra 1

```
a) 2^32 / 2^12 = 2^20 entradas · 4 bytes = 4 MiB por proceso.
b) Cada tabla de segundo nivel tiene 2^10 entradas · 4 bytes = 4 KiB (cabe justo en
   una página). La DL queda 10 | 10 | 12.
```

### 4.2 Ejercicio extra 2

```
a) 0,95 · (10 + 80) + 0,05 · (10 + 80 + 80) = 85,5 + 8,5 = 94 ns
b) Sin TLB: 2 · 80 = 160 ns (tabla + dato).
```

### 4.2 Ejercicio extra 3

```
a) Falso: tiene fragmentación interna en la última página de cada proceso (no tiene
   externa).
b) Verdadero: así se comparten bibliotecas o el código de dos instancias; conviene
   que sea de solo lectura.
c) Falso: tiene una entrada por marco de la memoria física, para todo el sistema.
```

### 4.2 Autoevaluación

```
1. La TLB es una caché de traducciones: evita ir a la tabla de páginas en memoria en
   cada acceso (sin ella, cada dato cuesta dos accesos). La paginación jerárquica
   evita tener una tabla enorme y contigua: se pagina la tabla y solo se cargan los
   pedazos que se usan.

2. 16 bits, offset de 12 → 4 bits de página. 3A7Fh → página 3, offset A7Fh.
   Marco 9 → DF = 9A7Fh.
```

### 4.3 Ejercicio guiado

```
Paso 1: 20000h = 10|0000 0000 0000 0000 → segmento 2, offset 0000h < 0FFFh.
  Read-write → la escritura es válida: DF = 1B800h + 0 = 1B800h.

Paso 2: 10000h = 01|0000... → segmento 1, offset 0 < 07FFh, pero es exec-only:
  escribir es una violación de protección (modo de acceso inválido).

Paso 3: 0BEEFh = 00|1011 1110 1110 1111 → segmento 0, offset BEEFh ≥ ABCDh:
  segmentation fault (además el segmento es de solo lectura).

Paso 4: 00ACEh → segmento 0, offset 0ACEh < ABCDh, pero es read-only: la escritura
  es una violación de protección.
```

### 4.3 Ejercicio extra 1

```
(0, 430): 430 < 600 → 219 + 430 = 649
(1, 10):  10 < 14   → 2300 + 10 = 2310
(2, 500): 500 ≥ 100 → dirección inválida (segmentation fault)
```

### 4.3 Ejercicio extra 2

```
a) Como 200Ah es del segmento 1, la DL tiene 3 bits de segmento y 13 de offset
   (200Ah = 001|0 0000 0000 1010).
   000Eh → seg 0, offset Eh, DF 0FAFh → base 0 = 0FAFh − Eh = 0FA1h
   201Eh → seg 1, offset 1Eh, DF 0FFFh → base 1 = 0FFFh − 1Eh = 0FE1h
   201Fh da segmentation fault → límite 1 = 1Fh
   Como 0 y 1 son adyacentes → límite 0 = 0FE1h − 0FA1h = 40h
   4077h → seg 2, offset 77h, DF FFF7h → base 2 = FFF7h − 77h = FF80h;
   está al final de la memoria → límite 2 = FFFFh − FF80h + 1 = 80h

   Segmento   Base    Límite
      0       0FA1h   0040h
      1       0FE1h   001Fh
      2       FF80h   0080h

b) El segmento 1: no admite escritura (200Ch da modo de acceso inválido), como el
   código.
c) Fragmentación externa (los segmentos son de tamaño variable y contiguos).
```

### 4.3 Autoevaluación

```
1. Segmentación: externa, porque los segmentos son de tamaño variable y dejan huecos
   al liberarse. Segmentación paginada: solo interna (última página de cada
   segmento), porque la memoria está dividida en marcos iguales.

2. 4123h = 01|00 0001 0010 0011 → seg 1, offset 0123h < 0400h → DF = 8000h + 123h
   = 8123h. 4500h → seg 1, offset 0500h ≥ 0400h → segmentation fault.
```
