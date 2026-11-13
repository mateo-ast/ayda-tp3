# Comparación de estructuras y algoritmos

## Objetivo

Comparar **Heap Sort** con **Counting Sort** y **Selection Sort** considerando:

- Tiempo de ejecución.
- Uso de memoria.
- Complejidad algorítmica.

Además, comparar las estructuras **Árbol AVL** y **Heap** en las operaciones de
inserción, búsqueda y eliminación, para concluir cuál conviene usar con grandes
volúmenes de datos.

## Resumen ejecutivo

- **Counting Sort** es el más rápido cuando el rango de valores `M` es parecido
  a la cantidad de datos `N`, pero necesita memoria proporcional a `N + M`.
- **Heap Sort** es la opción más robusta para grandes volúmenes y rangos
  amplios: `O(N log N)`, sin depender del rango y con memoria lineal.
- **Selection Sort** solo sirve para datos pequeños o con fines didácticos:
  `O(N²)` lo vuelve inviable para 100 millones de elementos.
- **AVL** conviene cuando se necesita búsqueda ordenada, búsqueda por valor o
  eliminación arbitraria en `O(log N)`.
- **Heap** conviene para colas de prioridad, obtener el máximo/mínimo y
  construir en `O(N)`; su búsqueda es lineal y solo elimina la raíz.

## Entorno y metodología

Las mediciones se realizaron con la implementación de este repositorio:

| Elemento      | Detalle                                             |
| ------------- | --------------------------------------------------- |
| Lenguaje      | Python 3.14, biblioteca estándar                    |
| Datos         | `array('I')` de enteros de 32 bits                  |
| Procesamiento | Un solo hilo                                        |
| Sistema       | Linux, 15 GB de RAM, disco NVMe                     |
| Tiempo        | `time.perf_counter()`                               |
| Memoria       | Máximo residente del proceso con `/usr/bin/time -v` |

Los valores marcados como **medidos** se ejecutaron realmente. Los marcados
como **estimados** se obtuvieron por extrapolación de las mediciones y de la
complejidad del algoritmo.

---

# l) Comparación de estructuras y algoritmos

## 1. Algoritmos de ordenamiento

### 1.1 Complejidad algorítmica

| Algoritmo      | Complejidad mejor caso | Complejidad peor caso | Complejidad promedio | Memoria auxiliar |
| -------------- | ---------------------- | --------------------- | -------------------- | ---------------- |
| Counting Sort  | `O(n + k)`             | `O(n + k)`            | `O(n + k)`           | `O(n + k)`       |
| Selection Sort | `O(n²)`                | `O(n²)`               | `O(n²)`              | `O(1)`           |
| Heap Sort      | `O(n log n)`           | `O(n log n)`          | `O(n log n)`         | `O(1)`           |

Para Counting Sort, `k` es el tamaño del rango de claves. En este programa se
usa `k = M + 1`, donde `M` es el valor máximo observado en los datos. Por eso
su costo depende de `M` y no solo de `N`.

Selection Sort y Heap Sort son algoritmos de comparación. Counting Sort no
compara elementos: cuenta apariciones y calcula posiciones.

> Nota de implementación: los tres algoritmos reciben el arreglo original y
> trabajan sobre una copia para no modificarlo. Por eso el programa usa
> `O(N)` de memoria adicional aunque el algoritmo, a nivel teórico, sea
> in-place.

### 1.2 Tiempo de ejecución

|           N |     Rango M |       Counting Sort |       Selection Sort |             Heap Sort |
| ----------: | ----------: | ------------------: | -------------------: | --------------------: |
|      10.000 |      10.000 |                   — |  **2,68 s** (medido) |                     — |
|      20.000 |      20.000 |                   — | **10,77 s** (medido) |                     — |
|     100.000 |     100.000 |  **38 ms** (medido) |  ~4,5 min (estimado) |   **507 ms** (medido) |
|   1.200.000 |   1.200.000 | **559 ms** (medido) |   ~10,8 h (estimado) |   **7,74 s** (medido) |
|  10.000.000 | 100.000.000 | **8,98 s** (medido) |  ~31 días (estimado) |      ~74 s (estimado) |
| 100.000.000 | 100.000.000 | ~1–2 min (estimado) | ~8,5 años (estimado) | ~15–25 min (estimado) |

Observaciones:

