#---- Funciones de animacion y easing ----#
import math


def ease_out_back(x):
    # Rebote suave hacia afuera
    c = 4
    return float((1 + c) * x**3 - c * x**2)


def ease_out_cubic(x):
    # Desaceleracion cubica
    return float(1 - (1 - x)**3)


def ease_in_out_cubic(x):
    # Aceleracion al inicio y desaceleracion al final
    if x < 0.5:
        return 4 * x**3
    return 1 - 4 * (1 - x)**3
