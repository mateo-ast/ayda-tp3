"""Árbol AVL con contador de repeticiones.

Los nodos se guardan en arreglos para ahorrar memoria. Cada clave única
aparece una sola vez y el arreglo counts indica cuántas veces se repite.
"""

from __future__ import annotations

from array import array
from collections.abc import Callable
from dataclasses import dataclass, field

Progress = Callable[[int, int], None] | None


@dataclass
class Rotation:
    """Rotación aplicada durante una operación.

    direction es "izquierda", "derecha", "izquierda-derecha" o
    "derecha-izquierda"; key es la clave del nodo sobre el que se aplicó.
    """

    direction: str
    key: int


@dataclass
class OperationReport:
    """Detalle de lo que cambió una inserción o eliminación."""

    operation: str = ""
    key: int = 0
    found: bool = False
    path: list[int] = field(default_factory=list)
    created: bool = False
    count_before: int = 0
    count_after: int = 0
    count_changed: bool = False
    removed: bool = False
    successor: int | None = None
    rotations: list[Rotation] = field(default_factory=list)
    height_before: int = 0
    height_after: int = 0
    nodes_before: int = 0
    nodes_after: int = 0
    values_before: int = 0
    values_after: int = 0


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

    def _rebalance(self, node: int, report: OperationReport | None = None) -> int:
        self._update_height(node)
        balance = self._height(self.left[node]) - self._height(self.right[node])

        if balance > 1:
            left = self.left[node]
            if self._height(self.left[left]) < self._height(self.right[left]):
                self.left[node] = self._rotate_left(left)
                if report is not None:
                    report.rotations.append(
                        Rotation("izquierda-derecha", self.keys[node])
                    )
                return self._rotate_right(node)
            if report is not None:
                report.rotations.append(Rotation("derecha", self.keys[node]))
            return self._rotate_right(node)

        if balance < -1:
            right = self.right[node]
            if self._height(self.right[right]) < self._height(self.left[right]):
                self.right[node] = self._rotate_right(right)
                if report is not None:
                    report.rotations.append(
                        Rotation("derecha-izquierda", self.keys[node])
                    )
                return self._rotate_left(node)
            if report is not None:
                report.rotations.append(Rotation("izquierda", self.keys[node]))
            return self._rotate_left(node)

        return node

    def _start_report(self, report: OperationReport, operation: str, key: int) -> None:
        report.operation = operation
        report.key = key
        report.height_before = self.height()
        report.nodes_before = self._active_nodes
        report.values_before = self.total_values

    def _finish_report(self, report: OperationReport) -> None:
        report.height_after = self.height()
        report.nodes_after = self._active_nodes
        report.values_after = self.total_values

    def _insert(
        self, node: int, key: int, report: OperationReport | None = None
    ) -> int:
        if node == -1:
            self.total_values += 1
            if report is not None:
                report.path.append(key)
                report.created = True
            return self._new_node(key)

        current = self.keys[node]
        if report is not None:
            report.path.append(current)
        if key == current:
            if report is not None:
                report.count_before = self.counts[node]
            self.counts[node] += 1
            self.total_values += 1
            if report is not None:
                report.count_after = self.counts[node]
                report.count_changed = True
            return node

        if key < current:
            self.left[node] = self._insert(self.left[node], key, report)
        else:
            self.right[node] = self._insert(self.right[node], key, report)

        return self._rebalance(node, report)

    def insert(self, key: int, report: OperationReport | None = None) -> None:
        """Inserta una clave; si ya existe, aumenta su contador.

        Si se pasa un reporte, se completa con el detalle de la operación.
        """
        if report is not None:
            self._start_report(report, "inserción", key)
        self.root = self._insert(self.root, key, report)
        if report is not None:
            report.found = True
            self._finish_report(report)

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

    def _remove_node(
        self, node: int, key: int, report: OperationReport | None = None
    ) -> int:
        if node == -1:
            return -1

        current = self.keys[node]
        if key < current:
            self.left[node] = self._remove_node(self.left[node], key, report)
        elif key > current:
            self.right[node] = self._remove_node(self.right[node], key, report)
        else:
            if self.left[node] == -1:
                self._active_nodes -= 1
                return self.right[node]
            if self.right[node] == -1:
                self._active_nodes -= 1
                return self.left[node]

            successor = self._min_node(self.right[node])
            if report is not None:
                report.successor = self.keys[successor]
            successor_key = self.keys[successor]
            self.keys[node] = successor_key
            self.counts[node] = self.counts[successor]
            self.right[node] = self._remove_node(self.right[node], successor_key, report)

        return self._rebalance(node, report)

    def delete(self, key: int, report: OperationReport | None = None) -> bool:
        """Elimina una aparición de la clave. Devuelve False si no existe.

        Si se pasa un reporte, se completa con el detalle de la operación.
        """
        if report is not None:
            self._start_report(report, "eliminación", key)

        node = self.root
        while node != -1:
            current = self.keys[node]
            if report is not None:
                report.path.append(current)
            if key == current:
                break
            node = self.left[node] if key < current else self.right[node]

        if node == -1:
            if report is not None:
                self._finish_report(report)
            return False

        if report is not None:
            report.found = True
        if self.counts[node] > 1:
            if report is not None:
                report.count_before = self.counts[node]
            self.counts[node] -= 1
            self.total_values -= 1
            if report is not None:
                report.count_after = self.counts[node]
                report.count_changed = True
                self._finish_report(report)
            return True

        if report is not None:
            report.removed = True
            report.count_before = 1
            report.count_after = 0
        self.root = self._remove_node(self.root, key, report)
        self.total_values -= 1
        if report is not None:
            self._finish_report(report)
        return True

    def find_node(self, key: int) -> int:
        """Devuelve el índice del nodo con esa clave, o -1 si no existe."""
        node = self.root
        while node != -1:
            current = self.keys[node]
            if key == current:
                return node
            node = self.left[node] if key < current else self.right[node]
        return -1

    def search_path(self, key: int) -> list[int]:
        """Claves visitadas al buscar una clave, incluida la clave final."""
        path: list[int] = []
        node = self.root
        while node != -1:
            current = self.keys[node]
            path.append(current)
            if key == current:
                break
            node = self.left[node] if key < current else self.right[node]
        return path

    def subtree_size(self, node: int, limit: int | None = None) -> int:
        """Cantidad de nodos del subárbol, como máximo limit."""
        if node == -1:
            return 0
        count = 0
        stack = [node]
        while stack:
            current = stack.pop()
            if current == -1:
                continue
            count += 1
            if limit is not None and count >= limit:
                return count
            stack.append(self.left[current])
            stack.append(self.right[current])
        return count

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
