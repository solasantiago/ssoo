# Capítulo 6: File systems (clases 7 y 8)

## 6.1 Archivos, directorios, permisos y links ★★★☆☆ (estimado)

Temas en Lumen: `u7-concepto-tipos-atributos-archivo`, `u7-operaciones-sobre-archivos`, `u7-estructuras-directorio`, `u7-metodos-acceso`, `u7-proteccion-matriz-acceso-acl`, `u7-archivos-mapeados-memoria`

Las estrellas de este capítulo son estimaciones: no hay parciales con fecha del 2do parcial. En el final del 20/02/2024, file systems apareció como verdadero o falso (asignación de bloques); la guía de file system tiene un ejercicio de links.

### 1. Conceptos

**File system (FS).** Es la parte del SO que da el servicio de archivos: almacenar datos y operar con ellos, garantizar su integridad, dar buen desempeño, soportar distintos dispositivos y varios usuarios, y ofrecer una interfaz estándar a los procesos.

**Archivo.** Un conjunto de datos relacionados, con nombre, en almacenamiento secundario y de larga duración. Se comparte entre procesos, con permisos. Cada archivo se administra con su **FCB** (File Control Block): atributos como tamaño, dueño, permisos, fechas y dónde están sus bloques. En ext2, el FCB es el **inodo**.

**Directorio.** Es un archivo que contiene la lista de nombres de otros archivos (o directorios) y lo necesario para encontrarlos. Traduce el nombre que usa el usuario al archivo. Estructuras: en **árbol** (rutas absolutas desde la raíz o relativas al directorio actual) o en **grafo acíclico** (un archivo en dos directorios, con links).

**Operaciones.** Crear, eliminar, abrir, cerrar, leer, escribir, posicionar el puntero (seek) y truncar. Las compuestas (copiar, mover, renombrar) se arman con estas. **Abrir** busca el archivo en el directorio una sola vez y lo registra como abierto, para no buscarlo en cada lectura.

**Tablas de archivos abiertos.** Como un proceso abre varios archivos y un archivo lo pueden abrir varios procesos, hay dos tablas:
- **Tabla global** (una para el sistema): una entrada por archivo abierto, con la información del FCB, igual para todos, y un **contador de aperturas**. La entrada se borra cuando el contador llega a 0.
- **Tabla por proceso:** una entrada por cada archivo que abrió ese proceso, con lo propio de esa apertura: modo (lectura o escritura) y puntero de posición. Apunta a la entrada de la tabla global.

**Locks.** Regulan el acceso concurrente a un archivo:
- **Compartido** (de lectura): muchos a la vez. **Exclusivo** (de escritura): uno solo, y nadie más mientras lo tiene.
- **Obligatorio** (mandatory): el SO impide el acceso a quien no respeta el lock. **Sugerido** (advisory): el SO informa el estado y el programador se encarga de respetarlo.

**Protección.** Quién puede hacer qué con cada archivo:
- **Matriz de acceso** (usuario × recurso → permisos): muy detallada, pero ocupa mucho y casi toda está vacía.
- **ACL** (lista de control de acceso): por cada archivo, la lista de usuarios con sus permisos. Ocupa menos.
- **Dueño, grupo y resto** (Unix): tres grupos de permisos rwx. Se puede combinar con ACL si no alcanza.

```
chmod 755 archivo → rwx r-x r-x   (r = 4, w = 2, x = 1; dueño, grupo, resto)
chmod g+w archivo → agrega escritura al grupo      chmod o-rw → saca lectura y escritura al resto
En un directorio: r = listar (ls), w = crear y borrar archivos adentro, x = entrar (cd)
```

**Hard link y soft link.**
- **Hard link:** otra entrada de directorio que apunta al **mismo inodo**. No hay "original" y "copia": son dos nombres del mismo archivo. El inodo tiene un **contador de referencias**, y el archivo se borra de verdad cuando llega a 0. No puede cruzar file systems (los números de inodo son de cada FS).
- **Soft link (simbólico):** un archivo aparte, con su **propio inodo**, cuyo contenido es la **ruta** al otro archivo. Puede cruzar file systems. Si se borra el archivo apuntado, el soft link queda roto.

```
ls -li
7775 -rw-r--r-- 2 ... fileloco          ← mismo inodo (7775), contador 2
7775 -rw-r--r-- 2 ... hl_fileloco       ← hard link
7777 lrwxrwxrwx 1 ... sl_fileloco -> fileloco   ← inodo propio, tipo l
```

