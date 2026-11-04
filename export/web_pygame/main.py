# /// script
# dependencies = [
#   "pygame-ce",
# ]
# ///
# ============================================================
# main.py — Arranque del plataformero IN CRYPTA
# ============================================================
# Al ejecutar `python main.py` se inicia directamente la ventana de Pygame,
# comenzando por la pantalla de presentación gótica (Intro), la cual da paso
# al Menú Principal diegético con tres opciones:
#   1. JUGAR (Inicia la campaña desde el Nivel 1)
#   2. SELECCIÓN DE PANTALLA (Selector de los 3 niveles del juego)
#   3. CRÉDITOS (Reconocimientos y referencias de diseño)
# ============================================================
import asyncio
import os
import sys
import warnings
from pathlib import Path

# Suprimir avisos de librerías externas obsoletas
warnings.filterwarnings("ignore", category=UserWarning)

RAIZ = Path(__file__).resolve().parent
os.chdir(RAIZ)
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# Si existe el entorno virtual del proyecto con pygame-ce y numpy, preferirlo automáticamente
venv_python = RAIZ / ".venv" / "bin" / "python"
if venv_python.exists() and sys.executable != str(venv_python) and not os.environ.get("_IN_CRYPTA_VENV_ACTIVE"):
    os.environ["_IN_CRYPTA_VENV_ACTIVE"] = "1"
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)

import pygame

from juego import Juego


async def main():
    nivel_inicio = None
    iniciar_tut = False
    if len(sys.argv) >= 2 and sys.argv[1] in ("--tutorial", "-t"):
        iniciar_tut = True
    elif len(sys.argv) >= 3 and sys.argv[1] in ("--nivel", "-n"):
        try:
            val = int(sys.argv[2])
            if val == 0:
                iniciar_tut = True
            elif 1 <= val <= 3:
                nivel_inicio = val - 1
        except ValueError:
            pass

    juego = Juego()
    if iniciar_tut:
        juego.iniciar_tutorial()
    elif nivel_inicio is not None:
        juego.seleccionar_nivel(nivel_inicio)
    await juego.run_async()


if __name__ == "__main__":
    asyncio.run(main())
