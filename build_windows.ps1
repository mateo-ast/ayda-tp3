# Compila el ejecutable de Windows.
# Ejecutar desde PowerShell, en la carpeta del proyecto:
#   powershell -ExecutionPolicy Bypass -File .\build_windows.ps1

$ErrorActionPreference = "Stop"

Write-Host "Sincronizando el entorno con uv..."
uv sync

Write-Host "Comprobando Python de 64 bits..."
uv run python -c "import struct; assert struct.calcsize('P') == 8, 'Se requiere Python de 64 bits'"

Write-Host "Compilando con PyInstaller..."
uv run --with pyinstaller pyinstaller --onefile --console --clean `
    --name AnalisisDatos --paths src run.py

Write-Host ""
Write-Host "Listo. Ejecutable: dist\AnalisisDatos.exe"
Write-Host "Copielo a una carpeta con permisos de escritura antes de ejecutarlo."
