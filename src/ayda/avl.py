"""Árbol AVL con contador de repeticiones.

Los nodos se guardan en arreglos para ahorrar memoria. Cada clave única
aparece una sola vez y el arreglo counts indica cuántas veces se repite.
"""

from __future__ import annotations

from array import array
from collections.abc import Callable

Progress = Callable[[int, int], None] | None


class AVLTree:
    """Árbol AVL balanceado."""

    def __init__(self) -> None:
        self.keys = array("I")
        self.counts = array("I")
        self.left = array("i")
        self.right = array("i")
        self.heights = array("i")
        self.root = -1
        self.total_values = 0
        self._active_nodes = 0

    @property
    def node_count(self) -> int:
        """Cantidad de claves únicas (nodos activos)."""
        return self._active_nodes

    def height(self) -> int:
        """Altura del árbol (0 si está vacío)."""
        return self._height(self.root)

    def _height(self, node: int) -> int:
        return self.heights[node] if node != -1 else 0

    def _update_height(self, node: int) -> None:
        self.heights[node] = 1 + max(
            self._height(self.left[node]), self._height(self.right[node])
        )

    def _new_node(self, key: int) -> int:
        node = len(self.keys)
        self.keys.append(key)
        self.counts.append(1)
        self.left.append(-1)
        self.right.append(-1)
        self.heights.append(1)
        self._active_nodes += 1
        return node

    def _rotate_left(self, node: int) -> int:
        new_root = self.right[node]
        self.right[node] = self.left[new_root]
        self.left[new_root] = node
        self._update_height(node)
        self._update_height(new_root)
        return new_root

    def _rotate_right(self, node: int) -> int:
        new_root = self.left[node]
        self.left[node] = self.right[new_root]
        self.right[new_root] = node
        self._update_height(node)
        self._update_height(new_root)
        return new_root

    def _rebalance(self, node: int) -> int:
        self._update_height(node)
        balance = self._height(self.left[node]) - self._height(self.right[node])

        if balance > 1:
            left = self.left[node]
            if self._height(self.left[left]) < self._height(self.right[left]):
                self.left[node] = self._rotate_left(left)
            return self._rotate_right(node)

        if balance < -1:
            right = self.right[node]
            if self._height(self.right[right]) < self._height(self.left[right]):
                self.right[node] = self._rotate_right(right)
            return self._rotate_left(node)

        return node

    def _insert(self, node: int, key: int) -> int:
        if node == -1:
            self.total_values += 1
            return self._new_node(key)

        current = self.keys[node]
        if key == current:
            self.counts[node] += 1
            self.total_values += 1
            return node

        if key < current:
            self.left[node] = self._insert(self.left[node], key)
        else:
            self.right[node] = self._insert(self.right[node], key)

        return self._rebalance(node)

    def insert(self, key: int) -> None:
        """Inserta una clave; si ya existe, aumenta su contador."""
        self.root = self._insert(self.root, key)

    def build(self, values: array, progress: Progress = None) -> None:
        """Inserta todos los valores del arreglo."""
        total = len(values)
        for index, value in enumerate(values):
            self.insert(value)
            if progress is not None and (index + 1) % 100_000 == 0:
                progress(index + 1, total)
        if progress is not None:
            progress(total, total)

    def search(self, key: int) -> int:
        """Devuelve cuántas veces aparece la clave (0 si no existe)."""
        node = self.root
        while node != -1:
            current = self.keys[node]
            if key == current:
                return self.counts[node]
            node = self.left[node] if key < current else self.right[node]
        return 0

    def _min_node(self, node: int) -> int:
        while self.left[node] != -1:
            node = self.left[node]
        return node

    def _remove_node(self, node: int, key: int) -> int:
        if node == -1:
            return -1

        current = self.keys[node]
        if key < current:
            self.left[node] = self._remove_node(self.left[node], key)
        elif key > current:
            self.right[node] = self._remove_node(self.right[node], key)
        else:
            if self.left[node] == -1:
                self._active_nodes -= 1
                return self.right[node]
            if self.right[node] == -1:
                self._active_nodes -= 1
                return self.left[node]

            successor = self._min_node(self.right[node])
            self.keys[node] = self.keys[successor]
            self.counts[node] = self.counts[successor]
            self.right[node] = self._remove_node(self.right[node], self.keys[successor])

        return self._rebalance(node)

    def delete(self, key: int) -> bool:
        """Elimina una aparición de la clave. Devuelve False si no existe."""
        node = self.root
        while node != -1:
            current = self.keys[node]
            if key == current:
                break
            node = self.left[node] if key < current else self.right[node]

        if node == -1:
            return False

        if self.counts[node] > 1:
            self.counts[node] -= 1
            self.total_values -= 1
            return True

        self.root = self._remove_node(self.root, key)
        self.total_values -= 1
        return True

    def in_order(self, limit: int = 15) -> list[tuple[int, int]]:
        """Devuelve (valor, repeticiones) en InOrden, hasta el límite."""
        result: list[tuple[int, int]] = []
        stack: list[int] = []
        node = self.root

        while (stack or node != -1) and len(result) < limit:
            while node != -1:
                stack.append(node)
                node = self.left[node]
            node = stack.pop()
            result.append((self.keys[node], self.counts[node]))
            node = self.right[node]

        return result
