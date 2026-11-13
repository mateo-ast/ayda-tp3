"""Configuración y rutas del programa."""

from __future__ import annotations

import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Devuelve la carpeta donde se guardan los datos.

    Si el programa está empaquetado como .exe, usa la carpeta del ejecutable.
    En desarrollo, usa la carpeta desde donde se ejecuta el programa.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


# Nombres de archivos exigidos por la consigna.
DATA_FILE = "Datos.txt"
COUNTING_FILE = "Datos_CountingSort.txt"
SELECTION_FILE = "Datos_SelectionSort.txt"
HEAP_FILE = "Datos_HeapSort.txt"
TIMING_FILE = "tiempos.log"

# Rango máximo por defecto: 0..100.000.000.
DEFAULT_MAX_VALUE = 100_000_000
