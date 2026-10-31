#!/usr/bin/env python3
# ============================================================
# verificar_paridad.py — ¿el export es el mismo juego?
# ============================================================
# Compara el proyecto GDevelop exportado contra el modelo real
# del juego Pygame (los objetos que crea nivel.py). Sirve como
# criterio de aceptación del exportador: si algo difiere, el
# export NO es el mismo juego y hay que reportarlo.
#
# Uso:
#   python tools/verificar_paridad.py [--proyecto RUTA]
# ============================================================

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from nivel import Nivel  # noqa: E402
from niveles import NIVELES, SALAS_PRUEBA  # noqa: E402

pygame.init()

PROYECTO_DEFAULT = ROOT / "export" / "gdevelop_nativo" / "IN_CRYPTA_NATIVO.json"
TILE = 32


# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------
def inst_por_nombre(escena: dict) -> dict[str, list[dict]]:
    """Agrupa las instancias de la escena por nombre de objeto."""
    salida: dict[str, list[dict]] = {}
    for inst in escena.get("instances", []):
        salida.setdefault(inst["name"], []).append(inst)
    return salida


def rect(inst: dict) -> tuple[int, int, int, int]:
    return (inst["x"], inst["y"], inst["width"], inst["height"])


def eventos_de(escena: dict) -> str:
    """Todo el árbol de eventos serializado (para buscar reglas)."""
    return json.dumps(escena.get("events", []), ensure_ascii=False)


def texto_textura(proyecto: dict, escena: dict, nombre_objeto: str) -> tuple[str, tuple[int, int]] | None:
    """Devuelve (archivo, tamaño real de la textura) del objeto."""
    recursos = {
        r["name"]: r["file"]
        for r in proyecto.get("resources", {}).get("resources", [])
        if r.get("kind") == "image"
    }
    for obj in escena.get("objects", []):
        if obj["name"] != nombre_objeto:
            continue
        animaciones = obj.get("animations") or []
        if not animaciones:
            return None
        sprites = animaciones[0]["directions"][0]["sprites"]
        if not sprites:
            return None
        archivo = recursos.get(sprites[0]["image"])
        if not archivo:
            return None
        ruta = ROOT / "export" / "gdevelop_nativo" / archivo
        if not ruta.exists():
            return None
        superficie = pygame.image.load(str(ruta))
        return archivo, (superficie.get_width(), superficie.get_height())
    return None


# ------------------------------------------------------------
# Escenas del juego que deben existir en el export
# ------------------------------------------------------------
def escenas_del_juego() -> list[tuple[str, Nivel]]:
    escenas: list[tuple[str, Nivel]] = []
    for indice, datos in enumerate(NIVELES, start=1):
        escenas.append(
            (
                f"Nivel {indice}",
                Nivel(datos["mapa"], datos["nombre"], datos["pista"], datos["tema"]),
            )
        )
    for numero, sala in enumerate(SALAS_PRUEBA[:3], start=1):
        escenas.append(
            (
                f"Sala {numero}",
                Nivel(sala["mapa"], sala["nombre"], sala["pista"], sala["tema"]),
            )
        )
    return escenas


# ------------------------------------------------------------
# Comparaciones
# ------------------------------------------------------------
class Informe:
    def __init__(self) -> None:
        self.lineas: list[str] = []
        self.problemas = 0

    def ok(self, texto: str) -> None:
        self.lineas.append(f"  OK    {texto}")

    def mal(self, texto: str) -> None:
        self.problemas += 1
        self.lineas.append(f"  FALLA {texto}")

    def info(self, texto: str) -> None:
        self.lineas.append(f"  --    {texto}")