- Selection Sort crece con `N²`: duplicar `N` cuadruplica el tiempo. Pasó de
  2,68 s con 10.000 elementos a 10,77 s con 20.000.
- Heap Sort creció de 507 ms a 7,74 s al pasar de 100.000 a 1.200.000
  elementos, un aumento coherente con `N log N`.
- Counting Sort fue el más rápido cuando el rango acompañó el tamaño de los
  datos. Con 1.200.000 valores en un rango de 1.200.000 tardó 559 ms, mientras
  Heap Sort tardó 7,74 s.
- Con 10.000.000 de valores en un rango de 100.000.000, Counting Sort tardó
  8,98 s. El rango grande empieza a pesar, aunque sigue siendo competitivo.

### 1.3 Uso de memoria

#### Memoria teórica

| Algoritmo      | Memoria auxiliar    | Total aproximado con N = 100.000.000                    |
| -------------- | ------------------- | ------------------------------------------------------- |
| Counting Sort  | `O(N + M)`          | ~1,2 GB (hasta ~1,6 GB transitorio) con M = 100.000.000 |
| Selection Sort | `O(N)` por la copia | ~400 MB de copia + 400 MB de datos                      |
| Heap Sort      | `O(N)` por la copia | ~400 MB de copia + 400 MB de datos                      |
| Árbol AVL      | `O(u)`              | ~1,26 GB con ~63,2 M de claves únicas + 400 MB de datos |
| Heap binario   | `O(N)`              | ~400 MB + 400 MB de datos                               |

En Counting Sort se distinguen dos picos:

1. Durante la suma prefija coexisten el arreglo de conteos original y el nuevo:
   `4N + 8(M + 1)` bytes.
2. Durante la colocación coexisten datos, conteos y resultado:
   `8N + 4(M + 1)` bytes.

El máximo es aproximadamente `máx(4N + 8M, 8N + 4M)` bytes, más el overhead del
intérprete. Por eso, con `N = 10.000.000` y `M = 100.000.000`, el pico teórico
es de unos 840 MB; la medición real del proceso fue de **852,7 MB**.

En el AVL, `u` es la cantidad de claves únicas. Cada nodo usa cinco arreglos de
4 bytes: clave, contador, izquierdo, derecho y altura. Son **20 bytes por
nodo**. Para valores aleatorios con `N = M = 100.000.000`, se esperan unas
63,2 millones de claves únicas: unos 1,26 GB solo para el árbol.

#### Memoria medida

|          N |     Rango M | Memoria máxima del proceso |
| ---------: | ----------: | -------------------------: |
|    100.000 |     100.000 |                    37,5 MB |
|  1.200.000 |   1.200.000 |                    93,8 MB |
| 10.000.000 | 100.000.000 |                   852,7 MB |

Estos valores incluyen el intérprete de Python, el arreglo de datos y las
estructuras auxiliares del algoritmo ejecutado.

### 1.4 Análisis de cada algoritmo

#### Counting Sort

**Ventajas:**

- Tiempo lineal `O(N + M)`; no realiza comparaciones.
- Es estable, por lo que conserva el orden relativo de elementos iguales.
- Excelente cuando `M` es del mismo orden que `N`.
- En la práctica fue el más rápido de los tres en los casos medidos.

**Desventajas:**

- Necesita un arreglo de conteos de tamaño `M + 1`.
- Si `M` es mucho mayor que `N`, desperdicia tiempo y memoria. Por ejemplo,
  ordenar 10.000 valores en el rango 0..100.000.000 tarda segundos y usa
  cientos de MB, cuando Heap Sort tardaría milisegundos.
- Solo sirve para claves enteras no negativas y de rango acotado.

**Cuándo usarlo:** cuando los datos son enteros, el rango es conocido y
`M` no es mucho mayor que `N`, y hay memoria suficiente.

#### Selection Sort

**Ventajas:**

- Muy simple de implementar y explicar.
- Realiza como máximo `N - 1` intercambios.
- No necesita estructuras auxiliares más allá de la copia del arreglo.

**Desventajas:**

- `O(N²)` comparaciones siempre, incluso si los datos ya están ordenados.
- Con 100.000 elementos tarda minutos; con 1.000.000, horas; con 100.000.000,
  años.
- No es competitivo para grandes volúmenes.

**Cuándo usarlo:** únicamente con `N` pequeño o como ejemplo didáctico.