**Journaling.** Las estructuras del FS (bitmap, directorios, FCB) suelen estar más al día en memoria que en disco; un corte puede dejarlas inconsistentes. Con journaling, cada cambio se escribe primero en un registro (journal) como una **transacción** que termina en un commit; si el sistema se cae, al volver se rehacen las transacciones confirmadas y se descartan las incompletas.

**Archivos mapeados a memoria.** Se asocia una parte del espacio de direcciones del proceso con el archivo: cada bloque corresponde a una página. Leer y escribir el archivo pasa a ser leer y escribir memoria, sin syscalls read y write, y varios procesos pueden compartirlo compartiendo las páginas. Las escrituras llegan al disco después.

**Los tipos de pregunta que toman:**
1. **Links:** qué link crear, qué pasa al borrar el original o el link, cuántos archivos hay.
2. **Permisos:** interpretar o armar un chmod; qué significa cada permiso en un directorio.
3. **Tablas de archivos abiertos:** qué va en cada una y cuándo se borra una entrada.
4. **Teoría:** locks, journaling, archivos mapeados, matriz de acceso contra ACL.

### 2. Ejemplo resuelto (Guía de file system, Ej 11)

> En un sistema Linux hay dos versiones de Java instaladas, en `/usr/lib/java-8/bin/java` y `/usr/lib/java-9/bin/java`. Se quiere configurar la versión por defecto con un link en `/etc/alternatives/java` que apunte a la versión elegida (al principio, java-8, pero que se pueda cambiar después).
> a) ¿Qué tipo de link crearía, sabiendo que la versión 9 está en otro volumen? b) En base al punto anterior, ¿cuántos archivos existen en el sistema que permiten ejecutar java-8? c) Resuelva los puntos anteriores suponiendo que la versión 9 está en el mismo volumen que la 8. d) En base al punto a (cada ítem es independiente): ¿qué pasa si se elimina `/usr/lib/java-8/bin/java`? ¿Y si se elimina `/etc/alternatives/java`? ¿Y si se eliminan los dos? e) Repita d en base a c.

Es del tipo 1. La clave es si el link puede cruzar volúmenes y si comparte el inodo con el original.

```
Paso 1: a) link a otro volumen
  Solo soft link: un hard link no puede cruzar file systems (el número de inodo es
  de cada FS), y el link tiene que poder apuntar después a java-9.

Paso 2: b) archivos que ejecutan java-8
  2: el original y el soft link, cada uno con su inodo.

Paso 3: c) mismo volumen
  Sirven los dos tipos. Con hard link hay un solo archivo (un inodo) con dos nombres.

Paso 4: d) con soft link
  i)   Borrar el original: el link queda roto (apunta a una ruta que no existe).
  ii)  Borrar el link: el original no se entera.
  iii) Borrar los dos: se pierde el archivo.

Paso 5: e) con hard link
  i)   Borrar /usr/lib/java-8/bin/java: el contenido sigue accesible desde el otro
       nombre; el contador del inodo baja a 1.
  ii)  Borrar /etc/alternatives/java: lo mismo (no hay original ni copia).
  iii) Borrar los dos: el contador llega a 0 y recién ahí se libera el archivo.

Control: coincide con la resolución de la cátedra ✓
```

### 3. Ejercicio guiado (material propio)

> Un archivo `notas.txt` tiene permisos `-rw-r-----` y el directorio `/datos`, `drwxr-x--x`. a) ¿Qué número de chmod corresponde a cada uno? b) ¿Qué puede hacer un usuario del grupo con `notas.txt`? ¿Y uno del resto? c) ¿Puede un usuario del resto entrar a `/datos` con cd? ¿Puede listarlo con ls? d) El dueño de `notas.txt` ejecuta `chmod o+r notas.txt`: ¿cómo quedan los permisos?

Es del tipo 2. Separá los 9 caracteres en tres grupos (dueño, grupo, resto) y sumá r = 4, w = 2, x = 1 en cada uno.

```
Paso 1: a) número de cada uno
  → ________

Paso 2: b) grupo y resto con notas.txt
  → ________

Paso 3: c) resto con /datos (cd y ls)
  → ________

Paso 4: d) después de chmod o+r
  → ________
```

### 4. Práctica

Respondé cada una en dos o tres líneas antes de mirar las respuestas.

