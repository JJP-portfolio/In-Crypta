"""Pipeline: manifiesto -> modelo del juego -> objetos e instancias.

Es la parte "genérica" del exportador: no sabe qué nivel es cuál, ni si hay
niveles o salas. Solo aplica los adaptadores sobre el modelo uniforme.
"""

from __future__ import annotations

from .adaptadores import Adaptador, adaptador, variables_instancia
from .gdevelop import (
    comportamiento_enemigo,
    comportamiento_plataforma,
    instancia,
    objeto_sprite,
    variables_enemigo,
    variables_plataforma,
)
from .modelo import Entidad, Escena


def nombre_textura(adapt: Adaptador, entidad: Entidad) -> str:
    """Nombre del PNG que se usa como textura del objeto."""
    if adapt.textura_por_tamano:
        return f"{adapt.objeto}_{entidad.rect.width}x{entidad.rect.height}"
    return adapt.textura


def nombre_objeto(adapt: Adaptador, entidad: Entidad, indice: int) -> str:
    """Nombre del objeto de GDevelop para una entidad concreta."""
    if adapt.objeto_por_instancia:
        return f"{adapt.objeto}_{indice}"
    return adapt.objeto


def _variables_objeto(adapt: Adaptador) -> list[dict]:
    if adapt.comportamiento == "enemigo":
        return variables_enemigo()
    if adapt.comportamiento == "plataforma":
        return variables_plataforma()
    return []


def _comportamientos_objeto(adapt: Adaptador) -> list[dict]:
    if adapt.comportamiento == "enemigo":
        return [comportamiento_enemigo()]
    if adapt.comportamiento == "plataforma":
        return [comportamiento_plataforma()]
    return []


def _ancho_alto(adapt: Adaptador, entidad: Entidad) -> tuple[int, int]:
    if adapt.sprite:
        return adapt.sprite
    return (entidad.rect.width, entidad.rect.height)


def _posicion(adapt: Adaptador, entidad: Entidad) -> tuple[int, int]:
    ancho, alto = _ancho_alto(adapt, entidad)
    if adapt.anclaje == "centro":
        return (
            entidad.rect.centerx - ancho // 2,
            entidad.rect.centery - alto // 2,
        )
    return (entidad.rect.x, entidad.rect.y)


def _numeros_por_tipo(escena: Escena) -> list[tuple[Entidad, int]]:
    """Numeración por tipo de entidad (para nombrar los objetos)."""
    contadores: dict[str, int] = {}
    salida = []
    for entidad in escena.entidades:
        tipo = entidad.kind
        contadores[tipo] = contadores.get(tipo, 0) + 1
        salida.append((entidad, contadores[tipo]))
    return salida


# Objetos que los eventos del juego siempre necesitan aunque el mapa actual
# no tenga esa entidad (por ejemplo la pala, el enemigo melee o el power-up:
# los eventos están siempre, pero en niveles sin esa entidad no hay instancias).
KINDS_SIEMPRE = ("pala", "enemigo_melee", "power_up_rango")


def objetos_entidades(escena: Escena) -> list[dict]:
    """Un objeto de GDevelop por tipo de entidad (o por tamaño/instancia)."""
    objetos = []
    vistos: set[str] = set()
    for entidad, numero in _numeros_por_tipo(escena):
        adapt = adaptador(entidad.kind)
        if adapt.en_fondo:
            continue
        nombre = nombre_objeto(adapt, entidad, numero)
        if nombre in vistos:
            continue
        vistos.add(nombre)
        objetos.append(
            objeto_sprite(
                nombre,
                nombre_textura(adapt, entidad),
                _variables_objeto(adapt),
                _comportamientos_objeto(adapt),
            )
        )
    for kind in KINDS_SIEMPRE:
        adapt = adaptador(kind)
        if adapt.objeto in vistos:
            continue
        vistos.add(adapt.objeto)
        objetos.append(
            objeto_sprite(
                adapt.objeto,
                adapt.textura,
                _variables_objeto(adapt),
                _comportamientos_objeto(adapt),
            )
        )
    return objetos


def instancias_entidades(escena: Escena) -> list[dict]:
    """Una instancia por entidad, con su posición exacta del juego."""
    instancias = []
    for entidad, numero in _numeros_por_tipo(escena):
        adapt = adaptador(entidad.kind)
        if adapt.en_fondo:
            continue
        ancho, alto = _ancho_alto(adapt, entidad)
        x, y = _posicion(adapt, entidad)
        instancias.append(
            instancia(
                nombre_objeto(adapt, entidad, numero),
                x,
                y,
                adapt.z,
                tam=(ancho, alto),
                variables=variables_instancia(adapt, entidad),
            )
        )
    return instancias
