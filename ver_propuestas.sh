#!/usr/bin/env bash
# ============================================================================
# ver_propuestas.sh — Visor de Documentación Interactiva y Laboratorio Visual
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Autodetección del intérprete Python (.venv prioritario)
if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v python)"
else
    PYTHON_BIN=""
fi

DOC_EXPLICACION="docs/explicacion_proyecto_in_crypta.html"
DOC_PROPUESTAS="docs/propuestas_visuales.html"
PORT="${PORT:-8080}"

mostrar_banner() {
    echo "========================================================"
    echo "  IN CRYPTA 1.0.0 - Documentación y Laboratorio Visual"
    echo "========================================================"
    echo "  1) Explicación integral : $DOC_EXPLICACION"
    echo "  2) Laboratorio visual   : $DOC_PROPUESTAS"
    echo "========================================================"
}

mostrar_ayuda() {
    mostrar_banner
    echo ""
    echo "Uso: [PORT=8080] ./ver_propuestas.sh [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --check         Valida la existencia y contenido de ambos archivos HTML"
    echo "  --serve         Sirve los documentos por HTTP en http://localhost:${PORT}/"
    echo "  --explicacion   Abre únicamente docs/explicacion_proyecto_in_crypta.html"
    echo "  --propuestas    Abre únicamente docs/propuestas_visuales.html"
    echo "  --port N        Define el puerto cuando se usa --serve (por defecto: ${PORT})"
    echo "  -h, --help      Muestra esta ayuda"
}

MODO="open"
TARGET="ambos"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check)
            MODO="check"
            shift
            ;;
        --serve)
            MODO="serve"
            shift
            ;;
        --explicacion)
            TARGET="explicacion"
            shift
            ;;
        --propuestas)
            TARGET="propuestas"
            shift
            ;;
        --port)
            if [[ $# -lt 2 ]]; then
                echo "✘ Error: --port requiere un número de puerto." >&2
                exit 1
            fi
            PORT="$2"
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

validar_archivos() {
    local fallos=0
    for doc in "$DOC_EXPLICACION" "$DOC_PROPUESTAS"; do
        if [[ -s "$SCRIPT_DIR/$doc" ]]; then
            local bytes
            bytes="$(wc -c < "$SCRIPT_DIR/$doc")"
            echo "  ✔ Encontrado: $doc (${bytes} bytes)"
        else
            echo "  ✘ Faltante o vacío: $doc" >&2
            fallos=$((fallos + 1))
        fi
    done
    return "$fallos"
}

if [[ "$MODO" == "check" ]]; then
    echo "▶ Verificando páginas HTML de documentación y propuestas..."
    if validar_archivos; then
        echo "✔ Verificación de documentos (--check) completada exitosamente."
        exit 0
    else
        echo "✘ Error: Faltan uno o más archivos HTML requeridos en docs/." >&2
        exit 1
    fi
fi

# Construir lista de documentos a abrir
DOCS_A_ABRIR=()
if [[ "$TARGET" == "ambos" || "$TARGET" == "explicacion" ]]; then
    if [[ -f "$SCRIPT_DIR/$DOC_EXPLICACION" ]]; then
        DOCS_A_ABRIR+=("$DOC_EXPLICACION")
    else
        echo "⚠ Aviso: No se encontró '$DOC_EXPLICACION'." >&2
    fi
fi
if [[ "$TARGET" == "ambos" || "$TARGET" == "propuestas" ]]; then
    if [[ -f "$SCRIPT_DIR/$DOC_PROPUESTAS" ]]; then
        DOCS_A_ABRIR+=("$DOC_PROPUESTAS")
    else
        echo "⚠ Aviso: No se encontró '$DOC_PROPUESTAS'." >&2
    fi
fi

if [[ ${#DOCS_A_ABRIR[@]} -eq 0 ]]; then
    echo "✘ Error: Ninguno de los documentos HTML solicitados está disponible." >&2
    exit 1
fi

if [[ "$MODO" == "serve" ]]; then
    if [[ -z "$PYTHON_BIN" ]]; then
        echo "✘ Error: Se requiere Python para servir los documentos con --serve." >&2
        exit 1
    fi
    echo "▶ Sirviendo documentación por HTTP en puerto ${PORT}..."
    for doc in "${DOCS_A_ABRIR[@]}"; do
        echo "  • http://localhost:${PORT}/${doc}"
    done
    echo "  Presiona Ctrl+C para detener el servidor."

    SERVER_PID=""
    cleanup_serve() {
        echo ""
        echo "▶ Deteniendo servidor de documentación..."
        if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
            kill "$SERVER_PID" 2>/dev/null || true
            wait "$SERVER_PID" 2>/dev/null || true
        fi
        echo "✔ Servidor detenido limpiamente."
        exit 0
    }
    trap cleanup_serve INT TERM

    "$PYTHON_BIN" -m http.server "$PORT" &
    SERVER_PID=$!
    sleep 0.4

    if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] && command -v xdg-open >/dev/null 2>&1; then
        for doc in "${DOCS_A_ABRIR[@]}"; do
            xdg-open "http://localhost:${PORT}/${doc}" >/dev/null 2>&1 || true
        done
    fi

    wait "$SERVER_PID"
    exit 0
fi

# Modo apertura directa con xdg-open
for doc in "${DOCS_A_ABRIR[@]}"; do
    full_path="$SCRIPT_DIR/$doc"
    echo "▶ Documento disponible: file://${full_path}"
    if [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" ]] && command -v xdg-open >/dev/null 2>&1; then
        echo "  Abriendo en navegador con xdg-open..."
        xdg-open "$full_path" >/dev/null 2>&1 || true
    else
        echo "  ℹ Sin entorno gráfico activo. Usa './ver_propuestas.sh --serve' o abre la ruta en tu navegador."
    fi
done
