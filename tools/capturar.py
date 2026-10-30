# ============================================================
# tools/capturar.py — Capturas headless del título y los tres niveles
# ============================================================
# Uso:
#   PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
#     .venv/bin/python tools/capturar.py
# ============================================================

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import pygame

pygame.init()

from juego import Juego


def main():
    destino = RAIZ / "capturas"
    destino.mkdir(exist_ok=True)

    juego_titulo = Juego()
    for _ in range(30):
        juego_titulo.actualizar(1 / 60)
    juego_titulo.dibujar()
    ruta_titulo = destino / "titulo.png"
    pygame.image.save(juego_titulo.pantalla, str(ruta_titulo))
    print(f"CAPTURA_OK {ruta_titulo}")

    for indice in range(3):
        juego = Juego()
        juego.cargar_nivel(indice, vidas=3)
        for _ in range(30):
            juego.actualizar(1 / 60)
        juego.dibujar()
        ruta = destino / f"nivel_{indice + 1}.png"
        pygame.image.save(juego.pantalla, str(ruta))
        print(f"CAPTURA_OK {ruta}")

    pygame.quit()


if __name__ == "__main__":
    main()
