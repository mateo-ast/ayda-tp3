"""Análisis de datos: máximo, mínimo y frecuencias."""

from __future__ import annotations

import heapq
from array import array
from collections import Counter

UINT64_MASK = 0xFFFF_FFFF_FFFF_FFFF


def find_extremes(values: array) -> tuple[int, int]:
    """Devuelve el mínimo y el máximo del arreglo."""
    return min(values), max(values)


def top_frequent(
    values: array, max_value: int, amount: int = 10
) -> list[tuple[int, int]]:
    """Devuelve los números más repetidos como (valor, repeticiones)."""
    if not values:
        return []

    # Con pocos datos conviene un diccionario; evita recorrer todo el rango.
    if len(values) <= 1_000_000:
        counter = Counter(values)
        ordered = sorted(
            counter.items(), key=lambda item: (item[1], item[0]), reverse=True
        )
        return [(value, count) for value, count in ordered[:amount]]

    # Con muchos datos se usa un arreglo de conteos de tamaño max_value + 1.
    counts = array("I", [0]) * (max_value + 1)
    for value in values:
        counts[value] += 1

    # Min-heap de tamaño amount para quedarnos con los mayores.
    best: list[tuple[int, int]] = []
    for value, count in enumerate(counts):
        if count == 0:
            continue
        item = (count, value)
        if len(best) < amount:
            heapq.heappush(best, item)
        elif item > best[0]:
            heapq.heapreplace(best, item)

    ordered = sorted(best, reverse=True)
    return [(value, count) for count, value in ordered]


def values_checksum(values: array) -> tuple[int, int]:
    """Calcula suma y XOR de un arreglo."""
    total = 0
    xor_value = 0
    for value in values:
        total += value
        xor_value ^= value
    return total & UINT64_MASK, xor_value


def is_sorted(values: array) -> bool:
    """Comprueba orden ascendente."""
    for index in range(1, len(values)):
        if values[index] < values[index - 1]:
            return False
    return True