1. Dos procesos abren el mismo archivo, uno para leer y otro para escribir. ¿Cuántas entradas hay en la tabla global y cuántas en las tablas por proceso? ¿Qué guarda cada una?
2. ¿Qué diferencia hay entre un lock obligatorio y uno sugerido?
3. ¿Qué ventaja tiene una ACL frente a la matriz de acceso?
4. ¿Qué problema resuelve el journaling y cómo?
5. ¿Qué ventaja tienen los archivos mapeados a memoria?

### 5. Cierre

**Fórmulas**

```
chmod: r = 4, w = 2, x = 1 (dueño | grupo | resto). Directorio: r = ls, w = crear/borrar, x = cd
Hard link: mismo inodo, contador de referencias, no cruza FS. Soft link: inodo propio, guarda la ruta, cruza FS
Tabla global: FCB + contador de aperturas. Tabla por proceso: modo + puntero
```

**Trampas**
- **Decir que el hard link es una copia.** Es el mismo archivo con otro nombre; no hay original.
- **Decir que borrar el original rompe un hard link.** Rompe los soft links; con hard link el contenido sigue mientras el contador sea mayor que 0.
- **Poner el puntero de posición en la tabla global.** Es de cada apertura: va en la tabla por proceso.
- **Olvidar que x en un directorio es entrar**, no ejecutar.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) Diferenciá hard link y soft link: inodo, contador, qué pasa al borrar el original, si cruzan file systems.
2. (Ejercicio) ¿Qué permisos deja `chmod 640 f`? Después se hace `chmod g+x,o+r f`: ¿qué número queda? (material propio)

## 6.2 Asignación de bloques y FAT ★★★★☆ (estimado)

Temas en Lumen: `u7-asignacion-espacio-gestion-espacio`, `u7-implementaciones-actuales-sistemas-archivos`

La clase 8 es entera de FAT y ext2, y la guía tiene 5 ejercicios de FAT. En el final del 20/02/2024 apareció la asignación de bloques como verdadero o falso.

### 1. Conceptos

**Bloques.** El disco físico se divide en **sectores**; el FS trabaja con **bloques lógicos** (en FAT se llaman **clusters**), de N sectores. El bloque es la unidad mínima de asignación: un archivo ocupa bloques enteros, y lo que sobra del último es **fragmentación interna**.

**Organización del disco.** El disco tiene un MBR y particiones; cada partición formateada es un **volumen**, con un bloque de arranque, la información de control del volumen (siempre en memoria), la metadata (estructuras de espacio libre, FCB) y los datos.

**Asignación contigua.** Cada archivo ocupa bloques seguidos; el FCB guarda el bloque inicial y la cantidad. Es rápida (el cabezal casi no se mueve) y buena para acceso secuencial y directo, pero hay que saber el tamaño al crear el archivo, cuesta agrandarlo y tiene **fragmentación externa** (hay que compactar).

**Asignación enlazada.** Cada bloque tiene un puntero al siguiente. No tiene fragmentación externa y el archivo crece fácil, pero es mala para acceso directo (para llegar al bloque n hay que leer los n anteriores), los punteros ocupan espacio y, si se corrompe uno, se pierde el resto del archivo.

**Asignación indexada.** Cada archivo tiene un **bloque de índice** con los punteros a todos sus bloques. Es buena para acceso secuencial y directo, sin fragmentación externa, pero los punteros ocupan más. Si el índice queda chico, se enlazan varios bloques de índice, se usa un índice multinivel o un esquema combinado (algunos punteros directos y otros a bloques de punteros): así funciona el inodo de ext2 (bloque 6.3).

**Espacio libre.** Se administra con un **bitmap** (un bit por bloque), con una lista enlazada de bloques libres, o con variantes (bloques indexados, lista de bloques, lista de tramos contiguos con bloque inicial y cantidad).

**FAT.** Es una variante de la asignación **enlazada**: los punteros no están en los bloques, sino en una tabla (la FAT) al principio del volumen, que se copia a memoria al arrancar y tiene una copia en disco por seguridad. Hay **una entrada por cluster**, y cada entrada dice cuál es el cluster siguiente del archivo (o fin de archivo, o libre). Como la tabla está en memoria, se puede seguir la cadena hasta el cluster n sin leer los bloques: permite acceso directo en un esquema enlazado. No hay FCB: los atributos y el primer cluster van en la **entrada de directorio**. Para buscar un cluster libre se recorre la tabla.

```
FAT (entrada = cluster siguiente)          Directorio: "a.txt", primer cluster 2
cluster: 0    1    2    3    4    5        → a.txt ocupa 2 → 5 → 3
valor:   -   libre  5  EOF libre  3
```

