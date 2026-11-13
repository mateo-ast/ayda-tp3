"""Heap binario (Max-Heap y Min-Heap)."""

from __future__ import annotations

from array import array
from collections.abc import Callable

Progress = Callable[[int, int], None] | None


class BinaryHeap:
    """Heap binario implementado sobre un arreglo."""

    def __init__(self, is_max: bool = True) -> None:
        self.is_max = is_max
        self.data = array("I")

    @property
    def size(self) -> int:
        return len(self.data)

    @property
    def kind(self) -> str:
        return "Max-Heap" if self.is_max else "Min-Heap"

    def height(self) -> int:
        """Altura aproximada de un árbol binario casi completo."""
        return self.size.bit_length()

    def root(self) -> int | None:
        return self.data[0] if self.data else None

    def _sift_down(self, index: int, size: int) -> None:
        data = self.data
        is_max = self.is_max

        while True:
            child = 2 * index + 1
            if child >= size:
                break

            right = child + 1
            if is_max:
                if right < size and data[right] > data[child]:
                    child = right
                if data[index] >= data[child]:
                    break
            else:
                if right < size and data[right] < data[child]:
                    child = right
                if data[index] <= data[child]:
                    break

            data[index], data[child] = data[child], data[index]
            index = child

    def _sift_up(self, index: int) -> None:
        data = self.data
        is_max = self.is_max

        while index > 0:
            parent = (index - 1) // 2
            if is_max:
                if data[index] <= data[parent]:
                    break
            else:
                if data[index] >= data[parent]:
                    break
            data[index], data[parent] = data[parent], data[index]
            index = parent

    def build(self, values: array, progress: Progress = None) -> None:
        """Construye el heap con heapify en O(n)."""
        self.data = array("I", values)
        total = len(self.data)
        if total < 2:
            return

        step = max(1, total // 100)
        for start in range(total // 2 - 1, -1, -1):
            self._sift_down(start, total)
            if progress is not None and (total // 2 - start) % step == 0:
                progress(total // 2 - start, total // 2)

        if progress is not None:
            progress(total // 2, total // 2)

    def insert(self, value: int) -> None:
        """Inserta un elemento y lo sube hasta su posición."""
        self.data.append(value)
        self._sift_up(len(self.data) - 1)

    def search(self, value: int) -> int:
        """Búsqueda lineal. Devuelve el índice o -1."""
        for index, current in enumerate(self.data):
            if current == value:
                return index
        return -1

    def delete_root(self) -> int | None:
        """Elimina y devuelve la raíz (máximo o mínimo)."""
        if not self.data:
            return None

        root = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            self._sift_down(0, len(self.data))
        return root
