"""Menú principal del programa."""

from __future__ import annotations

import sys
import time

from .analysis import find_extremes, is_sorted, top_frequent, values_checksum
from .avl import AVLTree
from .config import (
    COUNTING_FILE,
    DATA_FILE,
    DEFAULT_MAX_VALUE,
    HEAP_FILE,
    SELECTION_FILE,
)
from .file_io import (
    DataError,
    Dataset,
    data_path,
    generate_data,
    human_size,
    load_data,
    verify_file,
    write_values,
)
from .heap import BinaryHeap
from .sorting import counting_sort, heap_sort, selection_sort
from .timing import (
    TimeRecord,
    format_seconds,
    log_time,
    read_records,
    timing_path,
)

UINT32_MAX = 4_294_967_295
AVL_BUILD_WARNING = 200_000
HEAP_BUILD_WARNING = 2_000_000
SELECTION_WARNING = 20_000
SELECTION_COMPARISONS_PER_SECOND = 8_000_000

_dataset: Dataset | None = None
_avl: AVLTree | None = None
_heap: BinaryHeap | None = None


# ---------------------------------------------------------------------------
# Utilidades de pantalla
# ---------------------------------------------------------------------------


def fmt_int(value: int) -> str:
    """Formatea un entero con puntos de miles."""
    return f"{value:,}".replace(",", ".")


def progress_printer(label: str):
    """Crea una función que muestra el avance cada 5 %."""
    state = {"last": -1}

    def update(done: int, total: int) -> None:
        if total <= 0:
            return
        percent = int(done * 100 / total)
        if percent == state["last"]:
            return
        if percent >= state["last"] + 5 or percent >= 100:
            state["last"] = percent
            print(f"\r{label}: {percent}%", end="", flush=True)
            if percent >= 100:
                print()

    return update


def ask_int(
    prompt: str,
    minimum: int | None = None,
    maximum: int | None = None,
    default: int | None = None,
) -> int:
    """Pide un entero, validando el rango."""
    while True:
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            value = int(raw)
        except ValueError:
            print("Ingrese un número entero válido.")
            continue
        if minimum is not None and value < minimum:
            print(f"El valor debe ser mayor o igual que {fmt_int(minimum)}.")
            continue
        if maximum is not None and value > maximum:
            print(f"El valor debe ser menor o igual que {fmt_int(maximum)}.")
            continue
        return value


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    """Pide confirmación s/n."""
    suffix = "[S/n]" if default else "[s/N]"
    while True:
        raw = input(f"{prompt} {suffix}: ").strip().lower()
        if raw == "":
            return default
        if raw in ("s", "si", "sí"):
            return True
        if raw in ("n", "no"):
            return False


def record_time(operation: str, count: int, max_value: int, seconds: float) -> None:
    """Muestra y guarda una medición."""
    print(f"Tiempo de {operation}: {format_seconds(seconds)}")
    try:
        log_time(operation, count, max_value, seconds)
    except OSError as exc:
        print(f"No se pudo escribir en tiempos.log: {exc}")


# ---------------------------------------------------------------------------
# Carga de datos
# ---------------------------------------------------------------------------


def invalidate_caches() -> None:
    global _dataset, _avl, _heap
    _dataset = None
    _avl = None
    _heap = None


def load_dataset() -> Dataset | None:
    """Carga Datos.txt una sola vez por sesión y reutiliza la copia."""
    global _dataset

    path = data_path(DATA_FILE)
    if not path.exists():
        print(f"No existe {path.name}. Use la opción a) para generarlo.")
        return None

    stat = path.stat()
    if (
        _dataset is not None
        and _dataset.path == path
        and _dataset.mtime == stat.st_mtime
        and _dataset.size == stat.st_size
    ):
        return _dataset

    print(f"Cargando {path.name} ({human_size(stat.st_size)})...")
    start = time.perf_counter()
    try:
        _dataset = load_data(path)
    except DataError as exc:
        print(f"Error: {exc}")
        return None
    elapsed = time.perf_counter() - start
    dataset = _dataset
    print(
        f"Cargados {fmt_int(dataset.count)} números en "
        f"{format_seconds(elapsed)}. Rango observado: 0..{fmt_int(dataset.max_value)}."
    )
    return dataset


def show_status() -> None:
    """Muestra el estado de los datos en el menú."""
    if _dataset is not None:
        print(
            f"Datos en memoria: {fmt_int(_dataset.count)} números | "
            f"máximo observado: {fmt_int(_dataset.max_value)}"
        )
        return

    path = data_path(DATA_FILE)
    if path.exists():
        print(f"{path.name}: {human_size(path.stat().st_size)} (se carga al usarlo)")
    else:
        print("Sin datos: use la opción a) para generar Datos.txt")


