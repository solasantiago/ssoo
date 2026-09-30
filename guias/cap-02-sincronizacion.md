# Capítulo 2: Sincronización (clase 3)

## 2.1 Condición de carrera y sección crítica ★★★☆☆ (estimado)

Temas en Lumen: `u4-grafos-precedencia-condiciones-bernstein`, `u4-problema-region-critica`, `u4-espera-activa-alternancia-peterson`, `u4-mecanismos-provistos-hardware`, `u4-monitores`, `u4-ipc-paso-mensajes`

De los parciales con fecha no se conoce la teoría, así que las estrellas son una estimación. En el único examen completo que hay (el final del 20/02/2024), dos de los cinco verdaderos o falsos son de este bloque.

### 1. Conceptos

**Condición de carrera.** Varios procesos o hilos usan datos compartidos a la vez, y el resultado depende del orden en que se intercalan. Pasa porque una línea como `x++` no es atómica: en la CPU son tres instrucciones.

```
Hilo 1: x++                  Hilo 2: x--             (x = 5)
  r1 = x        → 5
                               r2 = x      → 5
  r1 = r1 + 1   → 6
                               r2 = r2 - 1 → 4
  x = r1        → x = 6
                               x = r2      → x = 4   (debería quedar 5)
```

**Cuándo hay que sincronizar: condiciones de Bernstein.** Hay riesgo de condición de carrera si más de un proceso usa el mismo recurso, al menos uno lo modifica y los accesos son concurrentes. Con R el conjunto de lectura y W el de escritura de cada proceso, **no** hace falta sincronizar A y B si se cumplen las tres:

$$W_A \cap W_B = \varnothing \qquad W_A \cap R_B = \varnothing \qquad R_A \cap W_B = \varnothing$$

Es decir: si solo comparten lecturas, no hay problema. Por ejemplo, con A: `a = b + c` y B: `d = b * c`, $R_A = \{b, c\}$, $W_A = \{a\}$, $R_B = \{b, c\}$, $W_B = \{d\}$: las tres intersecciones son vacías y pueden ejecutar en cualquier orden.

**Región (sección) crítica.** Es el tramo de código que usa el recurso compartido. Tiene que ejecutarse de forma atómica respecto de los otros procesos y ser **lo más chica posible**. Se protege con un protocolo:

```
sección de entrada     ← pide permiso
SECCIÓN CRÍTICA        ← uno por vez
sección de salida      ← libera
sección restante
```

**Requisitos de una solución.** Toda solución al problema de la sección crítica tiene que cumplir:
1. **Mutua exclusión:** uno solo por vez en la sección crítica.
2. **Progreso:** si nadie está en la sección crítica, deciden quién entra solo los que quieren entrar, y la decisión no se posterga para siempre.
3. **Espera limitada:** hay un límite de veces que otros entran antes que uno que ya pidió (no hay inanición).
4. **Velocidad:** funciona sin importar la velocidad de los procesos ni cuánto usen la sección crítica.

**Soluciones por software.** Con variables compartidas y espera activa:
- **Alternancia estricta** (`turno`): cumple mutua exclusión, pero no progreso. Un proceso no puede entrar dos veces seguidas si el otro no entró.
- **Vector de interesados** (`interesado[i] = TRUE; while (interesado[j]);`): cumple mutua exclusión, pero si los dos marcan interés a la vez, quedan los dos en el while para siempre.
- **Peterson:** combina las dos (interesado y turno). Cumple los tres requisitos, pero sirve solo para **dos** procesos, supone que las operaciones son atómicas y usa espera activa.

**Soluciones por hardware.**
- **Deshabilitar interrupciones:** nadie puede sacar al proceso de la CPU dentro de la sección crítica. Es peligroso en modo usuario y no sirve en multiprocesador (las otras CPU siguen).
- **Instrucciones atómicas** (`TestAndSet`, `swap`): leen y modifican una variable en una sola instrucción. Son simples y sirven en multiprocesador, pero tienen espera activa.

```
while (TestAndSet(&lock));    // espera activa hasta que lock valía FALSE
    SECCIÓN CRÍTICA
lock = FALSE;
```

**Semáforos.** Son una variable entera a la que solo se accede con dos syscalls atómicas: `wait` (pide, puede bloquear) y `signal` (libera). Se pueden implementar con espera activa o con bloqueo:

```
Con espera activa:                 Con bloqueo (cola de espera):
wait(s)   { while (s <= 0); s--; } wait(s)   { s--; if (s < 0) block(); }
signal(s) { s++; }                 signal(s) { s++; if (s <= 0) wakeup(); }
```

