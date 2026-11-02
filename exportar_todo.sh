#!/usr/bin/env bash
# ============================================================================
# exportar_todo.sh — Pipeline Maestro de Exportación, Paridad y Certificación
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"
export SDL_VIDEODRIVER=dummy
export SDL_AUDIODRIVER=dummy

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
    echo "  IN CRYPTA 1.0.0 - Pipeline de Exportación y QA"
    echo "========================================================"
    echo "  Directorio : $SCRIPT_DIR"
    echo "  Intérprete : $PYTHON_BIN"
    echo "  Modo SDL   : headless (dummy)"
    echo "========================================================"
}

mostrar_ayuda() {
    mostrar_banner
    echo ""
    echo "Uso: ./exportar_todo.sh [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --check       Ejecuta exportar_todo.py en modo validación (--check) junto con"
    echo "                validar_eventos_gd.py, verificar_paridad.py y la suite de tests"
    echo "  -h, --help    Muestra esta ayuda"
}

EXPORT_ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --check)
            EXPORT_ARGS+=("--check")
            shift
            ;;
        -h|--help)
            mostrar_ayuda
            exit 0
            ;;
        *)
            EXPORT_ARGS+=("$1")
            shift
            ;;
    esac
done

mostrar_banner

echo ""
echo "▶ [1/4] Ejecutando tools/exportar_todo.py ${EXPORT_ARGS[*]:-}..."
"$PYTHON_BIN" "$SCRIPT_DIR/tools/exportar_todo.py" "${EXPORT_ARGS[@]}"

echo ""
echo "▶ [2/4] Validando eventos GDevelop 5.6 contra el núcleo real (tools/validar_eventos_gd.py)..."
"$PYTHON_BIN" "$SCRIPT_DIR/tools/validar_eventos_gd.py"

echo ""
echo "▶ [3/4] Verificando paridad Pygame ↔ GDevelop (tools/verificar_paridad.py)..."
"$PYTHON_BIN" "$SCRIPT_DIR/tools/verificar_paridad.py"

echo ""
echo "▶ [4/4] Ejecutando suites de tests en modo headless..."
if "$PYTHON_BIN" -c "import pytest" >/dev/null 2>&1; then
    "$PYTHON_BIN" -m pytest "$SCRIPT_DIR/tests" -q
fi
"$PYTHON_BIN" "$SCRIPT_DIR/tests/test_logica.py"
"$PYTHON_BIN" "$SCRIPT_DIR/tests/test_hud.py"

if command -v node >/dev/null 2>&1 && [[ -f "$SCRIPT_DIR/tests/test_fisica_gdjs.js" ]]; then
    echo ""
    echo "▶ [Extra] Ejecutando pruebas de física GDJS en Node.js (tests/test_fisica_gdjs.js)..."
    node "$SCRIPT_DIR/tests/test_fisica_gdjs.js"
fi

echo ""
echo "========================================================"
echo "  ✔ PIPELINE DE EXPORTACIÓN Y CERTIFICACIÓN COMPLETADO"
echo "========================================================"