# ---------------------------------------------------------------------------
# Opciones generales
# ---------------------------------------------------------------------------


def option_generate() -> None:
    count = ask_int("Cantidad de números a generar: ", minimum=1)
    max_value = ask_int(
        f"Valor máximo del rango [Enter = {fmt_int(DEFAULT_MAX_VALUE)}]: ",
        minimum=0,
        maximum=UINT32_MAX,
        default=DEFAULT_MAX_VALUE,
    )

    estimated_bytes = count * (len(str(max_value)) + 1)
    print(
        f"Se generarán {fmt_int(count)} números entre 0 y {fmt_int(max_value)} "
        f"(aproximadamente {human_size(estimated_bytes)})."
    )

    if count > 1_000_000:
        print(
            "Aviso: con muchos datos, las opciones de AVL, Heap y Selection Sort "
            "pueden tardar mucho en Python."
        )

    if count > 5_000_000 and not ask_yes_no(
        "La generación puede tardar varios minutos. ¿Continuar?"
    ):
        return

    print("Generando archivo...")
    start = time.perf_counter()
    try:
        seed = generate_data(count, max_value, progress=progress_printer("Generando"))
    except DataError as exc:
        print(f"Error: {exc}")
        return
    elapsed = time.perf_counter() - start
    invalidate_caches()

    path = data_path(DATA_FILE)
    print(f"Archivo generado: {path}")
    print(f"Semilla aleatoria: {seed}")
    print(f"Tamaño: {human_size(path.stat().st_size)}")
    print(f"Tiempo de generación: {format_seconds(elapsed)}")


def option_extremes() -> None:
    dataset = load_dataset()
    if dataset is None:
        return

    start = time.perf_counter()
    minimum, maximum = find_extremes(dataset.values)
    elapsed = time.perf_counter() - start

    print(f"Mínimo: {fmt_int(minimum)}")
    print(f"Máximo: {fmt_int(maximum)}")
    record_time("Máximo y mínimo", dataset.count, dataset.max_value, elapsed)


def option_frequency() -> None:
    dataset = load_dataset()
    if dataset is None:
        return

    print("Calculando frecuencias...")
    start = time.perf_counter()
    top = top_frequent(dataset.values, dataset.max_value, 10)
    elapsed = time.perf_counter() - start

    print("\nTop 10 números más repetidos:")
    print("  #   Número        Repeticiones")
    for index, (value, count) in enumerate(top, start=1):
        print(f"{index:>4}   {fmt_int(value):<14} {fmt_int(count):>10}")

    record_time("Top 10 frecuentes", dataset.count, dataset.max_value, elapsed)


def option_counting_sort() -> None:
    dataset = load_dataset()
    if dataset is None:
        return

    if dataset.max_value > 300_000_000:
        print("El rango es demasiado grande para el arreglo de conteos.")
        return

    print(
        f"Counting Sort: {fmt_int(dataset.count)} valores, "
        f"rango 0..{fmt_int(dataset.max_value)}."
    )
    print("Contando valores y calculando posiciones...")
    start = time.perf_counter()
    sorted_values = counting_sort(
        dataset.values,
        dataset.max_value,
        progress=progress_printer("Counting Sort"),
    )
    sort_elapsed = time.perf_counter() - start

    path = data_path(COUNTING_FILE)
    print(f"Guardando {path.name}...")
    start = time.perf_counter()
    write_values(sorted_values, path, progress=progress_printer("Guardando"))
    write_elapsed = time.perf_counter() - start

    print(f"Archivo: {path}")
    print(f"Tiempo de ordenamiento: {format_seconds(sort_elapsed)}")
    print(f"Tiempo de escritura: {format_seconds(write_elapsed)}")
    record_time("Counting Sort", dataset.count, dataset.max_value, sort_elapsed)
    del sorted_values