En la versión con bloqueo, si el valor es positivo indica cuántas instancias hay libres, y si es negativo, $|s|$ es la cantidad de procesos bloqueados esperando. Ojo: un semáforo **nunca se inicializa en negativo**.

**Espera activa o bloqueo.** El bloqueo no gasta CPU, pero cuesta dos cambios de contexto. La espera activa (spinlock) conviene cuando hay **más de una CPU** y la sección crítica es **muy corta**: se espera menos de lo que costaría bloquearse y despertarse. En un monoprocesador, la espera activa solo gasta el quantum.

**Monitores.** Son una estructura que encapsula los datos compartidos y solo deja usarlos por sus operaciones, que se ejecutan en mutua exclusión. El programador no escribe los wait y signal: la exclusión la garantiza el monitor.

**Inversión de prioridades.** Un proceso de baja prioridad (P1) tiene un recurso; uno de alta prioridad (P3) lo pide y se bloquea; uno de prioridad media (P2) desaloja a P1, y así P3 queda esperando a P2 sin tener nada que ver. La solución es la **herencia de prioridades**: mientras P1 tiene el recurso que espera P3, hereda la prioridad de P3; al liberarlo, la pierde.

**Comunicación entre procesos (IPC).** Además de memoria compartida (que hay que sincronizar), los procesos pueden comunicarse con **paso de mensajes** (send y receive), donde el SO copia los datos y el receive bloqueante ya sincroniza.

**Los tipos de pregunta que toman:**
1. **Verdadero o falso:** condición de carrera y planificador, espera activa, requisitos de una solución, semáforos negativos.
2. **Analizar una solución por software:** qué requisitos cumple (alternancia, interesados, Peterson).
3. **Bernstein:** decidir si dos procesos necesitan sincronizarse.
4. **Conceptos:** inversión y herencia de prioridades, spinlock contra bloqueo, monitores.

### 2. Ejemplo resuelto (final del 20/02/2024, teoría 2 y 3)

> Explícitamente defina como VERDADERA o FALSA cada una de estas afirmaciones, justificando brevemente.
> 2) En un sistema monoprocesador, el algoritmo de planificación de corto plazo podría generar que se produzca una condición de carrera. Esto no es cierto si los procesos están correctamente sincronizados.
> 3) En entornos que no permiten E/S asincrónicas, estas pueden ser simuladas utilizando hilos.

Es del tipo 1. En los verdaderos o falsos de la cátedra cuenta la justificación: se dice V o F y se explica el mecanismo en una o dos oraciones.

```
Paso 1: 2) ¿el planificador puede causar una condición de carrera?
  VERDADERO. Aun con una sola CPU, el planificador decide cuándo interrumpir a un
  proceso: puede sacarlo en medio de una operación que debía ser atómica (x++) y
  darle la CPU a otro que usa el mismo dato. Si los procesos están bien
  sincronizados, el resultado es correcto sin importar el orden que elija.

Paso 2: 3) ¿se puede simular E/S asincrónica con hilos?
  VERDADERO. Se crea un hilo que hace la E/S sincrónica (y se bloquea), mientras
  el resto del proceso sigue ejecutando, como si la E/S fuera asincrónica.
  (Si fueran ULT sin jacketing no serviría: se bloquearía todo el proceso.)

Control: coincide con la resolución de la cátedra (V y V) ✓
```

### 3. Ejercicio guiado (material propio)

> Dos hilos comparten `x = 0` y ejecutan una vez cada uno: el hilo A hace `x = x + 1` y el hilo B hace `x = x * 2`. a) ¿Se cumplen las condiciones de Bernstein? b) ¿Qué valores finales puede tener x? c) Sincronícelos con un semáforo, indicando su tipo y valor inicial.

Es del tipo 3. Armá los conjuntos de lectura y escritura. Después pensá cada línea como tres instrucciones (leer, operar, escribir) y buscá los intercalados posibles.

```
Paso 1: R y W de cada hilo
  → ________

Paso 2: ¿qué intersección no es vacía? ¿Hace falta sincronizar?
  → ________

Paso 3: valores si ejecutan sin intercalarse (A antes que B, y B antes que A)
  → ________

Paso 4: valores si se intercalan (los dos leen x = 0 antes de escribir)
  → ________

Paso 5: la sincronización
  → ________
```

### 4. Práctica

Respondé cada una en dos o tres líneas antes de mirar las respuestas.

