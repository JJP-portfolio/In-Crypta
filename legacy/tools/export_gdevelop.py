#!/usr/bin/env python3
"""Exporta IN CRYPTA completo a un JSON que consume el runtime JS de GDevelop.

Versión 2: exporta TODAS las entidades del juego (plataformas, palas,
power-ups, tótems, cuervos, polillas, arañas, enemigos melee, jefes)
además de los tipos básicos.  Si el juego agrega una entidad nueva,
bastará con agregarla en `exportar_nivel()`.

Sin cambiar este archivo, el runtime JS en runtime_gdevelop.js
también puede consumir el JSON extendido.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

import config  # noqa: E402
from nivel import Nivel  # noqa: E402
from niveles import NIVELES, SALAS_PRUEBA, NIVEL_TUTORIAL  # noqa: E402

FORMATO = "incrypta.gdevelop-levels"
VERSION = 2


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
        "vidas_maximas": config.VIDAS_MAXIMAS,
        "almas_por_vida": config.ALMAS_POR_VIDA,
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
        "ataque_duracion": config.ATAQUE_DURACION,
        "ataque_cooldown": config.ATAQUE_COOLDOWN,
        "ataque_alcance": config.ATAQUE_ALCANCE,
        "ataque_alto": config.ATAQUE_ALTO,
        "ataque_alcance_mejorado": config.ATAQUE_ALCANCE_MEJORADO,
        "jefe_vida": config.JEFE_VIDA,
        "jefe_velocidad": config.JEFE_VELOCIDAD,
        "jefe_onda_velocidad": config.JEFE_ONDA_VELOCIDAD,
        "fps": config.FPS,
    }


def tamanos():
    return {
        "tile": config.TILE,
        "jugador": {"w": config.JUGADOR_ANCHO, "h": config.JUGADOR_ALTO},
        "enemigo": {"w": config.ENEMIGO_ANCHO, "h": config.ENEMIGO_ALTO},
        "alma": {"w": 16, "h": 16},
        "pala": {"w": 20, "h": 30},
        "jefe": {"w": config.JEFE_ANCHO, "h": config.JEFE_ALTO},
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


def _entidad_patrulla(entidad, prefijo, indice, tipo="enemigo"):
    """Serializa una entidad con patrulla (mínimo-máximo X)."""
    return {
        "id": f"{prefijo}-{tipo}-{indice:03d}",
        "kind": tipo,
        "x": entidad.rect.x,
        "y": entidad.rect.y,
        "w": entidad.rect.width,
        "h": entidad.rect.height,
        "patrol_min_x": entidad.minimo_x,
        "patrol_max_x": entidad.maximo_x,
        "direction": entidad.direccion,
        "speed": config.VELOCIDAD_ENEMIGO,
    }


def exportar_nivel(prefijo, nivel, pala_inicial=False):
    """Exporta un nivel (o sala) a su representación JSON completa."""
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

    # Enemigos básicos (E)
    enemigos = [
        _entidad_patrulla(e, prefijo, i + 1, "enemigo")
        for i, e in enumerate(nivel.enemigos)
    ]
    # Enemigos melee (L)
    enemigos_melee = [
        _entidad_patrulla(e, prefijo, i + 1, "enemigo_melee")
        for i, e in enumerate(nivel.enemigos_melee)
    ]
    # Polillas (m)
    polillas = [
        _entidad_patrulla(e, prefijo, i + 1, "polilla")
        for i, e in enumerate(nivel.polillas)
    ]
    # Arañas (A)
    aranias = [
        _entidad_patrulla(e, prefijo, i + 1, "arana")
        for i, e in enumerate(nivel.aranias)
    ]
    # Cuervos (C)
    cuervos = [
        {
            "id": f"{prefijo}-cuervo-{i + 1:03d}",
            "kind": "cuervo",
            "x": e.rect.x,
            "y": e.rect.y,
            "w": e.rect.width,
            "h": e.rect.height,
            "center_x": e.centro_x,
            "center_y": e.centro_y,
            "radius": e.radio,
            "speed": e.velocidad,
        }
        for i, e in enumerate(nivel.cuervos)
    ]
    # Tótems (O)
    totems = [
        {
            "id": f"{prefijo}-totem-{i + 1:03d}",
            "kind": "totem",
            "x": t.rect.x,
            "y": t.rect.y,
            "w": t.rect.width,
            "h": t.rect.height,
        }
        for i, t in enumerate(nivel.totems)
    ]
    # Palas recogibles (J)
    palas = [
        {
            "id": f"{prefijo}-pala-{i + 1:03d}",
            "kind": "pala",
            "x": p.rect.x,
            "y": p.rect.y,
            "w": p.rect.width,
            "h": p.rect.height,
        }
        for i, p in enumerate(nivel.palas)
    ]
    # Power-ups de rango (X)
    power_ups_rango = [
        {
            "id": f"{prefijo}-powerup_rango-{i + 1:03d}",
            "kind": "power_up_rango",
            "x": p.rect.x,
            "y": p.rect.y,
            "w": p.rect.width,
            "h": p.rect.height,
        }
        for i, p in enumerate(nivel.power_ups_rango)
    ]
    # Power-ups de dash (D)
    power_ups_dash = [
        {
            "id": f"{prefijo}-powerup_dash-{i + 1:03d}",
            "kind": "power_up_dash",
            "x": p.rect.x,
            "y": p.rect.y,
            "w": p.rect.width,
            "h": p.rect.height,
        }
        for i, p in enumerate(getattr(nivel, "power_ups_dash", []))
    ]
    # Checkpoints diegéticos (F)
    checkpoints = [
        {
            "id": f"{prefijo}-checkpoint-{i + 1:03d}",
            "kind": "checkpoint",
            "x": c.rect.x,
            "y": c.rect.y,
            "w": c.rect.width,
            "h": c.rect.height,
        }
        for i, c in enumerate(getattr(nivel, "checkpoints", []))
    ]
    # Plataformas móviles (Q/V)
    plataformas = [
        {
            "id": f"{prefijo}-plataforma-{i + 1:03d}",
            "kind": "plataforma",
            "x": p.rect.x,
            "y": p.rect.y,
            "w": p.rect.width,
            "h": p.rect.height,
            "origin_x": p.inicial_rect.x,
            "origin_y": p.inicial_rect.y,
            "amplitude": p.amplitud,
            "speed": p.velocidad,
            "phase": round(p.fase, 4),
            "axis": "h" if p.eje == "h" else "v",
        }
        for i, p in enumerate(nivel.plataformas)
    ]
    # Jefe (K)
    jefes = [
        {
            "id": f"{prefijo}-jefe-{i + 1:03d}",
            "kind": "jefe",
            "x": j.rect.x,
            "y": j.rect.y,
            "w": j.rect.width,
            "h": j.rect.height,
            "vida": j.vida,
            "fase": j.fase,
            "min_x": j.minimo_x,
            "max_x": j.maximo_x,
        }
        for i, j in enumerate(nivel.jefes)
    ]

    return {
        "id": prefijo,
        "name": nivel.nombre,
        "theme": nivel.tema,
        "hint": nivel.pista,
        "pala_inicial": pala_inicial,
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
        "hazards": peligros,
        "decorations": decoraciones,
        "enemies": enemigos,
        "enemies_melee": enemigos_melee,
        "moths": polillas,
        "spiders": aranias,
        "crows": cuervos,
        "totems": totems,
        "shovels": palas,
        "powerups_dash": power_ups_dash,
        "powerups_range": power_ups_rango,
        "checkpoints": checkpoints,
        "platforms": plataformas,
        "bosses": jefes,
        "total_souls": nivel.total_almas,
        "ascii": "\n".join(nivel.filas),
    }


def construir_documento():
    pygame.init()

    # Tutorial
    tutorial_nivel = Nivel(NIVEL_TUTORIAL, "Ritual del Sepulturero", "", "camposanto")
    tutorial = exportar_nivel("tutorial", tutorial_nivel, pala_inicial=False)

    # Niveles de campaña
    niveles = []
    for indice, datos in enumerate(NIVELES, start=1):
        nivel = Nivel(
            datos["mapa"],
            datos["nombre"],
            datos["pista"],
            datos.get("tema", "camposanto"),
        )
        pala_inicial = indice >= 3  # igual que juego.py: tiene_pala = indice >= 2 (base 0)
        niv = exportar_nivel(f"nivel_{indice}", nivel, pala_inicial=pala_inicial)
        niv["index"] = indice
        niveles.append(niv)

    # Salas de prueba
    salas = []
    for indice, datos in enumerate(SALAS_PRUEBA, start=1):
        nivel = Nivel(
            datos["mapa"],
            datos["nombre"],
            datos["pista"],
            datos.get("tema", "camposanto"),
        )
        sala = exportar_nivel(f"sala_{indice}", nivel, pala_inicial=bool(datos.get("pala")))
        sala["index"] = indice
        salas.append(sala)

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
        "tutorial": tutorial,
        "levels": niveles,
        "rooms": salas,
    }


def _numero(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError(f"{nombre} debe ser numérico")
    if not math.isfinite(valor):
        raise ValueError(f"{nombre} no es finito")


def _rect_valido(rect, ancho, alto, nombre, relajado=False):
    for clave in ("x", "y", "w", "h"):
        if clave not in rect:
            raise ValueError(f"{nombre}: falta {clave}")
        _numero(rect[clave], f"{nombre}.{clave}")
    if rect["w"] <= 0 or rect["h"] <= 0:
        raise ValueError(f"{nombre}: tamaño inválido")
    if not relajado:
        if rect["x"] < 0 or rect["y"] < 0:
            raise ValueError(f"{nombre}: posición negativa")
        if rect["x"] + rect["w"] > ancho or rect["y"] + rect["h"] > alto:
            raise ValueError(f"{nombre}: fuera del nivel")


def _validar_escena(ids, escena, ancho, alto):
    nombre = escena.get("id", "?")
    _rect_valido(escena["spawn"], ancho, alto, f"{nombre}.spawn")
    _rect_valido(escena["goal"], ancho, alto, f"{nombre}.goal")

    for coleccion in ("solids", "souls", "hazards", "decorations"):
        for rect in escena.get(coleccion, []):
            _rect_valido(rect, ancho, alto, rect["id"])
            if rect["id"] in ids:
                raise ValueError(f"Id repetido: {rect['id']}")
            ids.add(rect["id"])

    for decoracion in escena.get("decorations", []):
        if decoracion.get("type") not in {"t", "c", "r", "b", "s"}:
            raise ValueError(f"{decoracion['id']}: tipo desconocido")

    for enemigo in escena.get("enemies", []):
        _rect_valido(enemigo, ancho, alto, enemigo["id"])
        _numero(enemigo["patrol_min_x"], f"{enemigo['id']}.patrol_min_x")
        _numero(enemigo["patrol_max_x"], f"{enemigo['id']}.patrol_max_x")
        if enemigo["patrol_min_x"] >= enemigo["patrol_max_x"]:
            raise ValueError(f"{enemigo['id']}: patrulla inválida")
        if enemigo["id"] in ids:
            raise ValueError(f"Id repetido: {enemigo['id']}")
        ids.add(enemigo["id"])

    for plataforma in escena.get("platforms", []):
        _rect_valido(plataforma, ancho, alto, plataforma["id"], relajado=True)

    for jefe in escena.get("bosses", []):
        _rect_valido(jefe, ancho, alto, jefe["id"], relajado=True)


def validar_documento(documento):
    if documento.get("format") != FORMATO:
        raise ValueError("Formato inesperado")
    if documento.get("version") != VERSION:
        raise ValueError("Versión inesperada")

    niveles = documento.get("levels") or []
    if len(niveles) != len(NIVELES):
        raise ValueError(f"Se esperaban {len(NIVELES)} niveles, hay {len(niveles)}")

    diseno_doc = documento["game"].get("design") or {}
    if len(diseno_doc.get("mechanics") or []) != 3:
        raise ValueError("Deben declararse exactamente 3 mecánicas")
    if len(diseno_doc.get("aesthetics") or []) != 2:
        raise ValueError("Deben declararse exactamente 2 estéticas")

    ids: set[str] = set()
    todas_las_escenas = [documento.get("tutorial")] + niveles + documento.get("rooms", [])
    todas_las_escenas = [e for e in todas_las_escenas if e]

    for escena in todas_las_escenas:
        ancho = escena["size"]["width"]
        alto = escena["size"]["height"]
        if ancho <= 0 or alto <= 0:
            raise ValueError("Tamaño de escena inválido")
        _validar_escena(ids, escena, ancho, alto)

        # Reconstruir desde el ASCII y comparar
        reconstruido = Nivel(
            escena["ascii"],
            escena["name"],
            escena["hint"],
            escena.get("theme", "camposanto"),
        )
        checks = [
            ("solids", len(reconstruido.solidos), len(escena["solids"])),
            ("souls", len(reconstruido.almas), len(escena["souls"])),
            ("enemies", len(reconstruido.enemigos), len(escena["enemies"])),
            ("decorations", len(reconstruido.decoraciones), len(escena["decorations"])),
            ("hazards", len(reconstruido.peligros), len(escena["hazards"])),
            ("platforms", len(reconstruido.plataformas), len(escena["platforms"])),
            ("enemies_melee", len(reconstruido.enemigos_melee), len(escena["enemies_melee"])),
            ("totems", len(reconstruido.totems), len(escena["totems"])),
            ("cuervos", len(reconstruido.cuervos), len(escena["crows"])),
            ("polillas", len(reconstruido.polillas), len(escena["moths"])),
            ("aranias", len(reconstruido.aranias), len(escena["spiders"])),
            ("jefes", len(reconstruido.jefes), len(escena["bosses"])),
            ("palas", len(reconstruido.palas), len(escena["shovels"])),
            ("power_ups_dash", len(getattr(reconstruido, "power_ups_dash", [])), len(escena["powerups_dash"])),
            ("power_ups_rango", len(reconstruido.power_ups_rango), len(escena["powerups_range"])),
            ("checkpoints", len(getattr(reconstruido, "checkpoints", [])), len(escena["checkpoints"])),
        ]
        for coleccion, esperado, actual in checks:
            if esperado != actual:
                raise ValueError(f"{escena['name']}: {coleccion} no coinciden ({esperado} vs {actual})")

    # Resumen
    return {
        "escenas": len(todas_las_escenas),
        "niveles": len(niveles),
        "salas": len(documento.get("rooms", [])),
        "solids": sum(len(e["solids"]) for e in todas_las_escenas),
        "souls": sum(len(e["souls"]) for e in todas_las_escenas),
        "enemies": sum(len(e["enemies"]) for e in todas_las_escenas),
        "platforms": sum(len(e["platforms"]) for e in todas_las_escenas),
        "hazards": sum(len(e["hazards"]) for e in todas_las_escenas),
        "decorations": sum(len(e["decorations"]) for e in todas_las_escenas),
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
        f"escenas={resumen['escenas']} "
        f"niveles={resumen['niveles']} "
        f"salas={resumen['salas']} "
        f"solids={resumen['solids']} "
        f"souls={resumen['souls']} "
        f"enemies={resumen['enemies']} "
        f"platforms={resumen['platforms']} "
        f"hazards={resumen['hazards']} "
        f"decorations={resumen['decorations']}"
    )
    if not args.check:
        print(f"Archivo: {args.output}")


if __name__ == "__main__":
    main()