def comparar_solidos(informe: Informe, nombre: str, nivel: Nivel, escena: dict) -> None:
    grilla: dict[int, set[int]] = {}
    for inst in escena.get("instances", []):
        if inst["name"] != "Solido":
            continue
        for fila in range(inst["y"] // TILE, (inst["y"] + inst["height"]) // TILE):
            for col in range(inst["x"] // TILE, (inst["x"] + inst["width"]) // TILE):
                grilla.setdefault(fila, set()).add(col)
    diferencias = 0
    for fila, texto in enumerate(nivel.filas):
        for col, simbolo in enumerate(texto):
            esperado = simbolo == "#"
            real = col in grilla.get(fila, set())
            if esperado != real:
                diferencias += 1
    if diferencias:
        informe.mal(f"{nombre}: {diferencias} tiles de colisión difieren del mapa")
    else:
        informe.ok(f"{nombre}: colisiones idénticas al mapa ({len(nivel.solidos)} bloques)")


def comparar_conjuntos(
    informe: Informe,
    nombre: str,
    etiqueta: str,
    exportados: list[dict],
    esperados: list[tuple[int, int, int, int]],
    *,
    comparar_rect: bool = True,
) -> None:
    if len(exportados) != len(esperados):
        informe.mal(
            f"{nombre}: {etiqueta}: el export tiene {len(exportados)}, "
            f"el juego tiene {len(esperados)}"
        )
        return
    if not comparar_rect:
        informe.ok(f"{nombre}: {etiqueta}: {len(esperados)} en las mismas posiciones")
        return
    for inst, esperado in zip(exportados, esperados):
        if rect(inst) != esperado:
            informe.mal(
                f"{nombre}: {etiqueta}: en el export {rect(inst)} vs juego {esperado}"
            )
            return
    informe.ok(f"{nombre}: {etiqueta}: {len(esperados)} con posición y tamaño exactos")


def comparar_escena(informe: Informe, proyecto: dict, nombre: str, nivel: Nivel) -> None:
    escenas = {e["name"]: e for e in proyecto.get("layouts", [])}
    if nombre not in escenas:
        informe.mal(f"{nombre}: la escena no existe en el export")
        return
    escena = escenas[nombre]
    instancias = inst_por_nombre(escena)

    comparar_solidos(informe, nombre, nivel, escena)

    # Jugador: el juego lo crea en (spawn[0], spawn[1]).
    jugadores = instancias.get("Jugador", [])
    if len(jugadores) != 1:
        informe.mal(f"{nombre}: hay {len(jugadores)} jugadores (se espera 1)")
    else:
        esperado = (nivel.spawn[0], nivel.spawn[1], 32, 32)
        if rect(jugadores[0]) != esperado:
            informe.mal(
                f"{nombre}: jugador en {rect(jugadores[0])}, el juego lo pone en {esperado}"
            )
        else:
            informe.ok(f"{nombre}: jugador en la posición exacta del spawn")

    # Portón.
    puertas = instancias.get("Puerta", [])
    meta = nivel.meta
    esperado_meta = (meta.centerx - 21, meta.bottom - 58, 42, 58)
    if len(puertas) != 1:
        informe.mal(f"{nombre}: hay {len(puertas)} portones (se espera 1)")
    elif rect(puertas[0]) != esperado_meta:
        informe.mal(
            f"{nombre}: portón en {rect(puertas[0])}, el juego lo dibuja en {esperado_meta}"
        )
    else:
        informe.ok(f"{nombre}: portón en la posición exacta")

    # Almas.
    esperado_almas = [
        (a.rect.centerx - 12, a.rect.centery - 12, 24, 24) for a in nivel.almas
    ]
    comparar_conjuntos(
        informe, nombre, "almas", instancias.get("Alma", []), esperado_almas
    )

    # Pinchos.
    esperado_peligros = [(p.x, p.y, p.width, p.height) for p in nivel.peligros]
    comparar_conjuntos(
        informe, nombre, "pinchos", instancias.get("Pinchos", []), esperado_peligros
    )

    # Palas recogibles.
    esperado_palas = [(p.rect.x, p.rect.y, p.rect.width, p.rect.height) for p in nivel.palas]
    comparar_conjuntos(
        informe, nombre, "palas", instancias.get("PalaRecogible", []), esperado_palas
    )

    # Plataformas móviles: rectángulo + movimiento.
    plataformas = [
        inst
        for nombre_obj, lista in instancias.items()
        if nombre_obj.startswith("PlataformaMovil")
        for inst in lista
    ]
    esperado_plataformas = [
        (p.rect.x, p.rect.y, p.rect.width, p.rect.height) for p in nivel.plataformas
    ]
    comparar_conjuntos(
        informe,
        nombre,
        "plataformas",
        plataformas,
        esperado_plataformas,
        comparar_rect=False,
    )
    for inst, plataforma in zip(plataformas, nivel.plataformas):
        variables = {v["name"]: v["value"] for v in inst.get("initialVariables", [])}
        esperado_variables = {
            "origen_x": plataforma.inicial_rect.x,
            "origen_y": plataforma.inicial_rect.y,
            "amplitud": plataforma.amplitud,
            "velocidad": plataforma.velocidad,
            "fase": round(plataforma.fase, 4),
            "eje": 1 if plataforma.eje == "h" else 0,
        }
        for clave, valor in esperado_variables.items():
            if abs(float(variables.get(clave, 999999)) - float(valor)) > 0.01:
                informe.mal(
                    f"{nombre}: plataforma {clave}={variables.get(clave)} "
                    f"vs juego {valor}"
                )
    texto_eventos = eventos_de(escena)
    mueve = "PlataformaMovil" in texto_eventos and '"SetXY"' in texto_eventos
    if nivel.plataformas and not mueve:
        informe.mal(f"{nombre}: las plataformas no tienen regla de movimiento en los eventos")
    elif nivel.plataformas:
        informe.ok(f"{nombre}: las plataformas tienen regla de movimiento")

    # Enemigos.
    esperado_enemigos = [
        (e.rect.x, e.rect.y, e.rect.width, e.rect.height) for e in nivel.enemigos
    ]
    comparar_conjuntos(
        informe, nombre, "enemigos", instancias.get("Enemy", []), esperado_enemigos
    )
    for inst, enemigo in zip(instancias.get("Enemy", []), nivel.enemigos):
        variables = {v["name"]: v["value"] for v in inst.get("initialVariables", [])}
        if abs(float(variables.get("min_x", -1)) - enemigo.minimo_x) > 0.01:
            informe.mal(f"{nombre}: enemigo min_x={variables.get('min_x')} vs {enemigo.minimo_x}")
        if abs(float(variables.get("max_x", -1)) - enemigo.maximo_x) > 0.01:
            informe.mal(f"{nombre}: enemigo max_x={variables.get('max_x')} vs {enemigo.maximo_x}")

    # Jefe.
    esperado_jefes = [(j.rect.x, j.rect.y, j.rect.width, j.rect.height) for j in nivel.jefes]
    comparar_conjuntos(informe, nombre, "jefes", instancias.get("Jefe", []), esperado_jefes)

    # Entidades que el juego tiene y el export no.
    faltantes = {
        "enemigos melee (L)": (len(nivel.enemigos_melee), "EnemyMelee"),
        "tótems (O)": (len(nivel.totems), "Totem"),
        "cuervos (C)": (len(nivel.cuervos), "Cuervo"),
        "polillas (m)": (len(nivel.polillas), "Polilla"),
        "arañas (A)": (len(nivel.aranias), "Arana"),
        "power-ups de rango (X)": (len(nivel.power_ups_rango), "PowerUpRango"),
    }
    for etiqueta, (cantidad, objeto) in faltantes.items():
        if cantidad == 0:
            continue
        if objeto in instancias:
            informe.ok(f"{nombre}: {etiqueta}: {cantidad} exportadas")
        else:
            informe.mal(f"{nombre}: {etiqueta}: el juego tiene {cantidad} y el export ninguna")

    # Proporción de la textura vs caja de la instancia (evita sprites aplastados).
    for objeto in ("Jugador", "Enemy", "Alma", "Pinchos", "PlataformaMovil", "Puerta", "Jefe"):
        lista = instancias.get(objeto)
        if not lista:
            continue
        info_textura = texto_textura(proyecto, escena, objeto)
        if info_textura is None:
            continue
        _, (ancho_tex, alto_tex) = info_textura
        inst = lista[0]
        if alto_tex == 0:
            continue
        proporcion_tex = ancho_tex / alto_tex
        proporcion_inst = inst["width"] / inst["height"] if inst["height"] else 0
        if abs(proporcion_tex - proporcion_inst) > 0.02:
            informe.mal(
                f"{nombre}: sprite {objeto} de {ancho_tex}x{alto_tex} "
                f"(proporción {proporcion_tex:.2f}) en caja {inst['width']}x{inst['height']} "
                f"(proporción {proporcion_inst:.2f}) → se deforma"
            )


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proyecto", type=Path, default=PROYECTO_DEFAULT)
    args = parser.parse_args()

    if not args.proyecto.exists():
        print(f"No existe el proyecto: {args.proyecto}")
        return 2

    proyecto = json.loads(args.proyecto.read_text(encoding="utf-8"))
    informe = Informe()
    print(f"Verificando paridad: {args.proyecto}")
    for nombre, nivel in escenas_del_juego():
        comparar_escena(informe, proyecto, nombre, nivel)

    print("\n".join(informe.lineas))
    print()
    if informe.problemas:
        print(f"PARIDAD_ROTA: {informe.problemas} diferencias con el juego pygame")
        return 1
    print("PARIDAD_OK: el export coincide con el modelo del juego pygame")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
