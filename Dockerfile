# Imagen para generar AnalisisDatos.exe desde Linux usando Wine.
# Se usa a través de build_windows.sh.
#
# PyInstaller no hace compilación cruzada: dentro del contenedor se ejecuta el
# Python de Windows sobre Wine, por lo que el resultado es un .exe nativo.

# Nombre completo para que Podman no pida confirmar el registro (short-name).
FROM docker.io/tobix/pywine:3.12

# Evitar mensajes interactivos de Wine.
ENV WINEDEBUG=-all

WORKDIR /app

# Instalar uv dentro del entorno Windows de Wine.
# PyInstaller ya viene en la imagen, pero se deja explícito por si cambia.
RUN wine pip install --no-warn-script-location uv pyinstaller

# Copiar primero las definiciones de dependencias (aprovecha la caché).
COPY pyproject.toml uv.lock ./

# Instalar las dependencias del proyecto en el Python de Windows.
RUN wine uv pip install --system -r pyproject.toml

# Copiar el resto del código fuente.
COPY . .

# Generar el ejecutable en /tmp y copiarlo a dist/.
# Se compila fuera de dist/ porque ese directorio suele montarse desde el host
# y PyInstaller no puede borrar un punto de montaje al usar --noconfirm.
# --noupx evita falsos positivos de antivirus y problemas al ejecutar el .exe
# con Wine (la DLL de Python comprimida con UPX no siempre carga).
CMD ["sh", "-c", "wine pyinstaller --onefile --console --clean --noconfirm --noupx --name AnalisisDatos --paths src --distpath /tmp/ayda-dist run.py && cp /tmp/ayda-dist/AnalisisDatos.exe /app/dist/AnalisisDatos.exe"]
