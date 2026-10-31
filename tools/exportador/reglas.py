"""Reglas genéricas: el comportamiento que sale de los datos del mapa.

Cada regla se genera a partir de la entidad y sus variables, así que no hay
nada escrito "a mano" para un nivel concreto.
"""

from __future__ import annotations

from .gdevelop import accion, evento


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


def reglas_escena(escena) -> list[dict]:
    """Todas las reglas que dependen de los datos de una escena."""
    from .adaptadores import adaptador
    from .pipeline import _numeros_por_tipo, nombre_objeto

    eventos = []
    for entidad, numero in _numeros_por_tipo(escena):
        adapt = adaptador(entidad.kind)
        if adapt.regla == "plataforma":
            eventos.extend(
                regla_plataforma(entidad, nombre_objeto(adapt, entidad, numero))
            )
    return eventos
