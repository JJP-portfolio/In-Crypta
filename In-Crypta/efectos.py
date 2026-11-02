# ============================================================
# efectos.py - Funciones de easing y animaciones del HUD
# ============================================================

import math
import time

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


class EfectoAnimacion:
    """Gestión de animaciones del HUD con tiempo actual"""
    
    def __init__(self):
        self.tiempo_inicio = 0
        self.duracion = 0
        self.tipo = None
        self.valor = 0
        self.valor_objetivo = 0
        self.tiempo_actual = 0

    def iniciar(self, tipo: str, valor_objetivo: float, duracion: float):
        self.tipo = tipo
        self.valor_objetivo = valor_objetivo
        self.duracion = duracion
        self.tiempo_inicio = time.time()
        self.valor = 0

    def actualizar(self) -> float:
        if not self.duracion:
            return self.valor_objetivo
        
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        progreso = min(1.0, tiempo_transcurrido / self.duracion)
        
        if self.tipo == "escala":
            self.valor = ease_out_back(progreso)
        elif self.tipo == "opacidad":
            self.valor = ease_out_cubic(progreso)
        elif self.tipo == "escala_estrella":
            self.valor = ease_in_out_cubic(progreso)
        
        return self.valor

    def esta_completado(self) -> bool:
        return time.time() - self.tiempo_inicio >= self.duracion

    def valor_actual(self) -> float:
        return self.valor


class HitstopManager:
    """Gestor de freeze-frames quirúrgicos para impactos pesados (Juice it or lose it)."""
    
    def __init__(self):
        self.tiempo_restante = 0.0

    def congelar(self, duracion: float = 0.05):
        """Congela la actualización física por N segundos (ej: 0.05s = 3 cuadros a 60fps)."""
        self.tiempo_restante = max(self.tiempo_restante, duracion)

    def actualizar(self, dt: float) -> bool:
        """Actualiza el temporizador de hitstop. Retorna True si el tiempo está congelado."""
        if self.tiempo_restante > 0:
            self.tiempo_restante = max(0.0, self.tiempo_restante - dt)
            return True
        return False

    @property
    def activo(self) -> bool:
        return self.tiempo_restante > 0