#### Heap Sort

**Ventajas:**

- `O(N log N)` en todos los casos.
- No depende del rango de valores.
- Funciona bien con grandes volúmenes y rangos amplios.
- Usa memoria lineal y ordena sobre una copia del arreglo.
- Tiene un comportamiento predecible.

**Desventajas:**

- Es más lento que Counting Sort cuando `M ≈ N`.
- No es estable.
- En Python puro, cada comparación e intercambio tiene costo considerable.

**Cuándo usarlo:** cuando `N` es grande, el rango es amplio o desconocido, o no
hay memoria para Counting Sort.

### 1.5 Comparación directa para grandes volúmenes

| Situación                            | Mejor opción                               | Motivo                                            |
| ------------------------------------ | ------------------------------------------ | ------------------------------------------------- |
| Enteros, `M ≈ N`, memoria disponible | Counting Sort                              | `O(N + M)` y muy rápido en la práctica            |
| Rango `M` mucho mayor que `N`        | Heap Sort                                  | Counting desperdicia memoria y tiempo en el rango |
| Memoria muy limitada                 | Heap Sort                                  | Evita el arreglo de conteos de tamaño `M`         |
| Se necesita estabilidad              | Counting Sort                              | Selection y Heap Sort no son estables             |
| `N` pequeño (miles)                  | Cualquiera; Selection es aceptable         | La diferencia es despreciable                     |
| `N = 100.000.000`                    | Counting Sort si `M ≈ N`; si no, Heap Sort | Selection es inviable en todos los casos          |

---

## 2. Comparación AVL vs Heap

### 2.1 Complejidad de las operaciones

| Operación                  | Árbol AVL                           | Heap binario                     |
| -------------------------- | ----------------------------------- | -------------------------------- |
| Construcción desde N datos | `O(N log u)` insertando uno por uno | `O(N)` con heapify               |
| Inserción                  | `O(log u)`                          | `O(log N)`                       |
| Búsqueda de un valor       | `O(log u)`                          | `O(N)`                           |
| Eliminación                | `O(log u)` de una clave arbitraria  | `O(log N)`, pero solo de la raíz |
| Obtener mínimo/máximo      | `O(log u)`                          | `O(1)`                           |
| Recorrido ordenado         | `O(u)` con InOrden                  | No directo; requiere ordenar     |
| Memoria                    | ~20 bytes por clave única           | 4 bytes por elemento             |

`u` es la cantidad de claves únicas del AVL; `N` es la cantidad de elementos
del heap. El AVL maneja duplicados con un contador, por lo que `u ≤ N`.

### 2.2 Tiempos medidos con 100.000 elementos

| Operación    |                         AVL |              Heap Max |
| ------------ | --------------------------: | --------------------: |
| Construcción |                     1,172 s |               0,035 s |
| Búsqueda     |                     1,81 µs | 3.704,90 µs (3,70 ms) |
| Inserción    |                    15,14 µs |               3,99 µs |
| Eliminación  | 13,66 µs (clave arbitraria) |   5,15 µs (solo raíz) |

Datos: 100.000 valores aleatorios en el rango 0..99.999. El AVL quedó con
63.138 nodos únicos. La búsqueda del heap es lineal: se midió el promedio de
1.000 búsquedas y cada una recorrió parte del arreglo. En el AVL se midió el
promedio de 1.000 búsquedas, inserciones y eliminaciones.

Conclusiones de las mediciones:

- **Construcción:** el heap es mucho más rápido porque usa heapify `O(N)`.
  El AVL debe insertar y rebalancear uno por uno: `O(N log u)`.
- **Búsqueda:** el AVL es órdenes de magnitud más rápido. El heap no está
  diseñado para buscar valores arbitrarios.
- **Inserción:** ambos son `O(log N)`, pero el heap tiene menor constante.
- **Eliminación:** el heap solo elimina la raíz. Si se quisiera eliminar un
  valor arbitrario, primero habría que buscarlo en `O(N)` y luego reajustar.
- **Orden:** el AVL permite recorrer los datos ordenados; el heap solo garantiza
  que la raíz es el máximo o el mínimo.

### 2.3 Uso de memoria

| Estructura |     Memoria por elemento |             N = 100.000 |                          N = 100.000.000 |
| ---------- | -----------------------: | ----------------------: | ---------------------------------------: |
| AVL        | 20 bytes por clave única | ~1,26 MB (63.138 nodos) | ~1,26 GB si hay ~63,2 M de claves únicas |
| Heap       |                  4 bytes |                 ~400 KB |                                  ~400 MB |

