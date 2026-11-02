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
import os
import sys
from pathlib import Path

# Asegurar que el directorio de trabajo y sys.path apunten siempre a la raíz del juego
RAIZ = Path(__file__).resolve().parent
os.chdir(RAIZ)
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from juego import Juego


def main():
    nivel_inicio = None
    if len(sys.argv) >= 3 and sys.argv[1] in ("--nivel", "-n"):
        try:
            val = int(sys.argv[2])
            if 1 <= val <= 3:
                nivel_inicio = val - 1
        except ValueError:
            pass

    juego = Juego()
    if nivel_inicio is not None:
        juego.seleccionar_nivel(nivel_inicio)
    juego.run()


if __name__ == "__main__":
    main()
