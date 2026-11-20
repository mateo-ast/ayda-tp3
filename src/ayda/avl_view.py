"""Dibujo del árbol AVL en la consola.

El dibujo se limita a una cantidad de nodos y a una profundidad máxima para
que un árbol con millones de claves no inunde la pantalla.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from typing import TextIO

from .avl import AVLTree, OperationReport

MAX_FULL_NODES = 63
DEFAULT_MAX_DEPTH = 4
LOCAL_MAX_DEPTH = 3

_COLORS = {
    "N": "\033[32m",  # nodo nuevo
    "C": "\033[32m",  # contador actualizado
    "R": "\033[33m",  # rotación
    "S": "\033[36m",  # sucesor
    "E": "\033[31m",  # eliminado
    "F": "\033[36m",  # encontrado en una búsqueda
}
_RESET = "\033[0m"

LEGEND = (
    "Leyenda: [N] nuevo  [C] contador  [R] rotación  "
    "[S] sucesor  [E] eliminado  [F] encontrado"
)


def color_supported(stream: TextIO | None = None) -> bool:
    """Indica si conviene usar colores ANSI en la salida."""
    if stream is None:
        stream = sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not getattr(stream, "isatty", lambda: False)():
        return False
    if os.name == "nt":
        return bool(
            os.environ.get("WT_SESSION")
            or os.environ.get("ANSICON")
            or os.environ.get("TERM")
        )
    return os.environ.get("TERM", "") not in ("", "dumb")


def _fmt(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def _is_full(avl: AVLTree, root: int, max_nodes: int) -> bool:
    return avl.subtree_size(root, max_nodes + 1) <= max_nodes


def is_partial(avl: AVLTree, root: int | None = None) -> bool:
    """Indica si el dibujo se recortó por tamaño."""
    if avl.root == -1:
        return False
    if root is None:
        root = avl.root
    return not _is_full(avl, root, MAX_FULL_NODES)


def _format_node(
    avl: AVLTree, node: int, marks: Mapping[int, str], use_color: bool
) -> str:
    text = f"{_fmt(avl.keys[node])} ({_fmt(avl.counts[node])})"
    mark = marks.get(node, "")
    if not mark:
        return text
    label = f"[{mark}]"
    if use_color:
        for letter in mark:
            color = _COLORS.get(letter)
            if color is not None:
                return f"{text}  {color}{label}{_RESET}"
    return f"{text}  {label}"


def render_tree(
    avl: AVLTree,
    root: int | None = None,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_nodes: int = MAX_FULL_NODES,
    marks: Mapping[int, str] | None = None,
    use_color: bool | None = None,
) -> list[str]:
    """Devuelve las líneas del árbol o subárbol que arranca en root.

    Si el subárbol tiene como máximo max_nodes nodos se dibuja completo; si no,
    se muestran max_depth niveles y se marca con "…" cada rama cortada.
    """
    if root is None:
        root = avl.root
    if root == -1:
        return ["(árbol vacío)"]
    if use_color is None:
        use_color = color_supported()
    if marks is None:
        marks = {}

    full = _is_full(avl, root, max_nodes)
    lines: list[str] = []

    def walk(node: int, continuation: str, is_last: bool, depth: int) -> None:
        connector = "" if depth == 0 else ("└── " if is_last else "├── ")
        text = _format_node(avl, node, marks, use_color)
        truncated = (
            not full
            and depth >= max_depth - 1
            and (avl.left[node] != -1 or avl.right[node] != -1)
        )
        if truncated:
            text += " …"
        lines.append(continuation + connector + text)
        if truncated:
            return

        next_continuation = continuation
        if depth > 0:
            next_continuation += "    " if is_last else "│   "
        children = [
            child for child in (avl.left[node], avl.right[node]) if child != -1
        ]
        for index, child in enumerate(children):
            walk(child, next_continuation, index == len(children) - 1, depth + 1)

    walk(root, "", False, 0)
    return lines


def _add_mark(marks: dict[int, str], avl: AVLTree, key: int, mark: str) -> None:
    node = avl.find_node(key)
    if node == -1:
        return
    current = marks.get(node, "")
    if mark not in current:
        marks[node] = current + mark


def _rotation_new_root_key(path: list[int], key: int, direction: str) -> int | None:
    """Clave que queda arriba de la rotación según el camino recorrido."""
    if key not in path:
        return None
    index = path.index(key)
    offset = 2 if "-" in direction else 1
    if index + offset >= len(path):
        return None
    return path[index + offset]


def marks_from_report(avl: AVLTree, report: OperationReport) -> dict[int, str]:
    """Marcas para resaltar en el dibujo los nodos que cambiaron."""
    marks: dict[int, str] = {}
    if report.created:
        _add_mark(marks, avl, report.key, "N")
    if report.count_changed:
        _add_mark(marks, avl, report.key, "C")
    if report.successor is not None:
        _add_mark(marks, avl, report.successor, "S")
    if report.removed and len(report.path) >= 2:
        _add_mark(marks, avl, report.path[-2], "E")
    for rotation in report.rotations:
        _add_mark(marks, avl, rotation.key, "R")
        new_root = _rotation_new_root_key(
            report.path, rotation.key, rotation.direction
        )
        if new_root is not None:
            _add_mark(marks, avl, new_root, "R")
    return marks


def _anchor_node(avl: AVLTree, keys: list[int]) -> int:
    """Elige un nodo desde el que dibujar el cambio o la búsqueda."""
    if not keys:
        return avl.root
    anchor_key = keys[max(0, len(keys) - 3)]
    node = avl.find_node(anchor_key)
    return node if node != -1 else avl.root


def render_changes(
    avl: AVLTree, report: OperationReport, use_color: bool | None = None
) -> list[str]:
    """Dibuja un subárbol cercano a las claves modificadas."""
    keys = list(report.path)
    if report.rotations:
        rotation = report.rotations[-1]
        new_root = _rotation_new_root_key(
            report.path, rotation.key, rotation.direction
        )
        if new_root is not None:
            keys = [new_root]
    return render_tree(
        avl,
        root=_anchor_node(avl, keys),
        max_depth=LOCAL_MAX_DEPTH,
        marks=marks_from_report(avl, report),
        use_color=use_color,
    )


def render_search(
    avl: AVLTree, path: list[int], key: int, use_color: bool | None = None
) -> list[str]:
    """Dibuja el subárbol recorrido en una búsqueda y resalta el resultado."""
    marks: dict[int, str] = {}
    node = avl.find_node(key)
    if node != -1:
        marks[node] = "F"
    return render_tree(
        avl,
        root=_anchor_node(avl, path),
        max_depth=LOCAL_MAX_DEPTH,
        marks=marks,
        use_color=use_color,
    )