**Tamaños en FAT.** Con entradas de n bits se direccionan $2^n$ clusters (en FAT32, las entradas son de 32 bits, pero se usan 28):

$$\text{Tam. máx. del FS} = 2^{\text{bits usados}} \cdot \text{tam. cluster} \qquad \text{Tam. FAT} = \text{cant. entradas} \cdot \text{tam. entrada}$$

```
FAT12: 2^12 clusters   FAT16: 2^16   FAT32: 2^28 (entradas de 32 bits, se usan 28)
El tamaño teórico de un archivo es todo el FS; en FAT32, el campo de tamaño de la entrada
de directorio lo limita a 4 GiB (diapositivas de la clase).
```

Por ejemplo, FAT16 con clusters de 4 KiB: $2^{16} \cdot 2^{12} = 2^{28}$ = 256 MiB.

**Real o teórico.** El máximo **teórico** sale de la fórmula; el **real** es el menor entre el teórico y el tamaño del disco.

**Los tipos de ejercicio que toman:**
1. **Máximo direccionable** (teórico y real) y tamaño máximo de archivo.
2. **Tamaño de la FAT** y qué porcentaje del disco ocupa; bits desperdiciados por entrada.
3. **Tamaño mínimo de cluster** para cubrir un disco, y la fragmentación interna que genera.
4. **Comparar esquemas** de asignación (contigua, enlazada, indexada) y de espacio libre.

### 2. Ejemplo resuelto (Guía de file system, Ej 3)

> Un disco de 8 GiB se formatea con FAT32 con clusters de 4 KiB. Descartando la información administrativa: a) ¿Cuántas entradas tendría la FAT? b) ¿Qué porcentaje del disco ocuparía la FAT? c) ¿Cuántos bits de cada entrada se desperdiciarían?

Es del tipo 2. FAT32 podría tener $2^{28}$ entradas, pero solo hacen falta tantas como clusters tenga el disco.

```
Paso 1: a) cantidad de clusters (= entradas necesarias)
  8 GiB / 4 KiB = 2^33 / 2^12 = 2^21 = 2.097.152 entradas

Paso 2: b) tamaño de la FAT
  2^21 entradas · 32 bits (4 bytes) = 2^23 bytes = 8 MiB
  Con la copia de seguridad: 2 · 8 MiB = 16 MiB

Paso 3: b) porcentaje
  16 MiB / 8 GiB = 2^24 / 2^33 = 2^−9 ≈ 0,195 %   (una sola FAT: ≈ 0,098 %)

Paso 4: c) bits desperdiciados
  Se necesitan 21 bits para numerar 2^21 clusters. De los 28 que usa FAT32 sobran 7,
  y los 4 de arriba FAT32 no los usa nunca: 7 + 4 = 11 bits.

Control: coincide con la resolución de la cátedra (2^21 entradas, 0,195 %, 11 bits) ✓
```

### 3. Ejercicio guiado (Guía de file system, Ej 4)

> Se tiene un disco de 4 GiB y se desea formatear con FAT16. a) ¿Cuál sería el tamaño mínimo de cluster para poder direccionar todo el disco (descartando la información administrativa)? b) Si se guardan tres archivos de 1 KiB, 20 KiB y 1 MiB, ¿qué espacio en disco ocuparía cada uno? c) ¿Qué desventaja principal tiene este formateo?

Es del tipo 3. Despejá el cluster de la fórmula del máximo direccionable.

```
Paso 1: a) cluster mínimo = tamaño del disco / 2^16
  → ________

Paso 2: b) clusters y espacio de cada archivo
  → ________

Paso 3: c) desventaja
  → ________
```

### 4. Práctica

#### Ejercicio extra 1: agrandar el direccionamiento (Guía de file system, Ej 2)

> Un FS FAT12 tiene clusters de 8 KiB. a) ¿Cuál es el espacio máximo direccionable teórico? b) Para direccionar 128 MiB, ¿qué dos cambios se le podrían hacer? c) ¿Cuál de los dos es más eficiente en términos de 1) aprovechamiento del disco y 2) tiempo de respuesta al contar los clusters libres?

#### Ejercicio extra 2: teórico y real (Guía de file system, Ej 5)

> Un disco de 512 GiB se formatea con FAT32. Indique el máximo espacio direccionable y el tamaño máximo de un archivo (teórico y real) con a) clusters de 1 KiB y b) clusters de 4 KiB.

