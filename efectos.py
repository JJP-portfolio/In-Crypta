# ============================================================
# efectos.py - Funciones de easing para animaciones y tweens
# ============================================================

import math

# Funciones de easing para animaciones suaves
def ease_out_back(x: float) -> float:
    c = 4
    return float((1 + c) * x**3 - c * x**2)


def ease_out_cubic(x: float) -> float:
    return float(1 - (1 - x)**3)


def ease_in_out_cubic(x: float) -> float:
    if x < 0.5:
        return 4 * x**3
    return 1 - 4 * (1 - x)**3

