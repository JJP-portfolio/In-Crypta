#!/usr/bin/env bash
# ============================================================================
# jugar_web.sh — Lanzador nativo Linux para IN CRYPTA (Web Runtime / PixiJS)
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"

# Autodetección del intérprete Python (.venv prioritario)
if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
else
    echo "✘ Error: No se encontró una instalación de Python (.venv/bin/python o python3)." >&2
    exit 1
fi

PORT="${PORT:-8000}"
WEB_HTML="export/gdevelop/index.html"
WEB_JSON="export/gdevelop/game_data.json"

mostrar_banner() {
    echo "========================================================"
    echo "  IN CRYPTA 1.0.0 - Plataforma Web (GDevelop JS / PixiJS)"
    echo "========================================================"
    echo "  Directorio : $SCRIPT_DIR"
    echo "  Intérprete : $PYTHON_BIN"
    echo "========================================================"
}

mostrar_ayuda() {
    mostrar_banner
    echo ""
    echo "Uso: [PORT=8000] ./jugar_web.sh [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --check       Prueba en modo no interactivo que el servidor HTTP responde 200"
    echo "                en /export/gdevelop/index.html y /export/gdevelop/game_data.json"
    echo "  --port N      Define el puerto del servidor HTTP (por defecto: ${PORT})"
    echo "  -h, --help    Muestra esta ayuda"
}

MODO="normal"
PORT_EXPLICITO=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check)
            MODO="check"
            shift
            ;;
        --port)
            if [[ $# -lt 2 ]]; then
                echo "✘ Error: --port requiere un número de puerto." >&2
                exit 1
            fi
            PORT="$2"
            PORT_EXPLICITO=1
            shift 2
            ;;
        -h|--help)
            mostrar_ayuda
            exit 0
            ;;
        *)
            echo "✘ Opción desconocida: $1" >&2
            mostrar_ayuda
            exit 1
            ;;
    esac
done

mostrar_banner

# Verificar que existan los artefactos web; si falta game_data.json, ejecutar exportar_todo.py
if [[ ! -f "$SCRIPT_DIR/$WEB_JSON" ]]; then
    echo "⚠ No se encontró '$WEB_JSON'. Ejecutando tools/exportar_todo.py..."
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$PYTHON_BIN" "$SCRIPT_DIR/tools/exportar_todo.py"
fi

if [[ ! -f "$SCRIPT_DIR/$WEB_HTML" ]]; then
    echo "⚠ No se encontró '$WEB_HTML'. Ejecutando tools/exportar_todo.py por si requiere sincronización..."
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$PYTHON_BIN" "$SCRIPT_DIR/tools/exportar_todo.py" || true
fi

if [[ ! -f "$SCRIPT_DIR/$WEB_HTML" ]]; then
    echo "✘ Error: Falta '$WEB_HTML' en el repositorio." >&2
    exit 1
fi

if [[ ! -f "$SCRIPT_DIR/$WEB_JSON" ]]; then
    echo "✘ Error: Falta '$WEB_JSON' incluso tras ejecutar tools/exportar_todo.py." >&2
    exit 1
fi

if [[ "$MODO" == "check" ]]; then
    # Elegir un puerto libre automáticamente si no se forzó uno explícito
    if [[ "$PORT_EXPLICITO" -eq 0 ]]; then
        CHECK_PORT="$("$PYTHON_BIN" -c '
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("127.0.0.1", 0))
    print(s.getsockname()[1])
')"
    else
        CHECK_PORT="$PORT"
    fi

    echo "▶ Iniciando servidor HTTP temporal en 127.0.0.1:${CHECK_PORT} (--check)..."
    "$PYTHON_BIN" -m http.server "$CHECK_PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
    SERVER_PID=$!

    cleanup_check() {
        if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
            kill "$SERVER_PID" 2>/dev/null || true
            wait "$SERVER_PID" 2>/dev/null || true
        fi
    }
    trap cleanup_check EXIT INT TERM

    "$PYTHON_BIN" - "$CHECK_PORT" "$WEB_HTML" "$WEB_JSON" <<'PYEOF'
import sys
import time
import urllib.request

port = sys.argv[1]
paths = [sys.argv[2], sys.argv[3]]
base_url = f"http://127.0.0.1:{port}"

# Esperar a que el servidor acepte conexiones
ready = False
for _ in range(30):
    try:
        with urllib.request.urlopen(f"{base_url}/{paths[0]}", timeout=1) as resp:
            if resp.status == 200:
                ready = True
                break
    except Exception:
        time.sleep(0.1)

if not ready:
    print(f"✘ Error: El servidor HTTP en {base_url} no respondió a tiempo.", file=sys.stderr)
    sys.exit(1)

for rel_path in paths:
    url = f"{base_url}/{rel_path}"
    with urllib.request.urlopen(url, timeout=3) as resp:
        body = resp.read()
        if resp.status != 200 or len(body) == 0:
            print(f"✘ Error: {url} devolvió HTTP {resp.status} ({len(body)} bytes).", file=sys.stderr)
            sys.exit(1)
        print(f"  ✔ HTTP {resp.status} OK -> /{rel_path} ({len(body)} bytes)")

print("✔ Verificación Web (--check) completada exitosamente.")
PYEOF
    exit 0
fi

URL="http://localhost:${PORT}/${WEB_HTML}"
echo "▶ Servidor Web listo en: $URL"
echo "  Presiona Ctrl+C en esta terminal para detener el servidor limpiamente."
echo ""

SERVER_PID=""
cleanup_server() {
    echo ""
    echo "▶ Deteniendo servidor HTTP (puerto ${PORT})..."
    if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    echo "✔ Servidor detenido limpiamente."
    exit 0
}
trap cleanup_server INT TERM

"$PYTHON_BIN" -m http.server "$PORT" &
SERVER_PID=$!

# Esperar brevemente y abrir navegador si hay entorno gráfico disponible
sleep 0.4
if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] && command -v xdg-open >/dev/null 2>&1; then
    echo "▶ Abriendo navegador con xdg-open: $URL"
    xdg-open "$URL" >/dev/null 2>&1 || true
else
    echo "ℹ Entorno sin sesión gráfica o sin xdg-open; abre manualmente: $URL"
fi

wait "$SERVER_PID"
