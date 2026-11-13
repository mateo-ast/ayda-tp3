# Análisis de grandes volúmenes de datos

Programa de consola en Python puro con menú interactivo para generar, analizar
y ordenar un archivo de números, además de construir un árbol AVL y un heap
binario.

## Requisitos

- Python 3.11 o superior (64 bits recomendado).
- [uv](https://docs.astral.sh/uv/) para gestionar el entorno.
- No usa dependencias externas en tiempo de ejecución.

## Ejecución

```bash
uv sync
uv run python run.py
```

También se puede ejecutar directamente:

```bash
python run.py
```

Los archivos de datos se crean en la carpeta actual durante el desarrollo y
junto al `.exe` cuando el programa está empaquetado.

## Menú

```text
a) Generar Datos.txt
b) Máximo y mínimo
c) Top 10 números más frecuentes
d) Counting Sort
e) Selection Sort
f) Verificar archivos ordenados
g) Registro y comparativa de tiempos
i) Árbol AVL
j) Heap binario (Max/Min)
k) Heap Sort
0) Salir
```

La opción **a)** pide por teclado:

- **N**: cantidad de números a generar.
- **M**: valor máximo del rango (por defecto `100.000.000`, por lo que los
  valores quedan entre `0` y `100.000.000`).

Esto permite usar N pequeños para probar los algoritmos y N grandes para
analizar el volumen real.

## Archivos generados

| Archivo | Contenido |
|---|---|
| `Datos.txt` | Datos originales, un número por línea |
| `Datos_CountingSort.txt` | Resultado de Counting Sort |
| `Datos_SelectionSort.txt` | Resultado de Selection Sort |
| `Datos_HeapSort.txt` | Resultado de Heap Sort |
| `tiempos.log` | Registro de tiempos de ejecución |

## Algoritmos

### Counting Sort

Cuenta cuántas veces aparece cada valor en un arreglo de tamaño `M + 1`.
Luego calcula las posiciones acumuladas y coloca cada elemento en su lugar.
Es estable y su complejidad es **O(n + M)**. Necesita un arreglo auxiliar de
`M + 1` enteros.

### Selection Sort

Busca el menor elemento del resto del arreglo y lo intercambia con la posición
actual. Su complejidad es **O(n²)**, por lo que deja de ser práctico cuando N
crece. El programa avisa y pide confirmación antes de ejecutarlo con N grande.

### Heap Sort

Construye un Max-Heap en **O(n)** y luego extrae el máximo repetidamente,
dejándolo al final del arreglo. Su complejidad total es **O(n log n)**.

### Árbol AVL

Cada valor único es un nodo y un contador guarda cuántas veces se repite.
Las inserciones, búsquedas y eliminaciones son **O(log n)**. El árbol se
mantiene balanceado mediante rotaciones simples y dobles.

Los nodos se almacenan en arreglos paralelos (`keys`, `counts`, `left`,
`right`, `heights`) en lugar de objetos individuales, para reducir el uso de
memoria.

Se muestran:

- Altura del árbol.
- Cantidad de nodos únicos.
- Cantidad total de valores almacenados.
- Recorrido InOrden con los primeros 50 elementos.

### Heap binario

Se implementan Max-Heap y Min-Heap sobre un arreglo:

- Construcción por heapify: **O(n)**.
- Inserción: **O(log n)**.
- Eliminación de la raíz: **O(log n)**.
- Búsqueda: **O(n)**, porque el heap no está pensado para búsquedas.

Se muestra la cantidad de elementos, la raíz y la altura aproximada
(`⌊log₂ n⌋ + 1`).

## Verificación

La opción **f)** revisa cada archivo ordenado y comprueba:

1. Que exista.
2. Que la cantidad de números coincida con `Datos.txt`.
3. Que esté ordenado de forma ascendente.
4. Que la suma y el XOR de los valores coincidan con el original.

El checksum detecta pérdidas, duplicaciones o modificaciones de datos.

## Tiempos

Cada operación muestra su tiempo con `time.perf_counter()` y lo agrega a
`tiempos.log`. La opción **g)** muestra las últimas mediciones y el último
tiempo registrado por operación.

## Complejidades

