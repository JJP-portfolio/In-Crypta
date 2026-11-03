#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fisica_decorativa.py — Simulación de Física Secundaria Decorativa para IN CRYPTA Commercial Edition.
===================================================================================================
Controla la dinámica de elementos no colisionables (cadenas de osario, candelabros e incensarios)
mediante cuerpos rígidos articulados (Pymunk) o integración Verlet suave.
Garantiza que la física matemática determinista del jugador (saltos, dash, rebotes)
permanezca 100% aislada e inalterada.
"""

from __future__ import annotations
import math
from typing import List, Tuple
import pygame

try:
    import pymunk
    HAS_PYMUNK = True
except ImportError:
    HAS_PYMUNK = False
    pymunk = None


class EslabonCadena:
    def __init__(self, x: float, y: float, longitud: float = 14.0):
        self.x = x
        self.y = y
        self.ant_x = x
        self.ant_y = y
        self.longitud = longitud


class CadenaVerlet:
    """Cadena física decorativa resuelta mediante integración Verlet."""
    def __init__(self, anclaje_x: float, anclaje_y: float, num_eslabones: int = 8, longitud_eslabon: float = 12.0):
        self.anclaje_x = anclaje_x
        self.anclaje_y = anclaje_y
        self.eslabones: List[EslabonCadena] = []
        for i in range(num_eslabones):
            self.eslabones.append(EslabonCadena(anclaje_x, anclaje_y + i * longitud_eslabon, longitud_eslabon))

    def aplicar_impulso(self, fuerza_x: float, fuerza_y: float):
        for e in self.eslabones:
            e.ant_x -= fuerza_x
            e.ant_y -= fuerza_y

    def actualizar(self, dt: float, gravedad: float = 480.0):
        dt_sq = dt * dt
        # 1. Integración de posición
        for e in self.eslabones:
            vx = (e.x - e.ant_x) * 0.985  # Amortiguación
            vy = (e.y - e.ant_y) * 0.985
            e.ant_x = e.x
            e.ant_y = e.y
            e.x += vx
            e.y += vy + gravedad * dt_sq

        # 2. Restricciones de distancia (3 iteraciones para rigidez)
        self.eslabones[0].x = self.anclaje_x
        self.eslabones[0].y = self.anclaje_y

        for _ in range(3):
            for i in range(len(self.eslabones) - 1):
                e1 = self.eslabones[i]
                e2 = self.eslabones[i + 1]
                dx = e2.x - e1.x
                dy = e2.y - e1.y
                dist = math.hypot(dx, dy)
                if dist > 0.0001:
                    diff = (dist - e1.longitud) / dist
                    offset_x = dx * 0.5 * diff
                    offset_y = dy * 0.5 * diff
                    if i > 0:
                        e1.x += offset_x
                        e1.y += offset_y
                    e2.x -= offset_x
                    e2.y -= offset_y

    def dibujar(self, destino: pygame.Surface, camara_x: float = 0.0, camara_y: float = 0.0, color=(40, 36, 48)):
        puntos = [(int(self.anclaje_x - camara_x), int(self.anclaje_y - camara_y))]
        for e in self.eslabones:
            puntos.append((int(e.x - camara_x), int(e.y - camara_y)))

        if len(puntos) >= 2:
            pygame.draw.lines(destino, color, False, puntos, 2)
            # Dibujar el peso / incensario final
            fin_x, fin_y = puntos[-1]
            pygame.draw.circle(destino, (75, 65, 80), (fin_x, fin_y), 4)
            pygame.draw.circle(destino, (220, 160, 40), (fin_x, fin_y), 2)


class SimuladorFisicaDecorativa:
    """Gestor unificado de física decorativa (soporta Pymunk y Verlet nativo)."""
    def __init__(self):
        self.tiene_pymunk = HAS_PYMUNK
        self.espacio = None
        if self.tiene_pymunk:
            self.espacio = pymunk.Space()
            self.espacio.gravity = (0.0, 900.0)
            self.espacio.damping = 0.95

        self.cadenas: List[CadenaVerlet] = []

    def crear_cadena(self, x: float, y: float, eslabones: int = 7) -> CadenaVerlet:
        cadena = CadenaVerlet(x, y, eslabones)
        self.cadenas.append(cadena)
        return cadena

    def reaccionar_onda_expansiva(self, x_onda: float, y_onda: float, radio: float = 180.0, fuerza: float = 15.0):
        for c in self.cadenas:
            dx = c.anclaje_x - x_onda
            if abs(dx) < radio:
                signo = 1.0 if dx >= 0 else -1.0
                c.aplicar_impulso(signo * fuerza * (1.0 - abs(dx) / radio), -2.0)

    def actualizar(self, dt: float):
        if self.espacio is not None:
            self.espacio.step(dt)
        for c in self.cadenas:
            c.actualizar(dt)

    def dibujar(self, destino: pygame.Surface, camara_x: float = 0.0, camara_y: float = 0.0):
        for c in self.cadenas:
            c.dibujar(destino, camara_x, camara_y)