#### Ejercicio extra 3: teoría (Guía de file system, Ej 1, y final del 20/02/2024, teoría 5)

> a) ¿Qué tipo de asignación tiene FAT: contigua, encadenada o indexada? (Pista: qué tiene que hacer el FS para ubicar el enésimo cluster de un archivo). b) Verdadero o falso, justificando: "La compactación es una estrategia útil en todos los esquemas de asignación de bloques en disco."

### 5. Cierre

**Fórmulas**

$$\text{Tam. máx. FS} = 2^{\text{bits}} \cdot \text{tam. cluster} \qquad \text{Tam. FAT} = \text{entradas} \cdot \text{tam. entrada} \qquad \text{cluster mín.} = \frac{\text{disco}}{2^{\text{bits}}}$$

```
FAT12: 12 bits   FAT16: 16 bits   FAT32: 28 bits usados de 32. Hay una copia de la FAT.
Real = mín(teórico, disco).  Archivo en FAT32: máx. 4 GiB por la entrada de directorio.
Contigua: fragm. externa, buen acceso. Enlazada: sin acceso directo. Indexada: bloque de índice.
```

**Trampas**
- **Usar 32 bits en FAT32.** Se usan 28.
- **Olvidar la copia de la FAT** al calcular cuánto ocupa (si el enunciado la pide).
- **Dar el teórico como real.** El real no puede superar el disco.
- **Decir que FAT es indexada.** Es enlazada, con los punteros en una tabla.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Por qué FAT permite acceso directo si es una asignación enlazada? ¿Dónde guarda los atributos de cada archivo?
2. (Ejercicio) FAT16 con clusters de 2 KiB: ¿máximo direccionable? ¿Cuánto ocupa la FAT (una copia)? (material propio)

## 6.3 ext2: inodos y punteros ★★★★☆ (estimado)

Temas en Lumen: `u7-asignacion-espacio-gestion-espacio`, `u7-implementaciones-actuales-sistemas-archivos`

La guía de file system tiene 5 ejercicios de ext2 (tamaño máximo con punteros directos e indirectos, accesos a bloques).

### 1. Conceptos

**ext2.** Usa asignación **indexada** combinada: cada archivo tiene un **inodo** (su FCB) con la metadata (tipo, permisos, tamaño, fechas, contador de links) y punteros a bloques: algunos **directos** (a bloques de datos) y otros **indirectos** (a bloques de punteros).

```
inodo: 12 directos ─────────────────────────────→ datos
       1 indirecto simple ─→ [bloque de punteros] ─→ datos
       1 indirecto doble   ─→ [punteros] ─→ [punteros] ─→ datos
       1 indirecto triple  ─→ [punteros] ─→ [punteros] ─→ [punteros] ─→ datos
```

**Estructura del volumen.** Bloque de arranque y **grupos de bloques**; cada grupo tiene una copia del **superbloque** (totales de bloques e inodos, libres, tamaño de bloque y de inodo), los **descriptores de grupo**, un **bitmap de bloques**, un **bitmap de inodos**, la **tabla de inodos** y los bloques de datos. Los directorios son listas enlazadas de entradas de longitud variable (nombre y número de inodo).

**Punteros por bloque.** Un bloque de punteros tiene:

$$P = \frac{\text{tam. bloque}}{\text{tam. puntero}}$$

Por ejemplo, con bloques de 1 KiB y punteros de 4 bytes, P = 256.

**Tamaño máximo de archivo.** Cada tipo de puntero direcciona $P^{\text{nivel}}$ bloques de datos (nivel 0 = directo):

$$\text{Tam. máx.} = \left(D + S \cdot P + Dd \cdot P^2 + T \cdot P^3\right) \cdot \text{tam. bloque}$$

con D directos, S indirectos simples, Dd dobles y T triples. El máximo **real** tiene además dos límites: el disco y lo que pueden numerar los punteros ($2^{\text{bits del puntero}}$ bloques).

**Máximo direccionable del FS.**

$$\text{Tam. máx. FS} = 2^{\text{bits del puntero}} \cdot \text{tam. bloque}$$

**Accesos a bloques.** Para leer un byte, primero se calcula en qué bloque del archivo está (byte / tam. bloque, parte entera, contando desde 0) y con qué puntero se llega:

```
Bloques 0 a D−1                                 → directos: 1 acceso (el dato)
Bloques D a D + P − 1                           → indirecto simple: 2 accesos
Bloques D + P a D + P + P² − 1                  → indirecto doble: 3 accesos
El siguiente tramo, de P³ bloques               → indirecto triple: 4 accesos
(sin contar el inodo, que se supone en memoria)
```