| Operación | Complejidad | Memoria auxiliar |
|---|---|---|
| Máximo y mínimo | O(n) | O(1) |
| Frecuencia | O(n + M) | O(M) |
| Counting Sort | O(n + M) | O(n + M) |
| Selection Sort | O(n²) | O(n) |
| Heap Sort | O(n log n) | O(n) |
| Construir AVL | O(n log n) | O(n) |
| Buscar/insertar/eliminar en AVL | O(log n) | O(1) |
| Construir heap | O(n) | O(n) |
| Insertar/eliminar raíz en heap | O(log n) | O(1) |
| Buscar en heap | O(n) | O(1) |

## Rendimiento y limitaciones

Python puro es cómodo y didáctico, pero no es la mejor herramienta para
100.000.000 de elementos:

- `Datos.txt` con 100 millones de números ocupa aproximadamente 0,9 GB.
- Cargar el archivo y construir arreglos grandes puede tardar minutos.
- Selection Sort con 100 millones es inviable (semanas o meses).
- Construir el AVL o aplicar Heap Sort con 100 millones también puede tardar
  horas o días.

Por eso el programa permite elegir N y M. Para las demostraciones se
recomienda:

| Demostración | N sugerido |
|---|---|
| Selection Sort | 10.000 a 100.000 |
| AVL / Heap / Heap Sort | 100.000 a 1.000.000 |
| Counting Sort / frecuencia | 1.000.000 o más |

Las operaciones costosas muestran una estimación y piden confirmación.

### Resultados de referencia

Mediciones obtenidas en Linux con Python 3.14 y un disco NVMe. Los tiempos
varían según el equipo.

| N | Rango | Carga | Máx/mín | Frecuencia | Counting Sort | Heap Sort | AVL (construir) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100.000 | 0..99.999 | 17 ms | 5 ms | 59 ms | 38 ms | 507 ms | 1,18 s |
| 1.200.000 | 0..1.199.999 | 222 ms | — | 233 ms | 559 ms | 7,74 s | — |
| 10.000.000 | 0..100.000.000 | 1,84 s | 449 ms | 5,97 s | 8,98 s | — | — |

La frecuencia con 10 millones y rango 100 millones usa el arreglo de conteos
de 400 MB y tarda unos 6 segundos. Counting Sort con ese mismo volumen tarda
unos 9 segundos y usa cerca de 850 MB de memoria.

Con 100 millones de valores, Counting Sort necesita aproximadamente 1,5 GB de
RAM (datos + conteos + prefijos + resultado). Conviene usar una PC de 64 bits
con al menos 4 GB de memoria libre.

## Compilar el `.exe` en Windows

El ejecutable debe compilarse en un PC Windows con Python de 64 bits. No se
puede generar desde Linux porque PyInstaller no hace compilación cruzada.

```powershell
powershell -ExecutionPolicy Bypass -File .\build_windows.ps1
```

El script ejecuta:

```powershell
uv sync
uv run --with pyinstaller pyinstaller --onefile --console --clean `
    --name AnalisisDatos --paths src run.py
```

Resultado: `dist\AnalisisDatos.exe`.

Recomendaciones:

- Copiar el `.exe` a una carpeta con permisos de escritura, por ejemplo
  `C:\Ayda\`.
- No ejecutarlo desde `Program Files`, porque necesita crear archivos.
- Si Windows Defender marca el ejecutable de un solo archivo, compilar con
  `--onedir` en lugar de `--onefile`.
- Usar Python de 64 bits: uno de 32 bits no puede manejar los arreglos grandes.

## Estructura del código

```text
run.py                    Entrada para desarrollo y PyInstaller
src/ayda/config.py        Rutas y constantes
src/ayda/file_io.py       Generación, lectura, escritura y verificación
src/ayda/analysis.py      Máximo, mínimo y frecuencias
src/ayda/sorting.py       Counting Sort, Selection Sort y Heap Sort
src/ayda/avl.py           Árbol AVL
src/ayda/heap.py          Max-Heap y Min-Heap
src/ayda/timing.py        Medición y registro de tiempos
src/ayda/main.py          Menú y flujo del programa
```

Los nombres de archivos, clases, funciones y variables están en inglés. El
menú, los mensajes y los comentarios están en español.