1. Verdadero o falso: "La solución de Peterson no tiene espera activa". Justificá.
2. ¿Por qué la alternancia estricta no cumple el requisito de progreso?
3. ¿Por qué deshabilitar interrupciones no sirve en un multiprocesador?
4. Un semáforo con bloqueo vale −3. ¿Qué significa? ¿Y si vale 2?
5. ¿En qué caso conviene un spinlock antes que un mutex con bloqueo?
6. Explicá la inversión de prioridades con un ejemplo de tres procesos y cómo la resuelve la herencia de prioridades.

### 5. Cierre

**Fórmulas**

$$W_A \cap W_B = \varnothing \qquad W_A \cap R_B = \varnothing \qquad R_A \cap W_B = \varnothing \quad \Rightarrow \quad \text{no hay que sincronizar}$$

```
Requisitos: mutua exclusión, progreso, espera limitada, independencia de la velocidad
Alternancia: sin progreso. Interesados: pueden quedar los dos esperando. Peterson: OK, 2 procesos, espera activa
Semáforo con bloqueo: valor > 0 → instancias libres; valor < 0 → |valor| procesos bloqueados
Nunca inicializar un semáforo en negativo
```

**Trampas**
- **Pensar que en monoprocesador no hay condiciones de carrera.** El planificador puede cortar a mitad de un `x++`.
- **Sincronizar lecturas.** Si nadie escribe el dato compartido, no hace falta mutex (Bernstein).
- **Decir que Peterson no tiene espera activa.** Espera en un while.
- **Hacer la sección crítica grande.** Tiene que incluir solo el acceso al recurso, no lo que se puede hacer afuera (E/S, cálculos).
- **Confundir espera activa con bloqueo.** La espera activa consume CPU; el bloqueo, no.

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) Nombrá los cuatro requisitos de una solución a la sección crítica y explicá cuál no cumple la alternancia estricta.
2. (Ejercicio) Verdadero o falso, justificando: "Si dos procesos acceden a la misma variable compartida, siempre hay que sincronizarlos". (material propio)

## 2.2 Sincronizar con semáforos ★★★★★ (estimado)

Temas en Lumen: `u4-semaforos-espera-activa-bloqueo`, `u4-productor-consumidor`

Es el ejercicio de sincronización de los parciales. No se conocen los enunciados completos de los parciales con fecha, pero los cuatro "Ejercicios de parcial" de sincronización de la cátedra, dos de la "Práctica avanzada 1er parcial" y uno del final de 2024 son de este tipo.

### 1. Conceptos

**Tres usos, tres tipos de semáforo.** Casi todo ejercicio se arma combinando estos:

```
USO                            TIPO          VALOR INICIAL   PATRÓN
Mutua exclusión                mutex         1               wait(m); SC; signal(m)
Limitar N instancias           contador      N               wait(c); usar(); signal(c)
Ordenar o esperar un evento    binario/sinc. 0 (o 1 si arranca ese)   A: signal(s)   B: wait(s)
```

**Ordenar la ejecución.** Para que B vaya después de A, B hace `wait(s)` y A hace `signal(s)`, con `s = 0`. Para alternar A, B, A, B..., cada uno tiene su semáforo y le da paso al otro:

```
semA = 1, semB = 0
A: while(1) { wait(semA); print("A"); signal(semB); }
B: while(1) { wait(semB); print("B"); signal(semA); }
```

Un `wait` o `signal` "x2" (dos veces seguidas) sirve para pedir o dar dos pasos: por ejemplo, para imprimir A, B, B, C, A hace `signal(semB)` dos veces y C hace `wait(semC)` dos veces.

**Productor-consumidor.** Un productor deposita en un buffer y un consumidor retira. Hacen falta tres semáforos: un **mutex** para el buffer, un contador de **llenos** (el consumidor espera que haya algo) y, si el buffer tiene límite, un contador de **vacíos** (el productor espera que haya lugar):

```
mutex = 1, llenos = 0, vacios = N
Productor:                          Consumidor:
  item = producir();                  wait(llenos);
  wait(vacios);                       wait(mutex);
  wait(mutex);                        item = retirar(buffer);
  depositar(item, buffer);            signal(mutex);
  signal(mutex);                      signal(vacios);
  signal(llenos);                     consumir(item);
```

Ojo con el orden: primero el contador y **después** el mutex. Si el consumidor hace `wait(mutex)` y después `wait(llenos)` con el buffer vacío, se bloquea con el mutex tomado y el productor nunca puede depositar: deadlock.

**Vectores de semáforos.** Si hay varios recursos del mismo tipo identificados por un número (cajones, estaciones, aviones), se usa un vector: `mutex_cajon[3] = {1, 1, 1}` y `wait(mutex_cajon[id])`.

