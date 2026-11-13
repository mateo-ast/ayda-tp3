"""Medición de tiempos y registro en tiempos.log."""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path

from .config import TIMING_FILE, get_base_dir


@dataclass
class TimeRecord:
    """Una línea del registro de tiempos."""

    timestamp: str
    operation: str
    count: int
    max_value: int
    seconds: float


def format_seconds(seconds: float) -> str:
    """Convierte segundos a un texto corto y legible."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f} us"
    if seconds < 1:
        return f"{seconds * 1_000:.1f} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"
    if seconds < 3_600:
        return f"{seconds / 60:.2f} min"
    if seconds < 86_400:
        return f"{seconds / 3_600:.2f} h"
    return f"{seconds / 86_400:.2f} dias"


def timing_path() -> Path:
    return get_base_dir() / TIMING_FILE


def log_time(operation: str, count: int, max_value: int, seconds: float) -> None:
    """Agrega una medición al archivo de tiempos."""
    path = timing_path()
    new_file = not path.exists()
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "a", encoding="utf-8", newline="\n") as file:
        if new_file:
            file.write("# fecha | operacion | n | max | segundos\n")
        file.write(f"{stamp} | {operation} | {count} | {max_value} | {seconds:.6f}\n")


def read_records() -> list[TimeRecord]:
    """Lee el registro de tiempos, ignorando líneas inválidas."""
    path = timing_path()
    if not path.exists():
        return []

    records: list[TimeRecord] = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 5:
                continue
            try:
                records.append(
                    TimeRecord(
                        timestamp=parts[0],
                        operation=parts[1],
                        count=int(parts[2]),
                        max_value=int(parts[3]),
                        seconds=float(parts[4]),
                    )
                )
            except ValueError:
                continue
    return records
