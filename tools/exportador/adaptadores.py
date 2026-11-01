"""Adaptadores: cómo se traduce cada tipo de entidad del juego a GDevelop.

Un adaptador por tipo de entidad. Dice qué objeto de GDevelop la representa,
qué textura usa, en qué capa y con qué orden de dibujo, qué variables se le
exportan y qué regla de eventos la anima.

Agregar un tipo de entidad al export = agregar una fila acá. No hay que tocar
la generación de objetos ni de instancias.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from config import ENEMIGO_ALTO, ENEMIGO_ANCHO, JEFE_ALTO, JEFE_ANCHO, TILE

SOUL_SPRITE = 24
GATE_W = 42
GATE_H = 58
PINCHOS_W = TILE - 8
PINCHOS_H = TILE - 12
PALA_W = 20
PALA_ALTO = 30
CUERVO_SPRITE = 24
TOTEM_SPRITE = 32
CUERVO_ANCHO = 24
CUERVO_ALTO = 24


@dataclass(frozen=True)
class Adaptador:
    """Traducción de un kind del juego a un objeto de GDevelop."""

    kind: str
    objeto: str
    textura: str
    z: int = 2
    comportamiento: str | None = None
    regla: str | None = None
    variables: tuple[str, ...] = ()
    sprite: tuple[int, int] | None = None
    anclaje: str = "esquina"
    objeto_por_instancia: bool = False
    textura_por_tamano: bool = False
    en_fondo: bool = False
    nota: str = ""


ADAPTADORES: dict[str, Adaptador] = {
    "alma": Adaptador(
        "alma", "Alma", "Alma", z=3,
        sprite=(SOUL_SPRITE, SOUL_SPRITE),
        anclaje="centro",
        nota="El alma flota: su sprite es más grande que su rect de colisión.",
    ),
    "enemigo": Adaptador(
        "enemigo", "Enemy", "Enemy", z=5,
        comportamiento="enemigo", regla="patrulla",
        variables=("dir", "min_x", "max_x"),
        sprite=(ENEMIGO_ANCHO, ENEMIGO_ALTO),
    ),
    "enemigo_melee": Adaptador(
        "enemigo_melee", "EnemyMelee", "EnemyMelee", z=5,
        comportamiento="enemigo", regla="patrulla",
        variables=("dir", "min_x", "max_x"),
        sprite=(ENEMIGO_ANCHO, ENEMIGO_ALTO),
        nota="Paradoja de fase 2: aparece con la pala.",
    ),
    "polilla": Adaptador(
        "polilla", "Polilla", "Polilla", z=5,
        comportamiento="enemigo", regla="patrulla",
        variables=("dir", "min_x", "max_x"),
        sprite=(ENEMIGO_ANCHO, ENEMIGO_ALTO),
    ),
    "arana": Adaptador(
        "arana", "Arana", "Arana", z=5,
        comportamiento="enemigo", regla="patrulla",
        variables=("dir", "min_x", "max_x"),
        sprite=(ENEMIGO_ANCHO, ENEMIGO_ALTO),
    ),
    "cuervo": Adaptador(
        "cuervo", "Cuervo", "Cuervo", z=5,
        regla="orbita",
        variables=("centro_x", "centro_y", "radio", "velocidad"),
        sprite=(CUERVO_SPRITE, CUERVO_SPRITE),
    ),
    "totem": Adaptador(
        "totem", "Totem", "Totem", z=5,
        regla="totem",
        sprite=(TOTEM_SPRITE, TOTEM_SPRITE),
    ),
    "pala": Adaptador(
        "pala", "PalaRecogible", "Pala", z=4,
        sprite=(PALA_W, PALA_ALTO),
    ),
    "power_up_dash": Adaptador(
        "power_up_dash", "PowerUpDash", "PowerUpDash", z=4,
        sprite=(PALA_W, PALA_ALTO),
    ),
    "power_up_rango": Adaptador(
        "power_up_rango", "PowerUpRango", "PowerUpRango", z=4,
        sprite=(PALA_W, PALA_ALTO),
    ),
    "checkpoint": Adaptador(
        "checkpoint", "FarolCheckpoint", "FarolCheckpoint", z=3,
        sprite=(PALA_W, PALA_ALTO),
    ),
    "peligro": Adaptador(
        "peligro", "Pinchos", "Pinchos", z=2,
        sprite=(PINCHOS_W, PINCHOS_H),
    ),
    "decoracion": Adaptador(
        "decoracion", "", "", z=0,
        en_fondo=True,
        nota="Las decoraciones ya están horneadas en la textura de fondo.",
    ),
    "plataforma": Adaptador(
        "plataforma", "PlataformaMovil", "PlataformaMovil", z=4,
        comportamiento="plataforma", regla="plataforma",
        variables=("origen_x", "origen_y", "amplitud", "velocidad", "fase", "eje"),
        objeto_por_instancia=True,
        textura_por_tamano=True,
        nota="Un objeto por plataforma (su recorrido es propio) y una textura "
             "por ancho, para que el sprite no se deforme.",
    ),
    "jefe": Adaptador(
        "jefe", "Jefe", "Jefe", z=5,
        regla="jefe",
        variables=("vida", "fase", "min_x", "max_x"),
        sprite=(JEFE_ANCHO, JEFE_ALTO),
    ),
}


def adaptador(kind: str) -> Adaptador:
    try:
        return ADAPTADORES[kind]
    except KeyError as error:  # pragma: no cover - error de desarrollo
        raise KeyError(f"Tipo de entidad sin adaptador: {kind}") from error


def variables_instancia(adapt: Adaptador, entidad) -> list[dict]:
    """Serializa las variables declaradas por el adaptador para una entidad."""
    salida = []
    for nombre in adapt.variables:
        if nombre not in entidad.variables:
            continue
        valor = entidad.variables[nombre]
        tipo = "number" if isinstance(valor, (int, float)) and not isinstance(valor, bool) else "string"
        salida.append({"name": nombre, "type": tipo, "value": valor})
    return salida