**Método para sincronizar.**
1. **Recursos compartidos:** ¿qué variable o estructura se modifica desde más de un proceso? Mutex alrededor del acceso, lo más chico posible.
2. **Instancias limitadas:** ¿hay N de algo (impresoras, conexiones, lugares)? Contador en N.
3. **Esperas y orden:** ¿quién tiene que esperar a quién? Semáforo en 0: el que espera hace `wait`, el que habilita hace `signal`. Anotá cada par wait-signal.
4. **Buffers:** productor-consumidor (llenos, vacíos y mutex).
5. **Control:** que cada `wait` tenga su `signal` en algún lado, que no se tome un mutex mientras se espera otra cosa (deadlock), y que se respete el orden pedido. Declará cada semáforo con **tipo y valor inicial**.

**Los tipos de ejercicio que toman:**
1. **Sincronizar un pseudocódigo** dado (enunciado con una historia: robots, aviones, penales), solo con semáforos, sin deadlock ni inanición.
2. **Secuencias:** que se imprima un orden fijo (A, B, C, A...).
3. **Encontrar errores** en una sincronización ya hecha (sin volver a sincronizar).
4. **Productor-consumidor** con buffer limitado o ilimitado.

### 2. Ejemplo resuelto (Ejercicios de parcial de sincronización, Ej 1)

> Dos hermanos, Fred y George, organizan su armario. Fred saca de a una prenda del armario, se la prueba y, si le queda bien, la selecciona para volver a guardarla en un cajón; si no, la separa para donar. Mientras, George toma de a una la ropa que seleccionó su hermano y, según el tipo de prenda, la coloca en un cajón diferente. Hay 3 tipos de prendas y el armario tiene 3 cajones con capacidad de 15 prendas cada uno. Ron, el hermano menor, aprovecha cada vez que Fred separa una prenda para donar y saca otra previamente guardada en algún cajón y la vuelve a poner en el armario, por lo que esto se repite infinitamente. `tipoPrenda()` devuelve un número de 0 a 2 según el tipo de prenda, y `random()` devuelve un número de 0 a 2 al azar. Sincronizar usando únicamente semáforos. Variable compartida: `cajones[3]`.
>
> ```
> Fred (seleccionador)        George (llenador)                      Ron (desordenador)
> while(true) {               while(true) {                          while(true) {
>   agarrarPrenda()             id_prenda = tipoPrenda()               id_prenda = random()
>   if (quedaBien()) {          ponerEnCajon(cajones[id_prenda])       sacarPrendaDelCajonY
>     seleccionar()           }                                          DevolverAlArmario(cajones[id_prenda])
>   } else {                                                         }
>     separar()
>   }
> }
> ```

Es del tipo 1. Se aplica el método: recursos compartidos (los cajones), instancias limitadas (15 lugares por cajón) y esperas (George espera a Fred, Ron espera a Fred y a que haya prendas en el cajón).

```
Paso 1: recursos compartidos
  Cada cajón lo modifican George (pone) y Ron (saca) → un mutex por cajón:
    mutex_cajon[3] = {1, 1, 1}

Paso 2: instancias limitadas
  Cada cajón tiene 15 lugares: George espera lugar en ese cajón
    sem_espacioEnCajon[3] = {15, 15, 15}   (contador)
  Ron solo puede sacar si el cajón tiene algo
    sem_hayPrendaEnCajon[3] = {0, 0, 0}    (contador)

Paso 3: esperas
  George espera que Fred haya seleccionado una prenda
    sem_hayPrendaEnPila = 0   (Fred: signal al seleccionar; George: wait al empezar)
  Ron espera que Fred separe una prenda para donar
    sem_desordenar = 0        (Fred: signal al separar; Ron: wait al empezar)

Paso 4: el código
  Fred:   agarrarPrenda()
          if (quedaBien()) { seleccionar(); signal(sem_hayPrendaEnPila) }
          else             { separar();     signal(sem_desordenar) }

  George: wait(sem_hayPrendaEnPila)
          id_prenda = tipoPrenda()
          wait(sem_espacioEnCajon[id_prenda])
          wait(mutex_cajon[id_prenda])
          ponerEnCajon(cajones[id_prenda])
          signal(mutex_cajon[id_prenda])
          signal(sem_hayPrendaEnCajon[id_prenda])

  Ron:    wait(sem_desordenar)
          id_prenda = random()
          wait(sem_hayPrendaEnCajon[id_prenda])
          wait(mutex_cajon[id_prenda])
          sacarPrendaDelCajonYDevolverAlArmario(cajones[id_prenda])
          signal(mutex_cajon[id_prenda])
          signal(sem_espacioEnCajon[id_prenda])

Control: cada wait tiene su signal (espacio ↔ George y Ron, hayPrenda ↔ Ron y
George); los contadores se piden antes que el mutex; coincide con la resolución
de la cátedra ✓
```

