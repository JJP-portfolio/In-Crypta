# ============================================================
# generar_proyecto_rediseñado.py — IN CRYPTA room tests para GDevelop
# ============================================================
# Genera un proyecto GDevelop nativo usando los NIVELES REDESEÑADOS
# (room tests v2) en lugar de los niveles de campaña originales.
# ============================================================

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import pygame  # noqa: E402

from generar_proyecto_nativo import (  # noqa: E402
    OUT,
    PROJECT_NAME,
    construir_proyecto,
    generar_assets,
    accion,
    evento,
)

PROJECT_NAME_RED = "IN_CRYPTA_ROOM_TESTS_NATIVO.json"
from config import TILE  # noqa: E402
from nivel import Nivel  # noqa: E402
from niveles_redisenados import NIVELES_RED  # noqa: E402


def camara_seguir_jugador() -> list[dict]:
    """Evento que centra la cámara en el jugador cada frame."""
    return [
        evento(
            [],  # sin condiciones = siempre
            [
                accion("SetCameraCenterX", ["", "=", "Jugador.X()", "", "0"]),
                accion("SetCameraCenterY", ["", "=", "Jugador.Y()", "", "0"]),
                accion("SetCameraCenterX", ["", "=", "Jugador.X()", '"UI"', "0"]),
                accion("SetCameraCenterY", ["", "=", "Jugador.Y()", '"UI"', "0"]),
            ],
        ),
    ]


def main() -> int:
    pygame.init()
    OUT.mkdir(parents=True, exist_ok=True)

    niveles = [
        Nivel(d["mapa"], d["nombre"], d["pista"], d["tema"])
        for d in NIVELES_RED
    ]

    generar_assets(niveles)
    proyecto = construir_proyecto(niveles)

    # Renombrar escenas de niveles para diferenciar del proyecto original
    nivel_idx = 0
    for layout in proyecto["layouts"]:
        if layout["name"].startswith("Nivel "):
            nivel_idx += 1
            layout["name"] = f"Room Test {nivel_idx} - {NIVELES_RED[nivel_idx-1]['nombre'].replace(' (Room Test)', '')}"

    # --- CORRECCIÓN: mover definiciones de objetos a base["objects"] ---
    objetos_vistos = {}
    for layout in proyecto["layouts"]:
        for obj in layout.get("objects", []):
            nombre = obj.get("name")
            if nombre and nombre not in objetos_vistos:
                objetos_vistos[nombre] = obj
        layout["objects"] = []  # limpiar: las definiciones van en base["objects"]
    proyecto["objects"] = list(objetos_vistos.values())

    # --- CORRECCIÓN: agregar cámara de seguimiento a cada nivel ---
    for layout in proyecto["layouts"]:
        if layout["name"].startswith("Room Test "):
            layout["events"].extend(camara_seguir_jugador())

    destino = OUT / PROJECT_NAME_RED
    destino.write_text(json.dumps(proyecto, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Proyecto: {destino}")
    print(f"Escenas: {[l['name'] for l in proyecto['layouts']]}")
    print(
        "Datos: "
        + ", ".join(
            f"{n.nombre} {n.ancho}x{n.alto} ({len(n.solidos)} sólidos, "
            f"{len(n.almas)} almas, {len(n.enemigos)} enemigos, "
            f"{len(n.peligros)} peligros, {len(n.plataformas)} móviles)"
            for n in niveles
        )
    )
    print(f"Recursos: {len(proyecto['resources']['resources'])}")
    print("\nAbre IN_CRYPTA_ROOM_TESTS_NATIVO.json en GDevelop 5 para playtestear.")
    print("Controles: flechas mover, Shift dash, Up saltar, A atacar, Esc pausa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
