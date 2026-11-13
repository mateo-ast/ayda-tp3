"""Generación, lectura y escritura de Datos.txt y archivos ordenados."""

from __future__ import annotations

import os
import random
from array import array
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .config import DATA_FILE, get_base_dir

CHUNK_VALUES = 100_000
READ_BLOCK = 16 * 1024 * 1024
UINT64_MASK = 0xFFFF_FFFF_FFFF_FFFF

Progress = Callable[[int, int], None] | None


class DataError(Exception):
    """Error controlado al leer o escribir datos."""


@dataclass
class Dataset:
    """Datos cargados en memoria."""

    values: array
    max_value: int
    path: Path
    mtime: float
    size: int
    _checksum_sum: int | None = field(default=None, repr=False)
    _checksum_xor: int | None = field(default=None, repr=False)

    @property
    def count(self) -> int:
        return len(self.values)

    def checksums(self) -> tuple[int, int]:
        """Calcula suma y XOR de todos los valores (se guardan en caché)."""
        if self._checksum_sum is None or self._checksum_xor is None:
            total = 0
            xor_value = 0
            for value in self.values:
                total += value
                xor_value ^= value
            self._checksum_sum = total & UINT64_MASK
            self._checksum_xor = xor_value
        return self._checksum_sum, self._checksum_xor


@dataclass
class VerificationResult:
    """Resultado de verificar un archivo ordenado."""

    path: Path
    exists: bool
    count: int = 0
    ascending: bool = False
    checksum_ok: bool = False
    error: str | None = None


def data_path(name: str) -> Path:
    return get_base_dir() / name


def human_size(size_bytes: int) -> str:
    """Devuelve un tamaño en MB o GB."""
    if size_bytes >= 1024**3:
        return f"{size_bytes / (1024**3):.2f} GB"
    return f"{size_bytes / (1024**2):.2f} MB"


def _iter_ints(path: Path) -> Iterator[int]:
    """Lee enteros por bloques sin cargar todo el archivo como texto."""
    with open(path, "rb") as file:
        carry = b""
        while True:
            block = file.read(READ_BLOCK)
            if not block:
                break

            data = carry + block if carry else block
            parts = data.split()

            # Si el bloque corta un número, se guarda para el siguiente bloque.
            if block[-1] not in b" \t\r\n":
                carry = parts.pop() if parts else data
            else:
                carry = b""

            for part in parts:
                yield int(part)

        if carry:
            yield int(carry)


def generate_data(
    count: int,
    max_value: int,
    seed: int | None = None,
    progress: Progress = None,
) -> int:
    """Genera Datos.txt y devuelve la semilla usada.

    Escribe por bloques para no mantener millones de textos en memoria.
    """
    if count <= 0:
        raise DataError("La cantidad de números debe ser mayor que cero.")
    if max_value < 0:
        raise DataError("El valor máximo no puede ser negativo.")

    if seed is None:
        seed = int.from_bytes(os.urandom(8), "little")

    rng = random.Random(seed)
    limit = max_value + 1
    path = data_path(DATA_FILE)
    temp_path = path.with_name(path.name + ".tmp")

    try:
        with open(temp_path, "w", encoding="ascii", newline="\n") as file:
            done = 0
            while done < count:
                size = min(CHUNK_VALUES, count - done)
                # random() es rápido y el sesgo de coma flotante es despreciable.
                chunk = [str(int(rng.random() * limit)) for _ in range(size)]
                file.write("\n".join(chunk))
                file.write("\n")
                done += size
                if progress is not None:
                    progress(done, count)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()

    return seed


def load_data(path: Path | None = None) -> Dataset:
    """Carga Datos.txt en un array de enteros de 32 bits."""
    path = path or data_path(DATA_FILE)
    if not path.exists():
        raise DataError(f"No existe el archivo {path.name}.")

    values = array("I")
    try:
        for value in _iter_ints(path):
            values.append(value)
    except (ValueError, OverflowError) as exc:
        raise DataError(f"El archivo contiene un valor inválido: {exc}") from exc

    if not values:
        raise DataError("El archivo de datos está vacío.")

    stat = path.stat()
    return Dataset(
        values=values,
        max_value=max(values),
        path=path,
        mtime=stat.st_mtime,
        size=stat.st_size,
    )


def write_values(values: array, path: Path, progress: Progress = None) -> None:
    """Guarda los valores en un archivo de texto, uno por línea."""
    temp_path = path.with_name(path.name + ".tmp")
    total = len(values)

    try:
        with open(temp_path, "w", encoding="ascii", newline="\n") as file:
            done = 0
            while done < total:
                end = min(done + CHUNK_VALUES, total)
                chunk = values[done:end]
                file.write("\n".join(map(str, chunk)))
                file.write("\n")
                done = end
                if progress is not None:
                    progress(done, total)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def verify_file(
    path: Path,
    expected_count: int,
    expected_sum: int,
    expected_xor: int,
    progress: Progress = None,
) -> VerificationResult:
    """Verifica orden ascendente, cantidad y checksums de un archivo."""
    if not path.exists():
        return VerificationResult(path=path, exists=False)

    count = 0
    total = 0
    xor_value = 0
    previous = -1
    ascending = True

    try:
        for value in _iter_ints(path):
            if count > 0 and value < previous:
                ascending = False
            previous = value
            total += value
            xor_value ^= value
            count += 1
            if progress is not None and count % 5_000_000 == 0:
                progress(count, 0)
    except (ValueError, OverflowError) as exc:
        return VerificationResult(
            path=path,
            exists=True,
            error=f"Valor inválido: {exc}",
        )

    checksum_ok = (
        count == expected_count
        and (total & UINT64_MASK) == expected_sum
        and xor_value == expected_xor
    )
    return VerificationResult(
        path=path,
        exists=True,
        count=count,
        ascending=ascending,
        checksum_ok=checksum_ok,
    )


def is_sorted(values: array) -> bool:
    """Comprueba si un arreglo está ordenado de menor a mayor."""
    for index in range(1, len(values)):
        if values[index] < values[index - 1]:
            return False
    return True