Para leer un rango, se suman los bloques de datos y cada bloque de punteros que haya que leer (una vez).

**Los tipos de ejercicio que toman:**
1. **Tamaño máximo de archivo** con una conformación de punteros (teórico y real).
2. **Diseñar el inodo:** la mínima cantidad de punteros para llegar a un tamaño.
3. **Accesos a bloques** para leer un byte o un rango.
4. **Máximo direccionable** del FS según el tamaño del puntero.

### 2. Ejemplo resuelto (Guía de file system, Ej 7)

> En un sistema con ext2, los bloques son de 1 KiB y los punteros de 4 bytes. Indique el tamaño máximo teórico de un archivo con a) solamente 12 punteros directos; b) 12 directos y 1 indirecto; c) 12 directos, 1 indirecto, 1 doblemente indirecto y 1 triplemente indirecto.

Es del tipo 1. Primero, cuántos punteros entran en un bloque; después se suma lo que direcciona cada puntero.

```
Paso 1: punteros por bloque
  P = 1 KiB / 4 B = 2^10 / 2^2 = 2^8 = 256

Paso 2: a) 12 directos
  12 · 1 KiB = 12 KiB

Paso 3: b) + 1 indirecto simple
  12 KiB + 256 · 1 KiB = 12 KiB + 256 KiB = 268 KiB

Paso 4: c) + doble y triple
  doble:  256^2 · 1 KiB = 2^16 · 2^10 = 2^26 = 64 MiB
  triple: 256^3 · 1 KiB = 2^24 · 2^10 = 2^34 = 16 GiB
  Total: 16 GiB + 64 MiB + 256 KiB + 12 KiB ≈ 16 GiB

Paso 5: máximo direccionable del FS (extra)
  Punteros de 32 bits → 2^32 bloques · 1 KiB = 2^42 = 4 TiB

Control: coincide con la resolución de la cátedra (12 KiB, 268 KiB, ≈ 16 GiB) ✓
```

### 3. Ejercicio guiado (Guía de file system, Ej 9)

> Un sistema ext2 tiene bloques de 4 KiB y punteros de 8 bytes. El inodo tiene 12 punteros directos, 1 indirecto, 1 indirecto doble y 1 indirecto triple. ¿Cuántos accesos a bloques hacen falta para leer a) el byte número 16.777.227 de un archivo; b) desde el byte 0 hasta el 250.180?

Es del tipo 3. Calculá P, después en qué bloque del archivo cae el byte, y con qué puntero se llega.

```
Paso 1: punteros por bloque
  → ________

Paso 2: rangos de bloques de cada tipo de puntero
  → ________

Paso 3: a) bloque del byte 16.777.227 y cuántos accesos
  → ________

Paso 4: b) último bloque del rango y cuántos bloques de datos se leen
  → ________

Paso 5: b) bloques de punteros que hay que leer y total de accesos
  → ________
```

### 4. Práctica

#### Ejercicio extra 1: diseñar el inodo (Guía de file system, Ej 8)

> Un FS ext2 tiene bloques de 1 KiB y punteros de 8 bytes. a) ¿Cuál es la cantidad mínima de punteros en el inodo para direccionar hasta 30 MiB por archivo? Puede diseñar el inodo como quiera, con no más de 10 directos, 2 indirectos simples, 2 dobles y 2 triples. b) ¿Sería eficiente ese esquema si casi todos los archivos fueran de hasta 4 KiB?

#### Ejercicio extra 2: teórico y real (Guía de file system, Ej 10)

> Indique el máximo espacio direccionable y el tamaño máximo de un archivo (teórico y real) de un ext2 en un disco de 10 TiB, con inodos de 10 punteros directos, 2 indirectos dobles y 2 indirectos triples, bloques de 4 KiB y punteros de 8 bytes.

#### Ejercicio extra 3: teoría (Guía de file system, Ej 6)

> ¿Qué tipo de asignación de bloques tiene ext2: contigua, encadenada o indexada? ¿Qué ventaja tiene combinar punteros directos e indirectos?

### 5. Cierre

**Fórmulas**

$$P = \frac{\text{tam. bloque}}{\text{tam. puntero}} \qquad \text{Tam. máx.} = (D + S \cdot P + Dd \cdot P^2 + T \cdot P^3) \cdot \text{tam. bloque} \qquad \text{FS máx.} = 2^{\text{bits puntero}} \cdot \text{tam. bloque}$$