def option_selection_sort() -> None:
    dataset = load_dataset()
    if dataset is None:
        return

    count = dataset.count
    comparisons = count * (count - 1) // 2
    print(
        f"Selection Sort: {fmt_int(count)} valores, "
        f"aproximadamente {fmt_int(comparisons)} comparaciones."
    )

    if count > SELECTION_WARNING:
        estimated = comparisons / SELECTION_COMPARISONS_PER_SECOND
        print(f"Estimación muy aproximada: {format_seconds(estimated)}.")
        if not ask_yes_no("Selection Sort puede tardar mucho. ¿Continuar?"):
            return

    print("Ordenando...")
    start = time.perf_counter()
    sorted_values = selection_sort(
        dataset.values, progress=progress_printer("Selection Sort")
    )
    sort_elapsed = time.perf_counter() - start

    path = data_path(SELECTION_FILE)
    print(f"Guardando {path.name}...")
    start = time.perf_counter()
    write_values(sorted_values, path, progress=progress_printer("Guardando"))
    write_elapsed = time.perf_counter() - start

    print(f"Archivo: {path}")
    print(f"Tiempo de ordenamiento: {format_seconds(sort_elapsed)}")
    print(f"Tiempo de escritura: {format_seconds(write_elapsed)}")
    record_time("Selection Sort", dataset.count, dataset.max_value, sort_elapsed)
    del sorted_values


def option_verify() -> None:
    dataset = load_dataset()
    if dataset is None:
        return

    print("Calculando checksums del archivo original...")
    start = time.perf_counter()
    expected_sum, expected_xor = dataset.checksums()
    print(f"Checksums calculados en {format_seconds(time.perf_counter() - start)}.")

    files = [
        (COUNTING_FILE, "Counting Sort"),
        (SELECTION_FILE, "Selection Sort"),
        (HEAP_FILE, "Heap Sort"),
    ]

    print("\nVerificación de archivos:")
    print("Algoritmo       | Estado   | Cantidad       | Ascendente | Checksum")
    print("----------------+----------+----------------+------------+---------")

    for name, label in files:
        result = verify_file(
            data_path(name),
            dataset.count,
            expected_sum,
            expected_xor,
        )
        if not result.exists:
            print(f"{label:<15} | no existe")
            continue
        if result.error is not None:
            print(f"{label:<15} | ERROR: {result.error}")
            continue

        ok = result.ascending and result.checksum_ok
        state = "OK" if ok else "FALLA"
        ascending = "sí" if result.ascending else "no"
        checksum = "OK" if result.checksum_ok else "distinto"
        print(
            f"{label:<15} | {state:<8} | {fmt_int(result.count):<14} | "
            f"{ascending:<10} | {checksum}"
        )

    print(
        "\nChecksum OK significa misma cantidad, misma suma y mismo XOR que Datos.txt."
    )


def option_times() -> None:
    records = read_records()
    if not records:
        print(f"Todavía no hay tiempos registrados en {timing_path().name}.")
        return

    print(f"Registro: {timing_path()}")
    print("\nUltimas mediciones:")
    print("Fecha               | Operación                 | N           | Tiempo")
    print("--------------------+---------------------------+-------------+----------")
    for record in records[-30:]:
        print(
            f"{record.timestamp:<19} | {record.operation:<25} | "
            f"{fmt_int(record.count):<11} | {format_seconds(record.seconds)}"
        )
    if len(records) > 30:
        print(f"(se muestran las últimas 30 de {len(records)} mediciones)")

    latest: dict[str, TimeRecord] = {}
    for record in records:
        latest[record.operation] = record

    print("\nÚltimo tiempo por operación:")
    for operation, record in latest.items():
        print(
            f"  {operation}: {format_seconds(record.seconds)} "
            f"(N={fmt_int(record.count)})"
        )


# ---------------------------------------------------------------------------
# Árbol AVL
# ---------------------------------------------------------------------------


def show_avl(avl: AVLTree) -> None:
    print(f"Altura: {avl.height()}")
    print(f"Nodos únicos: {fmt_int(avl.node_count)}")
    print(f"Valores almacenados (con repeticiones): {fmt_int(avl.total_values)}")
    sample = avl.in_order(50)
    print("InOrden (primeros 50):")
    if not sample:
        print("  (árbol vacío)")
    for value, count in sample:
        print(f"  {fmt_int(value)} x {fmt_int(count)}")


