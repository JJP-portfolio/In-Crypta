#!/usr/bin/env bash
# ==============================================================================
# publicar_gd_games.sh — Compilador HTML5 GDevelop 5.6 y Lanzador gd.games
# Proyecto: IN CRYPTA (1.0.0)
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROYECTO_JSON="${ROOT_DIR}/export/gdevelop_nativo/IN_CRYPTA_NATIVO.json"
BUILD_DIR="${ROOT_DIR}/export/gdevelop_nativo/build"
ZIP_FILE="${ROOT_DIR}/export/IN_CRYPTA_1.0.0_HTML5_GDGAMES.zip"
EMPAQUETADOR="${ROOT_DIR}/tools/empaquetar_gd_games.py"

MODO="${1:---open-ide}"

mostrar_pasos_gd_games() {
    cat <<EOF

================================================================================
  PASOS PARA OBTENER EL LINK PÚBLICO EN GD.GAMES (GDevelop 5.6)
================================================================================
  Proyecto nativo : ${PROYECTO_JSON}
  Paquete HTML5   : ${ZIP_FILE}

  Con el proyecto abierto en GDevelop 5.6:
    1) Haz clic en el botón "Share" (Compartir / Exportar) en la barra superior.
    2) Selecciona "gd.games" -> "One-click packaging for web (gd.games)".
    3) Haz clic en "Publish game" (o "Generate link") y copia la URL pública:
       https://gd.games/<tu-usuario>/in-crypta

  Alternativa con el ZIP HTML5 ya compilado (${ZIP_FILE}):
    - Contiene index.html en la raíz del archivo ZIP (100% autónomo).
    - Puedes subirlo directamente a itch.io, GitHub Pages, Netlify o servidor web.
================================================================================
EOF
}

ejecutar_empaquetado() {
    echo ">>> Ejecutando compilación y empaquetado GDevelop 5.6 HTML5..."
    python3 "${EMPAQUETADOR}"
}

case "${MODO}" in
    --check)
        ejecutar_empaquetado

        echo ""
        echo ">>> Verificando artefactos generados..."
        if [[ ! -f "${BUILD_DIR}/index.html" ]]; then
            echo "ERROR: No se encontró ${BUILD_DIR}/index.html" >&2
            exit 1
        fi
        if [[ ! -f "${BUILD_DIR}/data.js" ]]; then
            echo "ERROR: No se encontró ${BUILD_DIR}/data.js" >&2
            exit 1
        fi
        if [[ ! -f "${ZIP_FILE}" ]]; then
            echo "ERROR: No se encontró ${ZIP_FILE}" >&2
            exit 1
        fi

        echo ">>> Probando servidor HTTP temporal sobre ${BUILD_DIR}..."
        python3 - "${BUILD_DIR}" <<'PYEOF'
import functools
import http.server
import socketserver
import sys
import threading
import urllib.request
from pathlib import Path

build_dir = Path(sys.argv[1]).resolve()
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(build_dir))

class QuietServer(socketserver.TCPServer):
    allow_reuse_address = True

with QuietServer(("127.0.0.1", 0), handler) as httpd:
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        for ruta in ("/index.html", "/data.js", "/assets/titulo.png"):
            url = f"http://127.0.0.1:{port}{ruta}"
            with urllib.request.urlopen(url, timeout=5) as resp:
                status = resp.status
                body = resp.read()
                if status != 200 or len(body) == 0:
                    raise RuntimeError(f"Respuesta inválida para {ruta}: HTTP {status} ({len(body)} bytes)")
                print(f"    [HTTP {status} OK] {ruta} ({len(body):,} bytes)")
    finally:
        httpd.shutdown()
PYEOF

        echo ""
        echo "✔ CHECK OK: Build HTML5 de GDevelop 5.6 y paquete ZIP validados correctamente."
        mostrar_pasos_gd_games
        ;;

    --play)
        ejecutar_empaquetado
        PUERTO="${PORT:-8080}"
        URL="http://localhost:${PUERTO}/index.html"
        echo ""
        echo ">>> Iniciando servidor web para jugar IN CRYPTA (GDevelop 5.6 HTML5)..."
        echo ">>> URL: ${URL}"
        echo ">>> Presiona Ctrl+C para detener el servidor."
        if command -v xdg-open >/dev/null 2>&1; then
            (sleep 1 && xdg-open "${URL}" >/dev/null 2>&1 || true) &
        fi
        exec python3 -m http.server "${PUERTO}" --bind 127.0.0.1 --directory "${BUILD_DIR}"
        ;;

    --open-ide)
        ejecutar_empaquetado
        mostrar_pasos_gd_games

        if command -v flatpak >/dev/null 2>&1 && flatpak info io.gdevelop.ide >/dev/null 2>&1; then
            echo ">>> Abriendo ${PROYECTO_JSON} en GDevelop 5.6 (Flatpak io.gdevelop.ide)..."
            nohup flatpak run --filesystem="${ROOT_DIR}" io.gdevelop.ide "${PROYECTO_JSON}" >/dev/null 2>&1 &
            echo "✔ GDevelop 5.6 lanzado en segundo plano con el proyecto cargado."
        elif command -v xdg-open >/dev/null 2>&1; then
            echo ">>> Abriendo https://editor.gdevelop.io en el navegador..."
            xdg-open "https://editor.gdevelop.io" >/dev/null 2>&1 || true
        else
            echo ">>> Abre manualmente ${PROYECTO_JSON} en GDevelop 5.6 o en https://editor.gdevelop.io"
        fi
        ;;

    -h|--help)
        cat <<EOF
Uso: ./publicar_gd_games.sh [--check | --play | --open-ide]

Opciones:
  --check      Compila el proyecto nativo de GDevelop 5.6, genera el ZIP HTML5
               y verifica mediante servidor HTTP local que /index.html y /data.js
               respondan HTTP 200 OK.
  --play       Compila el build HTML5 y levanta un servidor en http://localhost:8080/index.html
               abriéndolo en el navegador para jugar inmediatamente.
  --open-ide   (Por defecto) Compila/actualiza el proyecto, muestra los 3 pasos para
               publicar en gd.games y abre IN_CRYPTA_NATIVO.json en GDevelop 5.6.
EOF
        ;;

    *)
        echo "Opción no reconocida: ${MODO}" >&2
        echo "Usa: ./publicar_gd_games.sh [--check | --play | --open-ide]" >&2
        exit 1
        ;;
esac