El AVL usa más memoria porque necesita claves, contadores, dos punteros y la
altura de cada nodo. El heap solo necesita el arreglo de valores. Aun así, el
AVL sigue siendo eficiente en memoria comparado con una implementación basada
en objetos de Python; por eso el programa usa arreglos paralelos.

### 2.4 Comparación funcional

**Árbol AVL:**

- Mantiene los datos ordenados.
- Permite buscar cualquier valor en `O(log N)`.
- Permite insertar y eliminar claves arbitrarias.
- Permite recorrido InOrden.
- Es útil para diccionarios ordenados, rangos y búsquedas frecuentes.
- Es más complejo de implementar y consume más memoria.

**Heap:**

- Mantiene una prioridad: la raíz es el máximo o el mínimo.
- Construcción muy rápida en `O(N)`.
- Inserción y eliminación de la raíz en `O(log N)`.
- La búsqueda de un valor arbitrario es `O(N)`.
- Es ideal para colas de prioridad, planificación, top-k y algoritmos como
  Heap Sort.
- Es más simple y usa menos memoria.

### 2.5 Cuándo usar cada estructura

| Necesidad                              | Estructura recomendada      |
| -------------------------------------- | --------------------------- |
| Buscar valores frecuentemente          | AVL                         |
| Insertar y eliminar claves arbitrarias | AVL                         |
| Recorrer datos ordenados               | AVL                         |
| Obtener siempre el máximo o el mínimo  | Heap                        |
| Construir una cola de prioridad rápido | Heap                        |
| Ordenar con Heap Sort                  | Heap                        |
| Ahorrar memoria                        | Heap                        |
| Grandes volúmenes con búsquedas        | AVL (si la memoria alcanza) |

---

## 3. Conclusiones para grandes volúmenes de datos

1. **Selection Sort no es una opción para grandes volúmenes.** Su `O(N²)` hace
   que 100.000 elementos tarden minutos y 100.000.000 tarden años. Solo tiene
   valor didáctico o para arreglos muy pequeños.

2. **Counting Sort es el más rápido cuando el rango es manejable.** Con
   `M ≈ N`, su `O(N + M)` supera claramente a Heap Sort: por ejemplo, 559 ms
   frente a 7,74 s con 1.200.000 elementos. Sin embargo, su memoria crece con
   `M`: con 100.000.000 de valores puede necesitar más de 1 GB.

3. **Heap Sort es la mejor opción general.** Su `O(N log N)` no depende del
   rango, usa memoria lineal y funciona con cualquier conjunto de enteros. Es
   más lento que Counting Sort cuando `M ≈ N`, pero mucho más seguro cuando el
   rango es amplio o la memoria es limitada.

4. **Para el caso de la consigna** —100.000.000 de valores en el rango
   0..100.000.000— Counting Sort sería el más rápido si se dispone de
   aproximadamente 1,2–1,6 GB de RAM. Si no se dispone de esa memoria, Heap Sort
   es la alternativa práctica. Selection Sort queda descartado.

5. **AVL vs Heap depende de la operación.** El AVL gana en búsqueda y en
   operaciones ordenadas; el heap gana en construcción, memoria y obtención del
   máximo/mínimo. Para una cola de prioridad o para Heap Sort, el heap es
   claramente mejor. Para un diccionario ordenado con búsquedas frecuentes, el
   AVL es mejor.

6. **No hay un ganador absoluto.** La elección depende de la relación entre
   `N` y `M`, de la memoria disponible, de si se necesita estabilidad y del tipo
   de operaciones que se realizarán.

## 4. Limitaciones del análisis

- Las mediciones corresponden a Python puro y a un equipo concreto; los tiempos
  pueden variar en otro hardware o en el `.exe` de Windows.
- Los valores marcados como estimados no se ejecutaron por su costo; se
  obtuvieron por extrapolación de las mediciones y de la complejidad.
- La memoria medida es el máximo residente del proceso e incluye el intérprete
  de Python y los datos de entrada.
- En una implementación en C, los factores constantes serían menores, pero las
  conclusiones asintóticas se mantienen.
- El código y las instrucciones de ejecución están en el [README](README.md).