def option_avl() -> None:
    global _avl

    while True:
        print("\n--- ÁRBOL AVL ---")
        if _avl is None:
            print("Estado: sin construir")
        else:
            print(
                f"Estado: {fmt_int(_avl.node_count)} nodos, "
                f"altura {_avl.height()}, "
                f"{fmt_int(_avl.total_values)} valores"
            )
        print("1) Construir con todos los datos")
        print("2) Insertar valor")
        print("3) Buscar valor")
        print("4) Eliminar valor")
        print("5) Mostrar altura, nodos e InOrden")
        print("6) Liberar árbol")
        print("0) Volver")

        option = input("Opción AVL: ").strip()

        if option in ("0", ""):
            return

        if option == "1":
            dataset = load_dataset()
            if dataset is None:
                continue
            if dataset.count > AVL_BUILD_WARNING:
                estimated = (
                    dataset.count * max(1, dataset.count.bit_length())
                ) / 100_000
                print(
                    f"Aviso: insertar {fmt_int(dataset.count)} valores puede "
                    f"tardar mucho (estimación muy aproximada: "
                    f"{format_seconds(estimated)})."
                )
                if not ask_yes_no("¿Construir el AVL igualmente?", default=False):
                    continue

            print("Construyendo AVL...")
            tree = AVLTree()
            start = time.perf_counter()
            tree.build(dataset.values, progress=progress_printer("AVL"))
            elapsed = time.perf_counter() - start
            _avl = tree
            print("Árbol construido.")
            show_avl(tree)
            record_time("AVL: construcción", dataset.count, dataset.max_value, elapsed)

        elif option in ("2", "3", "4", "5", "6"):
            if _avl is None:
                print("Primero construya el árbol (opción 1).")
                continue

            if option == "2":
                value = ask_int("Valor a insertar: ", minimum=0, maximum=UINT32_MAX)
                start = time.perf_counter()
                _avl.insert(value)
                elapsed = time.perf_counter() - start
                print(f"Valor insertado. Repeticiones actuales: {_avl.search(value)}")
                record_time(
                    "AVL: inserción", _avl.total_values, _avl.node_count, elapsed
                )

            elif option == "3":
                value = ask_int("Valor a buscar: ", minimum=0, maximum=UINT32_MAX)
                start = time.perf_counter()
                repetitions = _avl.search(value)
                elapsed = time.perf_counter() - start
                if repetitions:
                    print(f"Encontrado. Aparece {fmt_int(repetitions)} veces.")
                else:
                    print("El valor no está en el árbol.")
                record_time(
                    "AVL: búsqueda", _avl.total_values, _avl.node_count, elapsed
                )

            elif option == "4":
                value = ask_int("Valor a eliminar: ", minimum=0, maximum=UINT32_MAX)
                start = time.perf_counter()
                removed = _avl.delete(value)
                elapsed = time.perf_counter() - start
                if removed:
                    print("Valor eliminado (una aparición).")
                else:
                    print("El valor no está en el árbol.")
                record_time(
                    "AVL: eliminación", _avl.total_values, _avl.node_count, elapsed
                )

            elif option == "5":
                show_avl(_avl)

            else:
                _avl = None
                print("Árbol liberado de la memoria.")


# ---------------------------------------------------------------------------
# Heap
# ---------------------------------------------------------------------------


def show_heap(heap: BinaryHeap) -> None:
    print(f"Tipo: {heap.kind}")
    print(f"Elementos: {fmt_int(heap.size)}")
    root = heap.root()
    print(f"Raíz: {fmt_int(root) if root is not None else '(vacío)'}")
    print(f"Altura aproximada: {heap.height()}")


