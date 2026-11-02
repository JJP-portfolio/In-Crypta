# ============================================================
# generar_proyecto_rediseñado.py — IN CRYPTA room tests para GDevelop
# ============================================================
# Genera un proyecto GDevelop nativo usando los NIVELES REDISEÑADOS
# (room tests v2) con assets aislados en assets_room_tests/.
# ============================================================

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import pygame  # noqa: E402

from exportador.gdevelop import accion, evento  # noqa: E402
from exportador.manifiesto import EscenaSpec  # noqa: E402
from exportador.modelo import leer_escena  # noqa: E402
from generar_proyecto_nativo import (  # noqa: E402
    OUT,
    construir_proyecto,
    generar_assets,
    limpiar_assets,
)
from niveles_rediseñados import NIVELES_RED  # noqa: E402

PROJECT_NAME_RED = "IN_CRYPTA_ROOM_TESTS_NATIVO.json"
ASSETS_ROOM_TESTS = OUT / "assets_room_tests"


def camara_seguir_jugador() -> list[dict]:
    """Evento que centra la cámara en el jugador cada frame (GD 5.6)."""
    return [
        evento(
            [],  # sin condiciones = siempre
            [
                accion("CameraCenterX", ["=", "Jugador.X()", '""', "0"]),
                accion("CameraCenterY", ["=", "Jugador.Y()", '""', "0"]),
                accion("CameraCenterX", ["=", "Jugador.X()", '"UI"', "0"]),
                accion("CameraCenterY", ["=", "Jugador.Y()", '"UI"', "0"]),
            ],
        ),
    ]


def main() -> int:
    pygame.init()
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS_ROOM_TESTS.mkdir(parents=True, exist_ok=True)

    specs = [
        EscenaSpec(
            clave=f"room_test_{idx + 1}",
            nombre=f"Room Test {idx + 1} - {d['nombre'].replace(' (Room Test)', '')}",
            mapa=d["mapa"],
            nombre_juego=d["nombre"],
            pista=d["pista"],
            tema=d.get("tema", "camposanto"),
            titulo=f"ROOM TEST {idx + 1} - {d['nombre'].upper()}",
            hud="ESPACIO: SALTO · SHIFT: DASH · A: PALA",
            hud_sin_pala="ESPACIO: SALTO · SHIFT: DASH",
            fondo=f"FondoRoomTest{idx + 1}",
            pala_inicial=True,
            es_sala=True,
        )
        for idx, d in enumerate(NIVELES_RED)
    ]
    escenas = [leer_escena(s) for s in specs]

    generar_assets(escenas, directorio_assets=ASSETS_ROOM_TESTS)
    proyecto = construir_proyecto(escenas, prefijo_recursos="assets_room_tests")
    limpiar_assets(proyecto, directorio_assets=ASSETS_ROOM_TESTS)

    # Definiciones de objetos en base["objects"]
    objetos_vistos = {}
    for layout in proyecto["layouts"]:
        for obj in layout.get("objects", []):
            nombre = obj.get("name")
            if nombre and nombre not in objetos_vistos:
                objetos_vistos[nombre] = obj
        layout["objects"] = []
    proyecto["objects"] = list(objetos_vistos.values())

    # Cámara de seguimiento a cada nivel
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
            f"{e.nombre} {e.ancho}x{e.alto} ({len(e.solidos)} sólidos, "
            f"{len(e.de_kind('alma'))} almas, {len(e.de_kind('enemigo'))} enemigos, "
            f"{len(e.de_kind('peligro'))} peligros, {len(e.de_kind('plataforma'))} móviles)"
            for e in escenas
        )
    )
    print(f"Recursos: {len(proyecto['resources']['resources'])}")
    print("\nAbre IN_CRYPTA_ROOM_TESTS_NATIVO.json en GDevelop 5 para playtestear.")
    print("Controles: flechas mover, Shift dash, Up saltar, A atacar, Esc pausa.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
