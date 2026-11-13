"""Algoritmos de ordenamiento implementados en Python puro."""

from __future__ import annotations

from array import array
from collections.abc import Callable
from itertools import accumulate

Progress = Callable[[int, int], None] | None


def counting_sort(values: array, max_value: int, progress: Progress = None) -> array:
    """Counting Sort estable. Complejidad O(n + k), con k = max_value.

    Se cuentan las apariciones, se calculan las posiciones acumuladas y se
    colocan los valores de atrás hacia adelante para conservar estabilidad.
    """
    total = len(values)
    if total == 0:
        return array("I")

    counts = array("I", [0]) * (max_value + 1)
    for index, value in enumerate(values):
        counts[value] += 1
        if progress is not None and index % 5_000_000 == 0:
            progress(index + 1, total)

    # Suma prefija: counts[v] indica cuántos valores son <= v.
    counts = array("I", accumulate(counts))

    result = array("I", [0]) * total
    for index in range(total - 1, -1, -1):
        value = values[index]
        counts[value] -= 1
        result[counts[value]] = value
        if progress is not None and index % 5_000_000 == 0:
            progress(total - index, total)

    if progress is not None:
        progress(total, total)
    return result


def selection_sort(values: array, progress: Progress = None) -> array:
    """Selection Sort. Complejidad O(n^2).

    En cada pasada busca el menor del resto y lo intercambia con la posición
    actual. Se ordena una copia para no modificar los datos originales.
    """
    result = array("I", values)
    total = len(result)
    if total < 2:
        return result

    step = max(1, total // 100)
    for index in range(total - 1):
        min_index = index
        min_value = result[index]
        for other in range(index + 1, total):
            value = result[other]
            if value < min_value:
                min_value = value
                min_index = other

        if min_index != index:
            result[index], result[min_index] = result[min_index], result[index]

        if progress is not None and index % step == 0:
            progress(index + 1, total)

    if progress is not None:
        progress(total, total)
    return result


def _sift_down(values: array, start: int, size: int) -> None:
    """Baja un valor en un Max-Heap hasta recuperar la propiedad."""
    root = start
    while True:
        child = 2 * root + 1
        if child >= size:
            break

        right = child + 1
        if right < size and values[right] > values[child]:
            child = right

        if values[root] >= values[child]:
            break

        values[root], values[child] = values[child], values[root]
        root = child


def heap_sort(values: array, progress: Progress = None) -> array:
    """Heap Sort ascendente. Complejidad O(n log n).

    Primero construye un Max-Heap y luego mueve el máximo al final.
    """
    result = array("I", values)
    total = len(result)
    if total < 2:
        return result

    # Construcción del Max-Heap en O(n).
    for start in range(total // 2 - 1, -1, -1):
        _sift_down(result, start, total)

    step = max(1, total // 100)
    for end in range(total - 1, 0, -1):
        result[0], result[end] = result[end], result[0]
        _sift_down(result, 0, end)
        if progress is not None and (total - end) % step == 0:
            progress(total - end, total)

    if progress is not None:
        progress(total, total)
    return result