def option_heap() -> None:
    global _heap

    while True:
        print("\n--- HEAP BINARIO ---")
        if _heap is None:
            print("Estado: sin construir")
        else:
            print(
                f"Estado: {_heap.kind}, {fmt_int(_heap.size)} elementos, "
                f"raíz {fmt_int(_heap.root()) if _heap.root() is not None else '-'}"
            )
        print("1) Construir Max-Heap")
        print("2) Construir Min-Heap")
        print("3) Insertar valor")
        print("4) Buscar valor")
        print("5) Eliminar raíz (máximo o mínimo)")
        print("6) Mostrar cantidad, raíz y altura")
        print("7) Liberar heap")
        print("0) Volver")

        option = input("Opción Heap: ").strip()

        if option in ("0", ""):
            return

        if option in ("1", "2"):
            dataset = load_dataset()
            if dataset is None:
                continue
            if dataset.count > HEAP_BUILD_WARNING and not ask_yes_no(
                f"Construir un heap con {fmt_int(dataset.count)} elementos "
                "puede tardar. ¿Continuar?",
                default=False,
            ):
                continue

            is_max = option == "1"
            heap = BinaryHeap(is_max=is_max)
            print(f"Construyendo {heap.kind}...")
            start = time.perf_counter()
            heap.build(dataset.values, progress=progress_printer("Heap"))
            elapsed = time.perf_counter() - start
            _heap = heap
            show_heap(heap)
            record_time(
                f"Heap: construcción ({heap.kind})",
                dataset.count,
                dataset.max_value,
                elapsed,
            )

        elif option in ("3", "4", "5", "6", "7"):
            if _heap is None:
                print("Primero construya un heap (opciones 1 o 2).")
                continue

            if option == "3":
                value = ask_int("Valor a insertar: ", minimum=0, maximum=UINT32_MAX)
                start = time.perf_counter()
                _heap.insert(value)
                elapsed = time.perf_counter() - start
                print(f"Valor insertado. Elementos: {fmt_int(_heap.size)}")
                record_time("Heap: inserción", _heap.size, 0, elapsed)

            elif option == "4":
                value = ask_int("Valor a buscar: ", minimum=0, maximum=UINT32_MAX)
                print("Buscando (la búsqueda en heap es lineal)...")
                start = time.perf_counter()
                index = _heap.search(value)
                elapsed = time.perf_counter() - start
                if index >= 0:
                    print(f"Encontrado en el índice {fmt_int(index)}.")
                else:
                    print("El valor no está en el heap.")
                record_time("Heap: búsqueda", _heap.size, 0, elapsed)

            elif option == "5":
                start = time.perf_counter()
                removed = _heap.delete_root()
                elapsed = time.perf_counter() - start
                if removed is None:
                    print("El heap está vacío.")
                else:
                    print(f"Eliminado: {fmt_int(removed)}")
                record_time("Heap: eliminación de raíz", _heap.size, 0, elapsed)

            elif option == "6":
                show_heap(_heap)

            else:
                _heap = None
                print("Heap liberado de la memoria.")


# ---------------------------------------------------------------------------
# Heap Sort
# ---------------------------------------------------------------------------


def option_heap_sort() -> None:
    dataset = load_dataset()
    if dataset is None:
        return

    if dataset.count > HEAP_BUILD_WARNING and not ask_yes_no(
        f"Heap Sort con {fmt_int(dataset.count)} elementos puede tardar. ¿Continuar?",
        default=False,
    ):
        return

    print("Construyendo Max-Heap y aplicando Heap Sort...")
    start = time.perf_counter()
    sorted_values = heap_sort(dataset.values, progress=progress_printer("Heap Sort"))
    sort_elapsed = time.perf_counter() - start

    path = data_path(HEAP_FILE)
    print(f"Guardando {path.name}...")
    start = time.perf_counter()
    write_values(sorted_values, path, progress=progress_printer("Guardando"))
    write_elapsed = time.perf_counter() - start

    print(f"Archivo: {path}")
    print(f"Tiempo de ordenamiento: {format_seconds(sort_elapsed)}")
    print(f"Tiempo de escritura: {format_seconds(write_elapsed)}")

    # Verificación en memoria del resultado.
    expected_sum, expected_xor = dataset.checksums()
    result_sum, result_xor = values_checksum(sorted_values)
    ascending = is_sorted(sorted_values)
    same_data = (
        len(sorted_values) == dataset.count
        and result_sum == expected_sum
        and result_xor == expected_xor
    )
    print(
        f"Verificación: ascendente={'sí' if ascending else 'no'}, "
        f"mismos datos={'sí' if same_data else 'no'}"
    )

    record_time("Heap Sort", dataset.count, dataset.max_value, sort_elapsed)
    del sorted_values


# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------


def show_menu() -> None:
    print("\n===== ANÁLISIS DE DATOS =====")
    show_status()
    print(
        """
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
"""
    )


def dispatch(option: str) -> None:
    if option == "a":
        option_generate()
    elif option == "b":
        option_extremes()
    elif option == "c":
        option_frequency()
    elif option == "d":
        option_counting_sort()
    elif option == "e":
        option_selection_sort()
    elif option == "f":
        option_verify()
    elif option == "g":
        option_times()
    elif option == "i":
        option_avl()
    elif option == "j":
        option_heap()
    elif option == "k":
        option_heap_sort()
    else:
        print("Opción inválida.")


def main() -> None:
    """Punto de entrada del programa."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

    print("Análisis de grandes volúmenes de datos")
    print("Los archivos se guardan en:", data_path("").resolve())

    while True:
        try:
            show_menu()
            option = input("Seleccione una opción: ").strip().lower()
            if option in ("0", "salir"):
                print("Hasta luego.")
                return
            dispatch(option)
        except (KeyboardInterrupt, EOFError):
            print("\nHasta luego.")
            return
        except Exception as exc:  # noqa: BLE001 - evita que un error cierre el .exe.
            print(f"\nError: {exc}")


if __name__ == "__main__":
    main()
