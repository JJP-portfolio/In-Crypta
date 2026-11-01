"""Modelo uniforme de una escena, leído del juego real (``nivel.py``).

El exportador no recalcula la geometría: la pide al juego. Cada tipo de
entidad del mapa se lee con un extractor y queda como una ``Entidad`` uniforme
(kind + rect + variables), así agregar un tipo nuevo al juego es agregar una
fila en ``EXTRACTORES`` y una en ``adaptadores.ADAPTADORES``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from nivel import Nivel


@dataclass(frozen=True)
class Entidad:
    """Una entidad del mapa, en términos independientes de GDevelop."""

    kind: str
    rect: pygame.Rect
    variables: dict = field(default_factory=dict)


@dataclass
class Escena:
    """Una escena exportable: su manifiesto + el nivel real del juego."""

    spec: object
    nivel: Nivel
    entidades: list[Entidad] = field(default_factory=list)

    @property
    def clave(self) -> str:
        return self.spec.clave

    @property
    def nombre(self) -> str:
        return self.spec.nombre

    @property
    def ancho(self) -> int:
        return self.nivel.ancho

    @property
    def alto(self) -> int:
        return self.nivel.alto

    @property
    def solidos(self) -> list[pygame.Rect]:
        return self.nivel.solidos

    @property
    def spawn(self) -> tuple[int, int]:
        return self.nivel.spawn

    @property
    def meta(self) -> pygame.Rect:
        return self.nivel.meta

    def de_kind(self, kind: str) -> list[Entidad]:
        return [e for e in self.entidades if e.kind == kind]


# ------------------------------------------------------------
# Extractores: kind -> lista de entidades leídas del nivel
# ------------------------------------------------------------
def _patrulla(entidad) -> dict:
    return {
        "dir": entidad.direccion,
        "min_x": entidad.minimo_x,
        "max_x": entidad.maximo_x,
    }


def _almas(nivel: Nivel) -> list[Entidad]:
    return [Entidad("alma", alma.rect) for alma in nivel.almas]


def _enemigos(nivel: Nivel) -> list[Entidad]:
    return [Entidad("enemigo", e.rect, _patrulla(e)) for e in nivel.enemigos]


def _enemigos_melee(nivel: Nivel) -> list[Entidad]:
    return [Entidad("enemigo_melee", e.rect, _patrulla(e)) for e in nivel.enemigos_melee]


def _polillas(nivel: Nivel) -> list[Entidad]:
    return [Entidad("polilla", e.rect, _patrulla(e)) for e in nivel.polillas]


def _aranias(nivel: Nivel) -> list[Entidad]:
    return [Entidad("arana", e.rect, _patrulla(e)) for e in nivel.aranias]


def _cuervos(nivel: Nivel) -> list[Entidad]:
    return [
        Entidad(
            "cuervo",
            e.rect,
            {
                "centro_x": e.centro_x,
                "centro_y": e.centro_y,
                "radio": e.radio,
                "velocidad": e.velocidad,
            },
        )
        for e in nivel.cuervos
    ]


def _totems(nivel: Nivel) -> list[Entidad]:
    return [Entidad("totem", t.rect) for t in nivel.totems]


def _palas(nivel: Nivel) -> list[Entidad]:
    return [Entidad("pala", p.rect) for p in nivel.palas]


def _power_ups(nivel: Nivel) -> list[Entidad]:
    return [Entidad("power_up_rango", p.rect) for p in nivel.power_ups_rango]


def _power_ups_dash(nivel: Nivel) -> list[Entidad]:
    return [Entidad("power_up_dash", p.rect) for p in getattr(nivel, "power_ups_dash", [])]


def _checkpoints(nivel: Nivel) -> list[Entidad]:
    return [Entidad("checkpoint", p.rect) for p in getattr(nivel, "checkpoints", [])]


def _peligros(nivel: Nivel) -> list[Entidad]:
    return [Entidad("peligro", pygame.Rect(r)) for r in nivel.peligros]


def _decoraciones(nivel: Nivel) -> list[Entidad]:
    return [Entidad("decoracion", d["rect"], {"tipo": d["tipo"]}) for d in nivel.decoraciones]


def _plataformas(nivel: Nivel) -> list[Entidad]:
    return [
        Entidad(
            "plataforma",
            p.rect,
            {
                "origen_x": p.inicial_rect.x,
                "origen_y": p.inicial_rect.y,
                "amplitud": p.amplitud,
                "velocidad": p.velocidad,
                "fase": round(p.fase, 4),
                "eje": 1 if p.eje == "h" else 0,
            },
        )
        for p in nivel.plataformas
    ]


def _minijefes(nivel: Nivel) -> list[Entidad]:
    return [
        Entidad(
            "minijefe",
            e.rect,
            {
                "vida": e.vida,
                "dir": getattr(e, "direccion", 1),
                "min_x": e.minimo_x,
                "max_x": e.maximo_x,
            },
        )
        for e in getattr(nivel, "minijefes", [])
    ]


def _jefes(nivel: Nivel) -> list[Entidad]:
    return [
        Entidad(
            "jefe",
            e.rect,
            {
                "vida": e.vida,
                "fase": e.fase,
                "min_x": e.minimo_x,
                "max_x": e.maximo_x,
            },
        )
        for e in nivel.jefes
    ]


EXTRACTORES = {
    "alma": _almas,
    "enemigo": _enemigos,
    "enemigo_melee": _enemigos_melee,
    "minijefe": _minijefes,
    "polilla": _polillas,
    "arana": _aranias,
    "cuervo": _cuervos,
    "totem": _totems,
    "pala": _palas,
    "power_up_dash": _power_ups_dash,
    "power_up_rango": _power_ups,
    "checkpoint": _checkpoints,
    "peligro": _peligros,
    "decoracion": _decoraciones,
    "plataforma": _plataformas,
    "jefe": _jefes,
}


def leer_escena(spec) -> Escena:
    """Construye la escena a partir del manifiesto, usando el modelo del juego."""
    nivel = Nivel(spec.mapa, spec.nombre_juego, spec.pista, spec.tema)
    entidades: list[Entidad] = []
    for extractor in EXTRACTORES.values():
        entidades.extend(extractor(nivel))
    return Escena(spec=spec, nivel=nivel, entidades=entidades)
