#!/usr/bin/env bash
# ============================================================================
# jugar_pygame.sh — Lanzador nativo Linux para IN CRYPTA (Desktop / Pygame-CE)
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Asegurar que los módulos de la raíz tengan prioridad sobre cualquier .pth
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

mostrar_banner() {
    echo "========================================================"
    echo "  IN CRYPTA 1.0.0 - Versión Desktop (Python / Pygame)"
    echo "========================================================"
    echo "  Directorio : $SCRIPT_DIR"
    echo "  Intérprete : $PYTHON_BIN"
    echo "========================================================"
}

mostrar_ayuda() {
    mostrar_banner
    echo ""
    echo "Uso: ./jugar_pygame.sh [opciones] [-- argumentos_main.py]"
    echo ""
    echo "Opciones:"
    echo "  --check       Verifica imports (pygame, main, Juego) en modo dummy y sale con 0"
    echo "  --headless    Ejecuta una prueba rápida sin ventana (SDL dummy) y sale con 0"
    echo "  --nivel N     Inicia directamente en el nivel N (1..3)"
    echo "  -h, --help    Muestra esta ayuda"
}

MODO="normal"
ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check)
            MODO="check"
            shift
            ;;
        --headless)
            MODO="headless"
            shift
            ;;
        -h|--help)
            mostrar_ayuda
            exit 0
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

mostrar_banner

if [[ "$MODO" == "check" || "$MODO" == "headless" ]]; then
    echo "▶ Ejecutando verificación en modo ${MODO} (SDL dummy)..."
    export SDL_VIDEODRIVER=dummy
    export SDL_AUDIODRIVER=dummy
    "$PYTHON_BIN" -c "
import os
import pygame
import main
from juego import Juego

juego = Juego()
juego.seleccionar_nivel(0)
juego.actualizar(1.0 / 60.0)
juego.dibujar()
pygame.quit()
print('✔ Verificación Pygame (${MODO}): imports, inicialización de Juego, update y draw OK.')
"
    exit 0
fi

echo "▶ Iniciando IN CRYPTA..."
exec "$PYTHON_BIN" "$SCRIPT_DIR/main.py" "${ARGS[@]}"