### 3. Ejercicio guiado (Guía de sincronización, Ej 7)

> Un proceso compila un conjunto de programas y envía el resultado de cada compilación por email. N hilos de kernel compilan cada uno un programa distinto y depositan el resultado en una lista compartida; un hilo de kernel retira los resultados y manda un email por cada uno. Asumiendo que la cantidad de programas es infinita, sincronice el código con semáforos: a) si la lista no tiene límite de tamaño; b) si la lista tiene un límite de M resultados.
>
> ```
> KLT compilador (N instancias)               KLT notificador (1 instancia)
> while (TRUE) {                              while (TRUE) {
>   id_programa = obtener_nuevo_programa();     r2 = retirar_resultado(lista);
>   r = compilar_programa(id_programa);         enviar_email(r2);
>   depositar_resultado(r, lista);            }
> }
> ```

Es del tipo 4: los compiladores son productores y el notificador es el consumidor.

```
Paso 1: ¿qué se comparte y quién lo modifica? ¿Qué semáforo va?
  → ________

Paso 2: a) ¿qué tiene que esperar el notificador? Semáforo y valor inicial
  → ________

Paso 3: a) el código de los dos (¿dónde van los wait y los signal?)
  → ________

Paso 4: b) ¿qué cambia si la lista tiene M lugares?
  → ________

Paso 5: control: ¿qué pasa si el notificador hace wait(mutex) antes de esperar resultados?
  → ________
```

### 4. Práctica

#### Ejemplo resuelto 2: encontrar errores (final del 20/02/2024, práctica 1)

> El siguiente pseudocódigo simula la interacción de N usuarios en la red social "Z" y un proceso analizador que toma cada uno de los posts generados para analizarlos. A pesar de estar sincronizado, el sistema se desempeña más lento de lo esperado y frecuentemente deja de funcionar hasta que el administrador reinicia el proceso Analizador. Encuentre al menos 3 errores y/o mejoras en la sincronización planteada (no sincronizar nuevamente, solamente marcar y explicar los errores encontrados).
>
> ```
> Usuario (N instancias)             Analizador (1 instancia)
> while(1) {                         while(1) {
>   wait(mutexPosts)                   wait(mutexPosts);
>   post = generarPost();              wait(hayPosts);
>   postear(post, postsNuevos);        post = obtenerPost(postsNuevos);
>   signal(hayPosts);                  resultado = procesar(post)
>   mostrarEnPantalla(post);           guardarEnDisco(resultado)
>   signal(mutexPosts);                signal(mutexPosts)
> }                                  }
> hayPosts: contador en 0; mutexPosts: mutex
> ```

Es del tipo 3. "Más lento de lo esperado" apunta a secciones críticas demasiado grandes; "deja de funcionar" apunta a un deadlock.

```
Paso 1: el deadlock (Analizador)
  Hace wait(mutexPosts) y después wait(hayPosts). Si no hay posts, se bloquea con
  el mutex tomado y ningún usuario puede postear: nadie hace signal(hayPosts).
  Corrección: invertir el orden (primero wait(hayPosts), después el mutex).

Paso 2: sección crítica grande en el Analizador
  procesar() y guardarEnDisco() no usan la cola: el signal(mutexPosts) tiene que
  ir justo después de obtenerPost(), si no los usuarios esperan una E/S a disco.

Paso 3: sección crítica grande en el Usuario (entrada)
  generarPost() no toca la cola compartida: el wait(mutexPosts) tiene que ir
  después, justo antes de postear().

Paso 4: sección crítica grande en el Usuario (salida)
  mostrarEnPantalla() tampoco usa la cola: el signal(mutexPosts) va justo después
  de postear().

Control: coincide con la resolución de la cátedra (los cuatro errores) ✓
```

#### Ejercicio extra 1: secuencia B, A, C, A (Guía de sincronización, Ej 6)

> Sean los procesos A, B y C, sincronizarlos para que ejecuten de la siguiente manera: B, A, C, A, B, A, C, A...
>
> ```
> Proceso A                 Proceso B                 Proceso C
> while(1) { print("A"); }  while(1) { print("B"); }  while(1) { print("C"); }
> ```

#### Ejercicio extra 2: aeropuerto (Guía de sincronización, Ej 8)

