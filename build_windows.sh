#!/usr/bin/env bash
# Genera dist/AnalisisDatos.exe desde Linux usando Docker o Podman.
#
# Uso:
#   chmod +x build_windows.sh   # solo la primera vez
#   ./build_windows.sh
#
# Variables opcionales:
#   CONTAINER_ENGINE=docker|podman   Fuerza el motor de contenedores.
#   IMAGE_NAME=nombre                Cambia el nombre de la imagen local.

set -euo pipefail

cd "$(dirname "$0")"

IMAGE_NAME="${IMAGE_NAME:-ayda-wine-builder}"
OUTPUT_DIR="$PWD/dist"

if [ -n "${CONTAINER_ENGINE:-}" ]; then
    ENGINE="$CONTAINER_ENGINE"
elif command -v docker >/dev/null 2>&1; then
    ENGINE="docker"
elif command -v podman >/dev/null 2>&1; then
    ENGINE="podman"
else
    echo "Error: se necesita Docker o Podman para compilar el .exe desde Linux." >&2
    exit 1
fi

if ! "$ENGINE" info >/dev/null 2>&1; then
    echo "Error: el motor de contenedores '$ENGINE' no está disponible." >&2
    echo "Verifique que el servicio esté iniciado y que su usuario tenga permisos." >&2
    exit 1
fi

# En hosts con SELinux (por ejemplo Fedora) el volumen necesita la etiqueta :Z.
MOUNT_SUFFIX=""
if command -v selinuxenabled >/dev/null 2>&1 && selinuxenabled; then
    MOUNT_SUFFIX=":Z"
fi

echo "Motor: $ENGINE"
echo "Construyendo la imagen $IMAGE_NAME..."
echo "(la primera vez descarga tobix/pywine:3.12, aproximadamente 1,3 GB)"
"$ENGINE" build -t "$IMAGE_NAME" .

# La compilación se hace en un directorio temporal montado en /app/dist.
# Así el .exe no queda con propietario root en dist/ y se evitan problemas de
# permisos con Docker o Podman.
TMP_DIR="$(mktemp -d)"
cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "Ejecutando PyInstaller dentro de Wine..."
"$ENGINE" run --rm \
    -v "$TMP_DIR:/app/dist$MOUNT_SUFFIX" \
    "$IMAGE_NAME"

if [ ! -f "$TMP_DIR/AnalisisDatos.exe" ]; then
    echo "Error: PyInstaller no generó AnalisisDatos.exe." >&2
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
cp "$TMP_DIR/AnalisisDatos.exe" "$OUTPUT_DIR/AnalisisDatos.exe"

echo
ls -lh "$OUTPUT_DIR/AnalisisDatos.exe"
echo "Listo: dist/AnalisisDatos.exe"
