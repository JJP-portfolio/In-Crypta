"""Exportador genérico de IN CRYPTA para GDevelop.

El paquete separa tres cosas que antes vivían mezcladas en un solo script:

* ``manifiesto``: qué escenas existen y con qué reglas (datos, no código).
* ``modelo``: la lectura del modelo real del juego Pygame (nivel.py).
* ``adaptadores``: cómo se traduce cada tipo de entidad a GDevelop.
* ``gdevelop``: primitivas de serialización del formato de proyecto.
* ``sprites``: las texturas, dibujadas con el código del propio juego.

Regla de oro: el exportador no conoce "el nivel 1" ni "la sala 2". Eso vive
en el manifiesto. Y no reimplementa la geometría: la lee del juego.
"""

__all__ = ["adaptadores", "gdevelop", "manifiesto", "modelo", "metadatos", "pipeline", "reglas", "sprites"]