> Un aeropuerto tiene muchos aviones, diez pistas de aterrizaje y despegue y dos controladores aéreos. Cada vez que un avión quiere despegar o aterrizar debe usar una pista: la pide al controlador de entrada y, después de usarla, se lo notifica al controlador de salida para que vuelva a estar disponible. Sincronice sin deadlock ni inanición (cuando el avión ya pidió pista), solo con semáforos, indicando su tipo y valor inicial. `pistasLibres = 10` es una variable compartida y `log()` imprime el valor actual de pistas libres.
>
> ```
> AVIÓN                  CONTROLADOR ENTRADA         CONTROLADOR SALIDA
> while(TRUE) {          while(TRUE) {               while(TRUE) {
>   mantenimiento();       otorgarUnaPista();          liberarUnaPista();
>   despegar();            pistasLibres--;             pistasLibres++;
>   volar();               log(pistasLibres);          log(pistasLibres);
>   aterrizar();         }                           }
> }
> ```

#### Ejercicio extra 3: despacho de productos (Ejercicios de parcial de sincronización, Ej 4)

> Los robots del almacén toman los productos a despachar y los dejan en una caja compartida con los robots de distribución. Cada robot de distribución toma un producto de la caja, se posiciona en una estación de etiquetado disponible y, una vez etiquetado, lo despacha al avión de su destino. Cada avión despega cuando están cargados todos los productos de su destino. Hay 400 productos, exactamente 80 por destino, y cada uno tiene el atributo `destino` con el id del avión. La caja tiene capacidad para 20 productos. Distribución tiene la función `id_etiq()`, que devuelve el id de la estación donde está; Etiquetado y Avión tienen `get_id()`, que devuelve su propio id. Sincronice con semáforos.
>
> ```
> ALMACÉN (N)                  DISTRIBUCIÓN (M)                       ETIQUETADO (4)   AVIÓN (5)
> while(1) {                   while(1) {                             while(1) {       despegar()
>   producto = tomar_producto()  producto = retirar(caja)               etiquetar()
>   depositar(producto, caja)    posicionarse_etiquetado(id_etiq())   }
> }                              despachar(producto, producto.destino)
>                              }
> ```

#### Ejercicio extra 4: reportes (Ejercicios de parcial de sincronización, Ej 2)

> Tres tipos de procesos generan y leen reportes de una base de datos. Los generadores obtienen una de las 10 conexiones disponibles, crean la consulta, la envían al motor de base de datos y, con la información, generan un reporte que escriben en un gran archivo de reportes (la única estructura compartida). Los lectores consumen los reportes sin borrarlos. Las lecturas del archivo pueden llevar horas; las escrituras, pocos segundos. Sincronice con semáforos.
>
> ```
> Lector (10)                  Generador (100)                  Motor de DB (1)
> while (1) {                  while (1) {                      while (1) {
>   nro = rand()                 db = obtenerConexion()           abrirConexion()
>   rep = leer(reportes, nro)    query = generarConsulta()        devolverConsulta()
>   print(rep)                   data = correr(query, db)         cerrarConexion()
> }                              rep = generar(data)            }
>                                escribir(reportes, rep)
>                              }
> ```

### 5. Cierre

**Fórmulas**

```
mutex = 1 (exclusión)   contador = N (instancias)   sincronización = 0 (espera un evento)
Orden A → B:  A hace signal(s), B hace wait(s), s = 0
Productor-consumidor:  mutex = 1, llenos = 0, vacios = N
  Productor: wait(vacios); wait(mutex); depositar; signal(mutex); signal(llenos)
  Consumidor: wait(llenos); wait(mutex); retirar; signal(mutex); signal(vacios)
```

**Trampas**
- **Pedir el mutex antes que el contador.** Si el contador bloquea, queda bloqueado con el mutex tomado: deadlock.
- **Meter en la sección crítica lo que no usa el recurso.** Generar, procesar, mostrar o escribir en disco van afuera.
- **Olvidar el tipo y el valor inicial.** La cátedra los pide para cada semáforo.
- **Un wait sin su signal.** Revisá que cada semáforo tenga quien lo libere; si no, alguien espera para siempre.
- **Proteger variables que solo se leen.** No hace falta (Bernstein).

