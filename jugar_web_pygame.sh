#!/usr/bin/env bash
# ============================================================================
# jugar_web_pygame.sh — Servidor de prueba WebAssembly (Pygame-CE + Pygbag)
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
else
    PYTHON_BIN="python"
fi

PORT="${PORT:-8000}"
WEB_DIR="$SCRIPT_DIR/export/web_pygame/build/web"

mostrar_banner() {
    echo "========================================================"
    echo "  IN CRYPTA 1.0.0 - WebAssembly Runtime (Pygame / Pygbag)"
    echo "========================================================"
    echo "  Directorio Web : $WEB_DIR"
    echo "  Intérprete     : $PYTHON_BIN"
    echo "  Puerto HTTP    : $PORT"
    echo "========================================================"
}

if [[ "${1:-}" == "--check" ]]; then
    mostrar_banner
    echo "▶ Verificando artefactos WebAssembly..."
    if [[ ! -f "$WEB_DIR/index.html" || ! -f "$WEB_DIR/web_pygame.apk" ]]; then
        echo "⚠ No se encontraron artefactos compilados. Ejecutando tools/exportar_web_pygame.py..."
        "$PYTHON_BIN" "$SCRIPT_DIR/tools/exportar_web_pygame.py" --build
    fi

    # Verificar existencia de archivos obligatorios
    for f in "$WEB_DIR/index.html" "$WEB_DIR/web_pygame.apk" "$WEB_DIR/.nojekyll"; do
        if [[ ! -f "$f" ]]; then
            echo "✘ Error: Falta archivo requerido: $f" >&2
            exit 1
        fi
        echo "  ✔ $(basename "$f") presente ($(wc -c < "$f") bytes)"
    done
    echo "✔ Verificación WebAssembly (--check) completada exitosamente."
    exit 0
fi

if [[ ! -f "$WEB_DIR/index.html" || ! -f "$WEB_DIR/web_pygame.apk" ]]; then
    echo "⚠ Compilando paquete Pygbag antes de iniciar el servidor..."
    "$PYTHON_BIN" "$SCRIPT_DIR/tools/exportar_web_pygame.py" --build
fi

mostrar_banner
URL="http://localhost:${PORT}/index.html"
echo "▶ Servidor WebAssembly listo en: $URL"
echo "  Presiona Ctrl+C para detener el servidor."
echo ""

cd "$WEB_DIR"
exec "$PYTHON_BIN" -m http.server "$PORT"
