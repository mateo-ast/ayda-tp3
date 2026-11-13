"""Punto de entrada para desarrollo y para PyInstaller."""

from __future__ import annotations

import sys
from pathlib import Path

# En desarrollo, agrega src/ al camino de importación.
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from ayda.main import main

if __name__ == "__main__":
    main()