```
Bloque de un byte = ⌊byte / tam. bloque⌋ (desde 0)
Accesos (inodo en memoria): directo 1, simple 2, doble 3, triple 4
Real = mín(teórico, disco, lo que numeran los punteros)
```

**Trampas**
- **Contar los bloques desde 1.** El byte 0 está en el bloque 0; el byte 4096 (con bloques de 4 KiB), en el bloque 1.
- **Olvidar sumar los tramos anteriores** al decidir con qué puntero se llega a un bloque (el doble empieza después de los directos y del simple).
- **Contar el bloque de punteros en cada bloque de datos.** En un rango, cada bloque de punteros se lee una vez.
- **Multiplicar mal las potencias.** Pasá todo a potencias de 2: $256^3 = 2^{24}$.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Qué guarda el inodo? ¿Por qué ext2 combina punteros directos e indirectos?
2. (Ejercicio) Bloques de 2 KiB, punteros de 4 bytes, inodo con 10 directos y 1 indirecto simple. ¿Tamaño máximo de archivo? ¿Cuántos accesos para leer el byte 30.000? (material propio)

## Respuestas del capítulo 6

### 6.1 Ejercicio guiado

```
Paso 1: -rw-r----- → rw- = 6, r-- = 4, --- = 0 → 640
        drwxr-x--x → rwx = 7, r-x = 5, --x = 1 → 751
Paso 2: el grupo puede leer notas.txt (r); el resto no puede hacer nada.
Paso 3: el resto tiene solo x en /datos: puede entrar con cd (y abrir un archivo si
  sabe su nombre y tiene permiso sobre él), pero no puede listarlo con ls (no tiene r).
Paso 4: chmod o+r agrega lectura al resto → -rw-r--r-- (644).
```

### 6.1 Práctica

```
1. Una entrada en la tabla global (el archivo, con el contador de aperturas en 2) y
   una en la tabla de cada proceso (dos en total), cada una con su modo (lectura o
   escritura) y su puntero de posición.
2. El obligatorio lo hace cumplir el SO: nadie accede si no respeta el lock. El
   sugerido solo informa; si un programa no lo consulta, puede acceder igual.
3. Ocupa mucho menos: solo guarda los usuarios que tienen algún permiso sobre cada
   archivo, en lugar de una matriz con casi todas las celdas vacías.
4. Que un corte deje inconsistentes las estructuras del FS. Los cambios se escriben
   primero como transacciones en un registro; al volver, se rehacen las confirmadas.
5. Leer y escribir el archivo es acceder a memoria: se evitan las syscalls read y
   write, y varios procesos lo comparten compartiendo páginas.
```

### 6.1 Autoevaluación

```
1. Hard link: otra entrada que apunta al mismo inodo; el inodo cuenta las referencias;
   si se borra "el original" el contenido sigue; no cruza FS. Soft link: un archivo con
   inodo propio que guarda la ruta; si se borra el original queda roto; puede cruzar FS.
2. 640 → rw-r-----. Después de g+x y o+r → rw-r-xr-- → 654.
```

### 6.2 Ejercicio guiado

```
Paso 1: 4 GiB / 2^16 = 2^32 / 2^16 = 2^16 bytes = 64 KiB.
Paso 2: 1 KiB → 1 cluster → ocupa 64 KiB. 20 KiB → 1 cluster → 64 KiB.
  1 MiB = 1024 KiB → 1024 / 64 = 16 clusters → 1 MiB justo.
Paso 3: la fragmentación interna: con clusters de 64 KiB, cada archivo chico
  desperdicia casi todo su cluster (el de 1 KiB desperdicia 63 KiB).
```

### 6.2 Ejercicio extra 1

```
a) 2^12 · 8 KiB = 2^12 · 2^13 = 2^25 = 32 MiB.
b) 128 MiB = 2^27: agrandar el cluster a 2^15 = 32 KiB (con FAT12), o pasar a FAT16
   (con 8 KiB llega a 2^29 = 512 MiB).
c) 1) Aprovechamiento: pasar a FAT16, porque clusters más grandes dan más
   fragmentación interna. 2) Contar clusters libres: agrandar el cluster, porque hay
   menos clusters (menos entradas) para recorrer.
```

### 6.2 Ejercicio extra 2

