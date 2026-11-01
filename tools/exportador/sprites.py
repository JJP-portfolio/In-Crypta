"""Texturas del export, dibujadas con el código de dibujo del propio juego.

La paridad de sprites no se logra a ojo: se logra usando el mismo código del
Pygame y guardando la superficie con el tamaño EXACTO del rect que la entidad
ocupa en el juego. Si el sprite y la caja de la instancia coinciden, GDevelop
no deforma nada (el error clásico: textura de 52x64 dentro de una caja de
26x26 → el enemigo queda aplastado).

Cada renderizador recibe ``(ancho, alto)`` y devuelve una superficie nueva.
"""

from __future__ import annotations

import pygame

from camara import Camara

ALMA_RECT = 16
CUERVO_RECT = 24
TOTEM_RECT = 32
PALA_RECT = (20, 30)
PELIGRO_RECT = (24, 20)
JEFE_RECT = (48, 64)


def _camara() -> Camara:
    return Camara()


def _superficie(ancho: int, alto: int) -> pygame.Surface:
    return pygame.Surface((int(ancho), int(alto)), pygame.SRCALPHA)


# ------------------------------------------------------------
# Renderizadores por tipo de entidad
# ------------------------------------------------------------
def render_alma(ancho: int, alto: int) -> pygame.Surface:
    from entidades import Alma

    surface = _superficie(ancho, alto)
    offset = ((ancho - ALMA_RECT) // 2, (alto - ALMA_RECT) // 2)
    Alma(pygame.Rect(offset[0], offset[1], ALMA_RECT, ALMA_RECT)).dibujar(
        surface, _camara(), 0.0
    )
    return surface


def render_enemigo(ancho: int, alto: int) -> pygame.Surface:
    from entidades import Enemigo

    surface = _superficie(ancho, alto)
    Enemigo(pygame.Rect(0, 0, ancho, alto), 0, 0).dibujar(surface, _camara(), 0.0)
    return surface


def render_enemigo_melee(ancho: int, alto: int) -> pygame.Surface:
    from entidades import EnemigoMelee

    surface = _superficie(ancho, alto)
    EnemigoMelee(pygame.Rect(0, 0, ancho, alto), 0, 0).dibujar(surface, _camara(), 0.0)
    return surface


def render_polilla(ancho: int, alto: int) -> pygame.Surface:
    from entidades import Polilla

    surface = _superficie(ancho, alto)
    Polilla(pygame.Rect(0, 0, ancho, alto), 0, 0).dibujar(surface, _camara(), 0.0)
    return surface


def render_arana(ancho: int, alto: int) -> pygame.Surface:
    from entidades import Araña

    surface = _superficie(ancho, alto)
    Araña(pygame.Rect(0, 0, ancho, alto), 0, 0).dibujar(surface, _camara(), 0.0)
    return surface


def render_cuervo(ancho: int, alto: int) -> pygame.Surface:
    from entidades import Cuervo

    surface = _superficie(ancho, alto)
    centro = (ancho // 2, alto // 2)
    Cuervo(
        pygame.Rect(0, 0, CUERVO_RECT, CUERVO_RECT),
        centro_x=centro[0],
        centro_y=centro[1],
        radio=3,
        velocidad=1.5,
    ).dibujar(surface, _camara(), 0.0)
    return surface


def render_totem(ancho: int, alto: int) -> pygame.Surface:
    from entidades import TotemProyectil

    surface = _superficie(ancho, alto)
    TotemProyectil(ancho // 2, alto).dibujar(surface, _camara(), 0.0)
    return surface


def render_pala(ancho: int, alto: int) -> pygame.Surface:
    from entidades import PalaRecogible

    surface = _superficie(ancho, alto)
    PalaRecogible(pygame.Rect(0, 0, ancho, alto)).dibujar(surface, _camara(), 0.0)
    return surface


def render_power_up(ancho: int, alto: int) -> pygame.Surface:
    from entidades import RangoPowerUp

    surface = _superficie(ancho, alto)
    RangoPowerUp(pygame.Rect(0, 0, ancho, alto)).dibujar(surface, _camara(), 0.0)
    return surface


def render_power_up_dash(ancho: int, alto: int) -> pygame.Surface:
    from entidades import DashPowerUp

    surface = _superficie(ancho, alto)
    DashPowerUp(pygame.Rect(0, 0, ancho, alto)).dibujar(surface, _camara(), 0.0)
    return surface


def render_checkpoint(ancho: int, alto: int) -> pygame.Surface:
    from entidades import FarolCheckpoint

    surface = _superficie(ancho, alto)
    FarolCheckpoint(pygame.Rect(0, 0, ancho, alto)).dibujar(surface, _camara(), 0.0)
    return surface


def render_peligro(ancho: int, alto: int) -> pygame.Surface:
    from nivel import Nivel

    surface = _superficie(ancho, alto)

    class _MapaFalso:
        peligros = [pygame.Rect(0, 0, ancho, alto)]

    Nivel.dibujar_peligros(_MapaFalso(), surface, _camara())
    return surface


def render_plataforma(ancho: int, alto: int) -> pygame.Surface:
    from nivel import Nivel, PlataformaMovil

    surface = _superficie(ancho, alto)

    class _MapaFalso:
        plataformas = [
            PlataformaMovil(pygame.Rect(0, 0, ancho, alto), "h", 0, 1.0, 0.0)
        ]

    Nivel.dibujar_plataformas(_MapaFalso(), surface, _camara())
    return surface


def render_jefe(ancho: int, alto: int) -> pygame.Surface:
    from entidades import Custodio

    surface = _superficie(ancho, alto)
    Custodio(pygame.Rect(0, 0, ancho, alto), 0, 0).dibujar(surface, _camara(), 0.0)
    return surface


RENDERIZADORES = {
    "alma": render_alma,
    "enemigo": render_enemigo,
    "enemigo_melee": render_enemigo_melee,
    "polilla": render_polilla,
    "arana": render_arana,
    "cuervo": render_cuervo,
    "totem": render_totem,
    "pala": render_pala,
    "power_up_dash": render_power_up_dash,
    "power_up_rango": render_power_up,
    "checkpoint": render_checkpoint,
    "peligro": render_peligro,
    "plataforma": render_plataforma,
    "jefe": render_jefe,
}


def renderizar(kind: str, ancho: int, alto: int) -> pygame.Surface:
    """Renderiza la textura de un tipo de entidad en el tamaño pedido."""
    try:
        renderizador = RENDERIZADORES[kind]
    except KeyError as error:  # pragma: no cover - error de desarrollo
        raise KeyError(f"Tipo de entidad sin sprite: {kind}") from error
    return renderizador(ancho, alto)


def guardar(kind: str, ancho: int, alto: int, ruta, escala: int = 2) -> None:
    """Guarda la textura del tipo de entidad en el tamaño pedido.

    ``escala`` sube la resolución del PNG (la proportion se mantiene, así que
    GDevelop no deforma nada al ajustarlo a la caja de la instancia).
    """
    surface = renderizar(kind, ancho, alto)
    if escala != 1:
        surface = pygame.transform.scale(
            surface,
            (surface.get_width() * escala, surface.get_height() * escala),
        )
    pygame.image.save(surface, str(ruta))
