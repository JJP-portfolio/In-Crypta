#!/usr/bin/env bash
#---- Lanzador para Linux (Pygame-CE) ----#
set -u

# Resolver directorio real del script (soporta symlinks)
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || realpath "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Si se ejecuta por doble clic desde entorno gráfico sin terminal interactiva,
#    intentar re-lanzar dentro de un emulador de terminal para que el usuario
#    pueda ver la instalación de requerimientos y posibles errores.
if [ ! -t 1 ] && [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ] && [ -z "${IN_CRYPTA_TERMINAL_SPAWNED:-}" ]; then
    for term in x-terminal-emulator gnome-terminal konsole xfce4-terminal alacritty kitty xterm; do
        if command -v "$term" >/dev/null 2>&1; then
            export IN_CRYPTA_TERMINAL_SPAWNED=1
            case "$term" in
                gnome-terminal) exec gnome-terminal -- "$0" "$@" ;;
                konsole) exec konsole -e "$0" "$@" ;;
                *) exec "$term" -e "$0" "$@" ;;
            esac
        fi
    done
fi

export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"
LOG_FILE="$SCRIPT_DIR/in_crypta_launcher.log"

echo "========================================================"
echo "  IN CRYPTA 1.1.1 - Version Desktop (Linux)"
echo "========================================================"
echo "  Directorio : $SCRIPT_DIR"

# Manejo de opciones rápidas (--check / --headless / -h)
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
            echo "Uso: ./jugar_pygame.sh [opciones] [-- argumentos_main.py]"
            echo "  --check       Verifica imports y entorno"
            echo "  --headless    Ejecuta prueba en modo SDL dummy"
            echo "  --fullscreen  Inicia en pantalla completa"
            echo "  --nivel N     Inicia directamente en el nivel N (1..3)"
            exit 0
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# 2. Detección del intérprete Python del sistema
PYTHON_SYS=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_SYS="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON_SYS="$(command -v python)"
fi

if [[ -z "$PYTHON_SYS" && ! -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
    echo "[ERROR] No se encontro Python 3 instalado en el sistema." | tee -a "$LOG_FILE"
    echo "Instala Python 3 (ej: sudo apt install python3 python3-venv python3-pip)"
    if [ -t 0 ]; then read -p "Presiona ENTER para salir..." -r _; fi
    exit 1
fi

# 3. Creación/Verificación de entorno virtual (.venv)
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "[IN CRYPTA] Creando entorno virtual local en $VENV_DIR..."
    "$PYTHON_SYS" -m venv "$VENV_DIR" || {
        echo "[ERROR] Fallo la creacion de .venv. En Debian/Ubuntu instala: sudo apt install python3-venv" | tee -a "$LOG_FILE"
        if [ -t 0 ]; then read -p "Presiona ENTER para salir..." -r _; fi
        exit 1
    }
fi

# 4. Verificación obligatoria de motor gráfico (pygame-ce)
echo "[IN CRYPTA] Verificando motor grafico (pygame-ce)..."
if ! "$VENV_PYTHON" -c "import pygame; assert getattr(pygame, 'IS_CE', False)" >/dev/null 2>&1; then
    echo "[IN CRYPTA] Instalando / configurando pygame-ce..."
    "$VENV_PYTHON" -m pip uninstall -y pygame >/dev/null 2>&1 || true
    if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
        "$VENV_PYTHON" -m pip install -r "$SCRIPT_DIR/requirements.txt" --upgrade || {
            echo "[AVISO] pip install tuvo advertencias, asegurando pygame-ce..."
            "$VENV_PYTHON" -m pip install "pygame-ce>=2.5,<3" --upgrade
        }
    else
        "$VENV_PYTHON" -m pip install "pygame-ce>=2.5,<3" --upgrade
    fi
fi

echo "  Interprete : $VENV_PYTHON"
echo "========================================================"

# Modo headless / check
if [[ "$MODO" == "check" || "$MODO" == "headless" ]]; then
    echo "[IN CRYPTA] Ejecutando verificacion en modo ${MODO} (SDL dummy)..."
    export SDL_VIDEODRIVER=dummy
    export SDL_AUDIODRIVER=dummy
    "$VENV_PYTHON" -c "
import os
import pygame
import main
from juego import Juego

juego = Juego()
juego.seleccionar_nivel(0)
juego.actualizar(1.0 / 60.0)
juego.dibujar()
pygame.quit()
print('[OK] Verificacion Pygame (${MODO}): imports, Juego, update y draw correctos.')
"
    exit 0
fi

# 5. Ejecución del juego (priorizar Wayland nativo cuando esté activo)
export SDL_VIDEO_WAYLAND_WMCLASS="${SDL_VIDEO_WAYLAND_WMCLASS:-in-crypta}"
export SDL_VIDEO_X11_WMCLASS="${SDL_VIDEO_X11_WMCLASS:-in-crypta}"
if [[ -z "${SDL_VIDEODRIVER:-}" && -n "${WAYLAND_DISPLAY:-}" ]]; then
    if SDL_VIDEODRIVER=wayland "$VENV_PYTHON" -c "import pygame; pygame.display.init(); pygame.display.quit()" >/dev/null 2>&1; then
        export SDL_VIDEODRIVER=wayland
    fi
fi
echo "[IN CRYPTA] Iniciando juego..."
"$VENV_PYTHON" "$SCRIPT_DIR/main.py" "${ARGS[@]}"
RET=$?

if [[ $RET -ne 0 ]]; then
    echo "" | tee -a "$LOG_FILE"
    echo "[ERROR] El juego finalizo inesperadamente con codigo de salida $RET." | tee -a "$LOG_FILE"
    if [ -t 0 ]; then
        echo "Presiona [ENTER] para cerrar esta ventana..."
        read -r _
    fi
    exit $RET
fi