**Autoevaluación** (sin mirar el bloque; cada ítem vale 1, 0,5 o 0)
1. (Concepto) ¿Para qué se usa un semáforo inicializado en 1, uno en N y uno en 0? Dá un ejemplo de cada uno.
2. (Ejercicio) Sincronizá tres procesos A, B y C para que impriman A, B, B, C, A, B, B, C... Indicá tipo y valor inicial de cada semáforo. (Guía de sincronización, Ej 5')

## Respuestas del capítulo 2

### 2.1 Ejercicio guiado

```
Paso 1: A: R = {x}, W = {x}      B: R = {x}, W = {x}

Paso 2: W_A ∩ W_B = {x} (y también W_A ∩ R_B y R_A ∩ W_B) → hay que sincronizar.

Paso 3: A antes que B: x = (0 + 1) · 2 = 2.   B antes que A: x = 0 · 2 + 1 = 1.

Paso 4: los dos leen 0. Si A escribe último: x = 1. Si B escribe último: x = 0.
  Valores posibles: 0, 1 o 2. El 0 es un resultado imposible sin intercalado:
  se perdió la actualización de A.

Paso 5: mutex m = 1 (tipo mutex)
  A: wait(m); x = x + 1; signal(m)      B: wait(m); x = x * 2; signal(m)
  (Así queda 1 o 2 según quién entre primero; si además hay que fijar el orden,
  hace falta un semáforo de sincronización en 0.)
```

### 2.1 Práctica

```
1. Falso: el proceso que no puede entrar se queda en el while (interesado[j] &&
   turno == j) consumiendo CPU. Es espera activa.
2. Porque obliga a alternar: si el proceso 0 quiere entrar dos veces seguidas y el
   1 no quiere entrar, el 0 espera igual (turno = 1). Decide alguien que no está
   interesado.
3. Porque solo afecta a la CPU donde se ejecuta: los procesos de las otras CPU
   siguen y pueden entrar a la sección crítica. Además, avisar a todas cuesta caro.
4. −3: hay 3 procesos bloqueados en su cola esperando. 2: hay 2 instancias libres
   (dos wait pasarían sin bloquear).
5. Con más de una CPU y una sección crítica muy corta: esperar girando es más
   barato que bloquearse y despertar (dos cambios de contexto).
6. P1 (baja) toma el recurso; P3 (alta) lo pide y se bloquea; P2 (media) desaloja
   a P1 y ejecuta, así P3 espera a P2. Con herencia, P1 toma la prioridad de P3
   mientras tiene el recurso: P2 no lo desaloja, P1 libera rápido y P3 sigue.
```

### 2.1 Autoevaluación

```
1. Mutua exclusión, progreso, espera limitada e independencia de la velocidad.
   La alternancia estricta no cumple progreso: un proceso no puede volver a entrar
   si el otro, que no quiere entrar, no pasó antes por la sección crítica.

2. Falso. Si los dos solo leen la variable (ninguno la escribe), se cumplen las
   condiciones de Bernstein y no hay condición de carrera posible.
```

### 2.2 Ejercicio guiado

```
Paso 1: la lista la modifican los N compiladores (depositan) y el notificador
  (retira) → mutexLista = 1 (mutex).

Paso 2: el notificador no puede retirar si la lista está vacía →
  programasEnLista = 0 (contador): los compiladores hacen signal al depositar y el
  notificador hace wait antes de retirar.

Paso 3: a)
  Compilador:                            Notificador:
    id_programa = obtener_nuevo_programa();  wait(programasEnLista);
    r = compilar_programa(id_programa);      wait(mutexLista);
    wait(mutexLista);                        r2 = retirar_resultado(lista);
    depositar_resultado(r, lista);           signal(mutexLista);
    signal(mutexLista);                      enviar_email(r2);
    signal(programasEnLista);

Paso 4: b) se agrega capacidadEnLista = M (contador): el compilador hace
  wait(capacidadEnLista) antes de wait(mutexLista), y el notificador hace
  signal(capacidadEnLista) después de retirar (antes de enviar el email).

Paso 5: si hace wait(mutexLista) y después wait(programasEnLista) con la lista
  vacía, se bloquea con el mutex tomado: ningún compilador puede depositar →
  deadlock. Siempre el contador primero.
```

### 2.2 Ejercicio extra 1

```
semA = 0, semB = 1, semC = 0 (sincronización), semBoC = 1 (turno de B o C)
A: while(1) { wait(semA); print("A"); signal(semBoC); }
B: while(1) { wait(semB); wait(semBoC); print("B"); signal(semA); signal(semC); }
C: while(1) { wait(semC); wait(semBoC); print("C"); signal(semA); signal(semB); }

Traza: B (habilita A y C); C espera semBoC → A imprime y lo libera → C; C habilita
A y B; B espera semBoC → A → B... = B, A, C, A, B, A, C, A ✓
(La guía da otra solución: semA = 0, semB = 2, semC = 1, con wait x2 en B y en C.)
```

### 2.2 Ejercicio extra 2

```
contadorPistas = 10 (contador), pedidoPista = 0, pistaOtorgada = 0,
liberarPista = 0 (sincronización), mutexPL = 1 (mutex de pistasLibres)

AVIÓN:
  mantenimiento();
  signal(pedidoPista); wait(pistaOtorgada);
  despegar();
  signal(liberarPista);
  volar();
  signal(pedidoPista); wait(pistaOtorgada);
  aterrizar();
  signal(liberarPista);

CONTROLADOR ENTRADA:                    CONTROLADOR SALIDA:
  wait(pedidoPista);                      wait(liberarPista);
  wait(contadorPistas);                   liberarUnaPista();
  otorgarUnaPista();                      signal(contadorPistas);
  signal(pistaOtorgada);                  wait(mutexPL);
  wait(mutexPL);                          pistasLibres++; log(pistasLibres);
  pistasLibres--; log(pistasLibres);      signal(mutexPL);
  signal(mutexPL);

pistasLibres lo modifican los dos controladores → mutexPL. Las pistas son 10 →
contadorPistas. Los semáforos de pedido y otorgamiento hacen que cada avión espere
su pista (atendidos en orden, sin inanición).
```

### 2.2 Ejercicio extra 3

```
mutexCaja = 1 (mutex), prodEnCaja = 0, espacioEnCaja = 20 (contadores),
etiqDisponible = 4 (contador), etiquetar[4] = {0,0,0,0}, etiquetado[4] = {0,0,0,0},
despachado[5] = {0,0,0,0,0} (sincronización), prodADespachar = 400 (contador)

ALMACÉN:                              DISTRIBUCIÓN:
  wait(prodADespachar)                  wait(prodEnCaja)
  producto = tomar_producto()           wait(mutexCaja)
  wait(espacioEnCaja)                   producto = retirar(caja)
  wait(mutexCaja)                       signal(mutexCaja)
  depositar(producto, caja)             signal(espacioEnCaja)
  signal(mutexCaja)                     wait(etiqDisponible)
  signal(prodEnCaja)                    posicionarse_etiquetado(id_etiq())
                                        signal(etiquetar[id_etiq()])
ETIQUETADO:                             wait(etiquetado[id_etiq()])
  wait(etiquetar[get_id()])             despachar(producto, producto.destino)
  etiquetar()                           signal(despachado[producto.destino])
  signal(etiquetado[get_id()])
  signal(etiqDisponible)              AVIÓN:
                                        wait(despachado[get_id()]) x 80
                                        despegar()
```

### 2.2 Ejercicio extra 4

```
mutex = 1 (archivo de reportes), sem_conexiones = 10 (contador),
sem_pedidos_conexion = 0, sem_conexion_lista = 0, sem_query_lista = 0,
sem_reporte_generado = 0 (contador de reportes disponibles)

Lector:                        Generador:                     Motor de DB:
  nro = rand()                   wait(sem_conexiones)           wait(sem_pedidos_conexion)
  wait(sem_reporte_generado)     db = obtenerConexion()         abrirConexion()
  wait(mutex)                    signal(sem_pedidos_conexion)   signal(sem_conexion_lista)
  rep = leer(reportes, nro)      query = generarConsulta()      devolverConsulta()
  signal(mutex)                  wait(sem_conexion_lista)       signal(sem_query_lista)
  print(rep)                     data = correr(query, db)       cerrarConexion()
                                 wait(sem_query_lista)          signal(sem_conexiones)
                                 rep = generar(data)
                                 wait(mutex)
                                 escribir(reportes, rep)
                                 signal(mutex)
                                 signal(sem_reporte_generado)

Así lo resuelve la cátedra. Ojo (comentario propio): como las lecturas duran
horas, con un solo mutex los generadores esperan mucho; el enunciado sugiere que
los lectores podrían leer a la vez (patrón lectores-escritores).
```

### 2.2 Autoevaluación

```
1. En 1: mutex, para la exclusión mutua de una variable compartida. En N: contador,
   para limitar el acceso a N instancias (3 impresoras → 3). En 0: sincronización,
   para que un proceso espere un evento de otro (el consumidor espera un item).

2. semA = 1, semB = 0, semC = 0 (sincronización)
   A: while(1) { wait(semA); print("A"); signal(semB); signal(semB); }
   B: while(1) { wait(semB); print("B"); signal(semC); }
   C: while(1) { wait(semC); wait(semC); print("C"); signal(semA); }
```
