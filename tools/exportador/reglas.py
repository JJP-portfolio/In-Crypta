"""Reglas genéricas: el comportamiento que sale de los datos del mapa.

Cada regla se genera a partir de la entidad y sus variables, así que no hay
nada escrito "a mano" para un nivel concreto.
"""

from __future__ import annotations

import math

from config import VELOCIDAD_ENEMIGO

from .gdevelop import accion, cond, evento


def regla_plataforma(entidad, nombre_objeto: str) -> list[dict]:
    """Mueve una plataforma móvil igual que en el Pygame.

    En el juego (``nivel.py::PlataformaMovil.actualizar``)::

        desplazamiento = sin(tiempo * velocidad + fase) * amplitud
        rect.x = round(origen_x + desplazamiento)     # eje horizontal
        rect.y = round(origen_y + desplazamiento)     # eje vertical

    En GDevelop la posición se pone con la acción ``SetXY``, que toma los
    parámetros (objeto, signo, x, signo, y). Las dos coordenadas van como
    valores absolutos: la que no se mueve es la de origen, y la otra es la
    fórmula del juego.
    """
    variables = entidad.variables
    origen_x = variables["origen_x"]
    origen_y = variables["origen_y"]
    amplitud = variables["amplitud"]
    velocidad = variables["velocidad"]
    fase = variables["fase"]
    horizontal = variables.get("eje", 1) == 1

    expresion = f"sin(TimeFromStart() * {velocidad} + {fase}) * {amplitud}"
    if horizontal:
        x = f"{origen_x} + {expresion}"
        y = str(origen_y)
    else:
        x = str(origen_x)
        y = f"{origen_y} + {expresion}"
    return [evento([], [accion("SetXY", [nombre_objeto, "=", x, "=", y])])]


def regla_patrulla(nombre_objeto: str, velocidad: float = VELOCIDAD_ENEMIGO) -> list[dict]:
    """Regla de patrulla entre min_x y max_x para cualquier enemigo terrestre."""
    return [
        evento(
            [
                cond("NumberObjectVariable", [nombre_objeto, "dir", "=", "1"]),
                cond("PosX", [nombre_objeto, ">=", f"{nombre_objeto}.Variable(max_x)"]),
            ],
            [accion("SetNumberObjectVariable", [nombre_objeto, "dir", "=", "-1"])],
        ),
        evento(
            [
                cond("NumberObjectVariable", [nombre_objeto, "dir", "=", "-1"]),
                cond("PosX", [nombre_objeto, "<=", f"{nombre_objeto}.Variable(min_x)"]),
            ],
            [accion("SetNumberObjectVariable", [nombre_objeto, "dir", "=", "1"])],
        ),
        evento(
            [],
            [
                accion(
                    "PlatformBehavior::PlatformerObjectBehavior::SetCurrentSpeed",
                    [nombre_objeto, "PlatformerObject", "=", f"{nombre_objeto}.Variable(dir) * {int(velocidad)}"],
                )
            ],
        ),
    ]


def regla_cuervo(entidad, nombre_objeto: str) -> list[dict]:
    """Cuervo: órbita circular/elíptica en torno a centro_x, centro_y."""
    var = entidad.variables
    cx = var.get("centro_x", entidad.rect.centerx)
    cy = var.get("centro_y", entidad.rect.centery)
    radio = var.get("radio", 48)
    velocidad = var.get("velocidad", 1.5)
    x = f"{cx} + cos(TimeFromStart() * {velocidad}) * {radio}"
    y = f"{cy} + sin(TimeFromStart() * {velocidad}) * {int(radio * 0.5)}"
    return [evento([], [accion("SetXY", [nombre_objeto, "=", x, "=", y])])]


def regla_polilla(entidad, nombre_objeto: str) -> list[dict]:
    """Polilla: patrulla horizontal a velocidad reducida con ondulación vertical."""
    vel = int(VELOCIDAD_ENEMIGO * 0.6)
    return [
        *regla_patrulla(nombre_objeto, vel),
        evento(
            [],
            [
                accion(
                    "SetY",
                    [
                        nombre_objeto,
                        "=",
                        f"{entidad.rect.y} + sin(TimeFromStart() * 3) * 8",
                    ],
                )
            ],
        ),
    ]


def reglas_escena(escena) -> list[dict]:
    """Todas las reglas que dependen de los datos de una escena."""
    from .adaptadores import adaptador
    from .pipeline import _numeros_por_tipo, nombre_objeto

    eventos = []
    vistos_patrulla = set()
    for entidad, numero in _numeros_por_tipo(escena):
        adapt = adaptador(entidad.kind)
        obj_name = nombre_objeto(adapt, entidad, numero)
        if adapt.regla == "plataforma":
            eventos.extend(
                regla_plataforma(entidad, obj_name)
            )
        elif adapt.regla == "patrulla":
            target = obj_name if adapt.objeto_por_instancia else adapt.objeto
            if target not in vistos_patrulla:
                vistos_patrulla.add(target)
                if adapt.kind == "polilla":
                    eventos.extend(regla_polilla(entidad, target))
                else:
                    eventos.extend(regla_patrulla(target, VELOCIDAD_ENEMIGO))
        elif adapt.regla == "orbita":
            eventos.extend(regla_cuervo(entidad, obj_name))
    return eventos
