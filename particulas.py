# ============================================================
# particulas.py — Almas, polvo, estelas y chispas de la pala
# ============================================================
# La estética "Sensación" se construye con feedback visual:
# cada acción importante deja una marca breve en pantalla.
# ============================================================

import math
import random

import pygame

from config import AMARILLO, BLANCO, HUESO, NARANJA, ROJO, SANGRE, TURQUESA, VIOLETA


# --- Clase Particula --- #
class Particula:
    def __init__(self, x, y, vx, vy, vida, color, tamano, gravedad=700.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.vida = float(vida)
        self.vida_inicial = float(vida)
        self.color = color
        self.tamano = float(tamano)
        self.gravedad = gravedad

    # --- Función actualizar --- #
    def actualizar(self, dt):
        self.vida -= dt
        self.vy += self.gravedad * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    # --- Función dibujar --- #
    def dibujar(self, surface, camara):
        if self.vida <= 0:
            return

        proporcion = max(0.0, self.vida / self.vida_inicial)
        tamano = max(1, int(self.tamano * proporcion))
        x = int(camara.aplicar_x(self.x))
        y = int(camara.aplicar_y(self.y))
        pygame.draw.circle(surface, self.color, (x, y), tamano)


# --- Clase SistemaParticulas --- #
class SistemaParticulas:
    def __init__(self):
        self.particulas = []

    # --- Función emitir --- #
    def emitir(self, x, y, cantidad, colores, velocidad=180.0, vida=0.45, tamano=4.0, gravedad=700.0):
        for _ in range(cantidad):
            angulo = random.uniform(0, math.tau)
            fuerza = random.uniform(0.35, 1.0) * velocidad
            self.particulas.append(Particula(
                x,
                y,
                math.cos(angulo) * fuerza,
                math.sin(angulo) * fuerza,
                random.uniform(vida * 0.55, vida),
                random.choice(colores),
                random.uniform(tamano * 0.5, tamano),
                gravedad,
            ))

    # --- Función salto --- #
    def salto(self, x, y):
        self.emitir(x, y, 5, (HUESO, (150, 140, 120)), 90, 0.3, 3, 300)

    # --- Función alma --- #
    def alma(self, x, y):
        self.emitir(x, y, 12, (VIOLETA, TURQUESA, BLANCO), 150, 0.6, 4, 120)

    # --- Función dash --- #
    def dash(self, x, y, direccion):
        for _ in range(3):
            self.particulas.append(Particula(
                x + random.uniform(-8, 8),
                y + random.uniform(-12, 12),
                -direccion * random.uniform(80, 220),
                random.uniform(-45, 45),
                random.uniform(0.18, 0.35),
                random.choice((VIOLETA, (170, 140, 220), BLANCO)),
                random.uniform(2, 5),
                0,
            ))

    # --- Función ataque --- #
    def ataque(self, x, y, direccion):
        for _ in range(7):
            self.particulas.append(Particula(
                x + random.uniform(-5, 5),
                y + random.uniform(-10, 10),
                direccion * random.uniform(160, 330),
                random.uniform(-90, 90),
                random.uniform(0.12, 0.24),
                random.choice((AMARILLO, (255, 224, 150), BLANCO)),
                random.uniform(2, 4),
                80,
            ))

    # --- Función pala --- #
    def pala(self, x, y):
        self.emitir(x, y, 14, (HUESO, SANGRE, ROJO, NARANJA), 220, 0.55, 5, 600)

    # --- Función daño --- #
    def daño(self, x, y):
        self.emitir(x, y, 16, (ROJO, (190, 70, 60), BLANCO), 240, 0.6, 5, 700)

    # --- Función meta --- #
    def meta(self, x, y):
        self.emitir(x, y, 30, (AMARILLO, BLANCO, TURQUESA, VIOLETA), 260, 1.0, 5, 300)

    # --- Función actualizar --- #
    def actualizar(self, dt):
        for particula in self.particulas:
            particula.actualizar(dt)
        self.particulas = [p for p in self.particulas if p.vida > 0]

    # --- Función dibujar --- #
    def dibujar(self, surface, camara):
        for particula in self.particulas:
            particula.dibujar(surface, camara)
