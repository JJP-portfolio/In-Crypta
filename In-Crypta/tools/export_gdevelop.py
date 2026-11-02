#!/usr/bin/env python3
"""Exporta IN CRYPTA a un JSON que consume el runtime de GDevelop."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import config
from nivel import Nivel
from niveles import NIVELES

FORMATO = "incrypta.gdevelop-levels"
VERSION = 1


def color_hex(color):
    return "#{:02x}{:02x}{:02x}".format(*color[:3])


def rect_dict(rect, sufijo, indice):
    return {
        "id": f"{sufijo}-{indice:03d}",
        "x": rect.x,
        "y": rect.y,
        "w": rect.width,
        "h": rect.height,
    }


def reglas():
    return {
        "vidas_iniciales": config.VIDAS_INICIALES,
        "gravedad": config.GRAVEDAD,
        "salto": config.SALTO,
        "velocidad": config.VELOCIDAD,
        "max_caida": config.MAX_CAIDA,
        "coyote_time": config.COYOTE_TIME,
        "jump_buffer": config.JUMP_BUFFER,
        "corte_salto": config.CORTE_SALTO,
        "invulnerabilidad": config.INVULNERABILIDAD,
        "rebote_enemigo": config.REBOTE_ENEMIGO,
        "velocidad_enemigo": config.VELOCIDAD_ENEMIGO,
        "dash_velocidad": config.DASH_VELOCIDAD,
        "dash_duracion": config.DASH_DURACION,
        "dash_cooldown": config.DASH_COOLDOWN,
        "dash_usos_aire": config.DASH_USOS_AIRE,
        "fps": config.FPS,
    }


def tamanos():
    return {
        "tile": config.TILE,
        "jugador": {"w": config.JUGADOR_ANCHO, "h": config.JUGADOR_ALTO},
        "enemigo": {"w": config.ENEMIGO_ANCHO, "h": config.ENEMIGO_ALTO},
        "alma": {"w": 16, "h": 16},
    }


def paleta():
    return {
        "fondo": color_hex((6, 8, 18)),
        "fondo_bajo": color_hex((22, 30, 42)),
        "jugador": color_hex(config.AZUL_OSCURO),
        "jugador_oscuro": color_hex(config.MARRON_OSCURO),
        "enemigo": color_hex(config.VERDE_OSCURO),
        "alma": color_hex(config.VIOLETA),
        "meta": color_hex(config.ORO),
        "piso": color_hex(config.MARRON),
        "plataforma": color_hex(config.PIEDRA),
        "pasto": color_hex(config.MUSGO),
        "dash": color_hex(config.TURQUESA),
        "acento": color_hex(config.SANGRE),
        "hueso": color_hex(config.HUESO),
        "niebla": color_hex(config.NIEBLA),
        "piedra_oscura": color_hex(config.PIEDRA_OSCURA),
    }


def diseno():
    return {
        "mechanics": ["salto de precisión", "dash de sombra", "golpe de pala"],
        "aesthetics": ["Desafío", "Sensación"],
        "dynamics": [
            "ritmo de salto-dash-pala",
            "riesgo/recompensa por almas sobre abismos",
            "morador como plataforma de rebote",
            "escape y maestría",
        ],
        "mda": {
            "mechanics": "Reglas de movimiento, dash y golpe descendente con la pala.",
            "dynamics": "El jugador encadena acciones y decide cuándo arriesgar.",
            "aesthetics": "Desafío por precisión; Sensación por oscuridad, velocidad, partículas y sonido.",
        },
        "references": list(config.REFERENCIAS),
    }


def exportar_nivel(indice, datos):
    nivel = Nivel(
        datos["mapa"],
        datos["nombre"],
        datos["pista"],
        datos.get("tema", "camposanto"),
    )
    prefijo = f"n{indice + 1}"

    solidos = [
        rect_dict(rect, f"{prefijo}-solido", i + 1)
        for i, rect in enumerate(nivel.solidos)
    ]
    almas = [
        rect_dict(alma.rect, f"{prefijo}-alma", i + 1)
        for i, alma in enumerate(nivel.almas)
    ]
    peligros = [
        rect_dict(peligro, f"{prefijo}-peligro", i + 1)
        for i, peligro in enumerate(nivel.peligros)
    ]
    decoraciones = []
    for i, decoracion in enumerate(nivel.decoraciones):
        item = rect_dict(decoracion["rect"], f"{prefijo}-decoracion", i + 1)
        item["type"] = decoracion["tipo"]
        decoraciones.append(item)
    enemigos = [
        {
            "id": f"{prefijo}-enemigo-{i + 1:03d}",
            "x": enemigo.rect.x,
            "y": enemigo.rect.y,
            "w": enemigo.rect.width,
            "h": enemigo.rect.height,
            "patrol_min_x": enemigo.minimo_x,
            "patrol_max_x": enemigo.maximo_x,
            "direction": enemigo.direccion,
            "speed": config.VELOCIDAD_ENEMIGO,
        }
        for i, enemigo in enumerate(nivel.enemigos)
    ]
    plataformas = [
        {
            "id": f"{prefijo}-plat-{i + 1:03d}",
            "x": plat.rect.x,
            "y": plat.rect.y,
            "w": plat.rect.width,
            "h": plat.rect.height,
            "origin_x": plat.inicial_rect.x,
            "origin_y": plat.inicial_rect.y,
            "axis": plat.eje,
            "amplitude": plat.amplitud,
            "speed": plat.velocidad,
            "phase": plat.fase,
        }
        for i, plat in enumerate(nivel.plataformas)
    ]
    palas = [
        rect_dict(p.rect, f"{prefijo}-pala", i + 1)
        for i, p in enumerate(nivel.palas)
    ]
    powerups = [
        rect_dict(p.rect, f"{prefijo}-powerup", i + 1)
        for i, p in enumerate(nivel.power_ups_rango)
    ]
    enemigos_melee = [
        {
            "id": f"{prefijo}-melee-{i + 1:03d}",
            "x": e.rect.x,
            "y": e.rect.y,
            "w": e.rect.width,
            "h": e.rect.height,
            "patrol_min_x": e.minimo_x,
            "patrol_max_x": e.maximo_x,
            "direction": e.direccion,
            "speed": getattr(e, "velocidad", config.VELOCIDAD_ENEMIGO),
        }
        for i, e in enumerate(nivel.enemigos_melee)
    ]
    jefes = [
        {
            "id": f"{prefijo}-jefe-{i + 1:03d}",
            "x": j.rect.x,
            "y": j.rect.y,
            "w": j.rect.width,
            "h": j.rect.height,
            "min_x": j.minimo_x,
            "max_x": j.maximo_x,
            "hp": j.vida,
            "fase": getattr(j, "fase", 1),
        }
        for i, j in enumerate(nivel.jefes)
    ]

    return {
        "index": indice + 1,
        "id": f"nivel-{indice + 1}",
        "name": datos["nombre"],
        "theme": datos.get("tema", "camposanto"),
        "hint": datos["pista"],
        "size": {
            "columns": nivel.columnas,
            "rows": nivel.num_filas,
            "width": nivel.ancho,
            "height": nivel.alto,
        },
        "spawn": {
            "x": nivel.spawn[0],
            "y": nivel.spawn[1],
            "w": config.JUGADOR_ANCHO,
            "h": config.JUGADOR_ALTO,
        },
        "goal": {
            "x": nivel.meta.x,
            "y": nivel.meta.y,
            "w": nivel.meta.width,
            "h": nivel.meta.height,
        },
        "solids": solidos,
        "souls": almas,
        "enemies": enemigos,
        "enemies_melee": enemigos_melee,
        "hazards": peligros,
        "decorations": decoraciones,
        "platforms": plataformas,
        "palas": palas,
        "powerups": powerups,
        "bosses": jefes,
        "total_souls": len(nivel.almas),
        "ascii": "\n".join(nivel.filas),
    }


def construir_documento():
    return {
        "format": FORMATO,
        "version": VERSION,
        "game": {
            "name": config.TITULO,
            "subtitle": config.SUBTITULO,
            "team": config.EQUIPO,
            "members": list(config.INTEGRANTES),
            "references": list(config.REFERENCIAS),
            "tile": config.TILE,
            "viewport": {"width": config.ANCHO, "height": config.ALTO},
            "rules": reglas(),
            "sizes": tamanos(),
            "palette": paleta(),
            "design": diseno(),
        },
        "levels": [exportar_nivel(i, datos) for i, datos in enumerate(NIVELES)],
    }


def _numero(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser numérico")
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} no es finito")


def _rect_valido(rect, ancho, alto, nombre):
    for clave in ("x", "y", "w", "h"):
        if clave not in rect:
            raise ValueError(f"{nombre}: falta {clave}")
        _numero(rect[clave], f"{nombre}.{clave}")
    if rect["w"] <= 0 or rect["h"] <= 0:
        raise ValueError(f"{nombre}: tamaño inválido")
    if rect["x"] < 0 or rect["y"] < 0:
        raise ValueError(f"{nombre}: posición negativa")
    if rect["x"] + rect["w"] > ancho or rect["y"] + rect["h"] > alto:
        raise ValueError(f"{nombre}: fuera del nivel")


def validar_documento(documento):
    if documento.get("format") != FORMATO:
        raise ValueError("Formato inesperado")
    if documento.get("version") != VERSION:
        raise ValueError("Versión inesperada")

    niveles = documento.get("levels") or []
    if len(niveles) != 3:
        raise ValueError("IN CRYPTA debe tener exactamente 3 niveles")

    diseno_doc = documento["game"].get("design") or {}
    if len(diseno_doc.get("mechanics") or []) != 3:
        raise ValueError("Deben declararse exactamente 3 mecánicas")
    if len(diseno_doc.get("aesthetics") or []) != 2:
        raise ValueError("Deben declararse exactamente 2 estéticas")

    ids = set()
    for nivel in niveles:
        ancho = nivel["size"]["width"]
        alto = nivel["size"]["height"]
        if ancho <= 0 or alto <= 0:
            raise ValueError("Tamaño de nivel inválido")
        if nivel["size"]["columns"] * documento["game"]["tile"] != ancho:
            raise ValueError("Ancho de nivel inconsistente")
        if nivel["size"]["rows"] * documento["game"]["tile"] != alto:
            raise ValueError("Alto de nivel inconsistente")

        filas = nivel["ascii"].splitlines()
        if len(filas) != nivel["size"]["rows"]:
            raise ValueError(f"{nivel['name']}: filas inconsistentes")
        if any(len(fila) != nivel["size"]["columns"] for fila in filas):
            raise ValueError(f"{nivel['name']}: columnas inconsistentes")

        _rect_valido(nivel["spawn"], ancho, alto, f"{nivel['id']}.spawn")
        _rect_valido(nivel["goal"], ancho, alto, f"{nivel['id']}.goal")
        for coleccion in ("solids", "souls", "hazards", "decorations", "palas", "powerups"):
            for rect in nivel.get(coleccion, []):
                _rect_valido(rect, ancho, alto, rect["id"])
                if rect["id"] in ids:
                    raise ValueError(f"Id repetido: {rect['id']}")
                ids.add(rect["id"])

        for plat in nivel.get("platforms", []):
            _rect_valido(plat, ancho, alto, plat["id"])
            if plat["id"] in ids:
                raise ValueError(f"Id repetido: {plat['id']}")
            ids.add(plat["id"])

        for enemigo in nivel.get("enemies_melee", []):
            _rect_valido(enemigo, ancho, alto, enemigo["id"])
            if enemigo["id"] in ids:
                raise ValueError(f"Id repetido: {enemigo['id']}")
            ids.add(enemigo["id"])

        for jefe in nivel.get("bosses", []):
            _rect_valido(jefe, ancho, alto, jefe["id"])
            if jefe["id"] in ids:
                raise ValueError(f"Id repetido: {jefe['id']}")
            ids.add(jefe["id"])

        for decoracion in nivel["decorations"]:
            if decoracion.get("type") not in {"t", "c", "r", "b", "s"}:
                raise ValueError(f"{decoracion['id']}: tipo desconocido")

        for enemigo in nivel["enemies"]:
            _rect_valido(enemigo, ancho, alto, enemigo["id"])
            _numero(enemigo["patrol_min_x"], f"{enemigo['id']}.patrol_min_x")
            _numero(enemigo["patrol_max_x"], f"{enemigo['id']}.patrol_max_x")
            if enemigo["patrol_min_x"] >= enemigo["patrol_max_x"]:
                raise ValueError(f"{enemigo['id']}: patrulla inválida")
            if enemigo["patrol_min_x"] < 0 or enemigo["patrol_max_x"] > ancho:
                raise ValueError(f"{enemigo['id']}: patrulla fuera del nivel")
            if enemigo["x"] < enemigo["patrol_min_x"]:
                raise ValueError(f"{enemigo['id']}: fuera de patrulla")
            if enemigo["x"] + enemigo["w"] > enemigo["patrol_max_x"]:
                raise ValueError(f"{enemigo['id']}: fuera de patrulla")
            if enemigo["id"] in ids:
                raise ValueError(f"Id repetido: {enemigo['id']}")
            ids.add(enemigo["id"])

        reconstruido = Nivel(
            nivel["ascii"],
            nivel["name"],
            nivel["hint"],
            nivel.get("theme", "camposanto"),
        )
        if len(reconstruido.solidos) != len(nivel["solids"]):
            raise ValueError(f"{nivel['name']}: sólidos no coinciden")
        if len(reconstruido.almas) != len(nivel["souls"]):
            raise ValueError(f"{nivel['name']}: almas no coinciden")
        if len(reconstruido.enemigos) != len(nivel["enemies"]):
            raise ValueError(f"{nivel['name']}: enemigos no coinciden")
        if len(reconstruido.decoraciones) != len(nivel["decorations"]):
            raise ValueError(f"{nivel['name']}: decoraciones no coinciden")
        if len(reconstruido.peligros) != len(nivel["hazards"]):
            raise ValueError(f"{nivel['name']}: peligros no coinciden")
        if reconstruido.total_almas != nivel["total_souls"]:
            raise ValueError(f"{nivel['name']}: total de almas inconsistente")

    return {
        "levels": len(niveles),
        "solids": sum(len(n["solids"]) for n in niveles),
        "souls": sum(len(n["souls"]) for n in niveles),
        "enemies": sum(len(n["enemies"]) for n in niveles),
        "hazards": sum(len(n["hazards"]) for n in niveles),
        "decorations": sum(len(n["decorations"]) for n in niveles),
    }


def guardar(documento, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(destino.suffix + ".tmp")
    with temporal.open("w", encoding="utf-8") as archivo:
        json.dump(documento, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")
    temporal.replace(destino)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=RAIZ / "export" / "gdevelop" / "game_data.json",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="valida el documento sin escribir el archivo",
    )
    args = parser.parse_args()

    documento = construir_documento()
    resumen = validar_documento(documento)

    if not args.check:
        guardar(documento, args.output)

    print(
        "EXPORT_OK "
        f"levels={resumen['levels']} "
        f"solids={resumen['solids']} "
        f"souls={resumen['souls']} "
        f"enemies={resumen['enemies']} "
        f"hazards={resumen['hazards']} "
        f"decorations={resumen['decorations']}"
    )
    if not args.check:
        print(f"Archivo: {args.output}")


if __name__ == "__main__":
    main()