```
a) Clusters de 1 KiB: 2^28 · 2^10 = 2^38 = 256 GiB, teórico y real (es menor que el
   disco). Archivo: teórico 256 GiB (todo el FS).
b) Clusters de 4 KiB: 2^28 · 2^12 = 2^40 = 1 TiB teórico; real 512 GiB (el disco).
   Archivo: teórico 1 TiB, real 512 GiB.
(La resolución de la guía toma el archivo igual al FS. Ojo: según la clase, en FAT32
el campo de tamaño de la entrada de directorio limita cada archivo a 4 GiB.)
```

### 6.2 Ejercicio extra 3

```
a) Encadenada (enlazada): cada entrada de la FAT dice cuál es el cluster siguiente.
   Para llegar al enésimo cluster hay que seguir la cadena, pero como la FAT está en
   memoria no hace falta leer los bloques del disco.
b) Falso (según la cátedra, se acepta también verdadero bien justificado): la
   compactación sirve en la asignación contigua, que sufre fragmentación externa; en
   la enlazada y la indexada cualquier bloque libre sirve. (Tener los bloques juntos
   igual mejora los tiempos de acceso: por eso también puede justificarse verdadero.)
```

### 6.2 Autoevaluación

```
1. Porque la cadena de clusters está en la FAT, que se carga en memoria: se sigue la
   cadena en RAM sin leer los bloques. Los atributos van en la entrada de directorio
   (no hay FCB).
2. 2^16 · 2^11 = 2^27 = 128 MiB. FAT: 2^16 entradas · 2 bytes = 128 KiB.
```

### 6.3 Ejercicio guiado

```
Paso 1: P = 4 KiB / 8 B = 2^12 / 2^3 = 2^9 = 512.

Paso 2: directos: bloques 0 a 11. Simple: 12 a 523 (512 bloques).
  Doble: 524 a 524 + 512^2 − 1 = 262.667. Triple: desde 262.668.

Paso 3: a) 16.777.227 / 4096 = 4096,0027 → bloque 4096 (el 4097º, contando desde 0).
  4096 está en el tramo del indirecto doble → 3 accesos: bloque de punteros doble,
  bloque de punteros simple y bloque de datos.

Paso 4: b) 250.180 / 4096 = 61,08 → último bloque: 61 → 62 bloques de datos (0 a 61).

Paso 5: los bloques 12 a 61 se leen con el indirecto simple → 1 bloque de punteros.
  Total: 62 + 1 = 63 accesos (12 con los directos y 50 con el simple, más el bloque
  de punteros).
```

### 6.3 Ejercicio extra 1

```
a) P = 1 KiB / 8 B = 128.
   10 directos + 2 simples = 10 KiB + 2 · 128 KiB = 266 KiB (no alcanza).
   1 doble = 128^2 · 1 KiB = 16 MiB; 2 dobles = 32 MiB ≥ 30 MiB.
   1 triple = 128^3 · 1 KiB = 2 GiB, alcanza y sobra.
   La mínima cantidad de punteros es 1: un solo indirecto triple.
b) No: para leer un archivo de 4 KiB con solo un triple hay que leer 3 bloques de
   punteros más los 4 de datos (7 accesos). Para archivos chicos convienen punteros
   directos.
```

### 6.3 Ejercicio extra 2

```
P = 4 KiB / 8 B = 512.
Archivo: 10 · 4 KiB + 2 · 512^2 · 4 KiB + 2 · 512^3 · 4 KiB
       = 40 KiB + 2^31 (2 GiB) + 2^40 (1 TiB) ≈ 1 TiB (teórico).
       Como es menor que el disco (10 TiB), el real también es ≈ 1 TiB.
FS: punteros de 64 bits → 2^64 · 2^12 = 2^76 bytes teóricos (64 ZiB); real, 10 TiB
    (el disco).
```

### 6.3 Ejercicio extra 3

```
Indexada (combinada o multinivel): el inodo tiene punteros a los bloques. Los
directos hacen que los archivos chicos se lean rápido (sin bloques de punteros), y
los indirectos permiten archivos muy grandes sin agrandar el inodo.
```

### 6.3 Autoevaluación

```
1. La metadata del archivo (tipo, permisos, dueño, tamaño, fechas, contador de links)
   y los punteros a sus bloques. Combina: directos para que los archivos chicos no
   necesiten bloques de punteros, e indirectos para llegar a archivos grandes.
2. P = 2 KiB / 4 B = 512. Máximo: (10 + 512) · 2 KiB = 1044 KiB.
   Byte 30.000 → bloque 30.000 / 2048 = 14 → con el indirecto simple (10 a 521)
   → 2 accesos.
```
