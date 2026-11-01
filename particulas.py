# ============================================================
# particulas.py — Almas, polvo, estelas, plumas y chispas de la pala
# ============================================================
# Feedback visual poeano y diegético sin asignaciones dinámicas pesadas.
# ============================================================

import math
import random

import pygame

from config import (
    AMARILLO,
    BLANCO,
    CARMESÍ_SANGRE,
    FAROL_CÁLIDO,
    GRIS,
    HUESO,
    HUESO_MARFIL,
    NARANJA,
    NEGRO_NOCHE,
    ORO,
    ORO_LITÚRGICO,
    ROJO,
    SANGRE,
    TURQUESA,
    TURQUESA_ÁNIMA,
    VIOLETA,
    VIOLETA_POE,
)


# --- Clase Particula estándar --- #
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


# --- Clase ParticulaPluma (Plumas del Cuervo) --- #
class ParticulaPluma:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vida = random.uniform(0.9, 1.4)
        self.vida_inicial = self.vida
        self.fase = random.uniform(0, math.tau)
        self.longitud = random.uniform(4.5, 7.5)
        self.angulo = random.uniform(-0.5, 0.5)
        self.velocidad_y = random.uniform(22.0, 36.0)

    def actualizar(self, dt):
        self.vida -= dt
        self.fase += dt * 3.8
        self.x += math.sin(self.fase) * 20.0 * dt
        self.y += self.velocidad_y * dt
        self.angulo += math.sin(self.fase * 0.7) * 0.06

    def dibujar(self, surface, camara):
        if self.vida <= 0:
            return
        cx = camara.aplicar_x(self.x)
        cy = camara.aplicar_y(self.y)
        dx = math.cos(self.angulo) * self.longitud
        dy = math.sin(self.angulo) * self.longitud
        p0 = (int(cx - dx), int(cy - dy))
        p1 = (int(cx + dx), int(cy + dy))
        # Color carbón azabache poeano
        pygame.draw.line(surface, (15, 13, 19), p0, p1, 2)
        pygame.draw.line(surface, (36, 30, 42), (int(cx - dx * 0.4), int(cy - dy * 0.4)), (int(cx + dx * 0.4), int(cy + dy * 0.4)), 1)


# --- Clase SistemaParticulas --- #
class SistemaParticulas:
    def __init__(self):
        self.particulas = []
        self.plumas = []

    # --- Función emitir genérica --- #
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
        self.emitir(x, y, 6, (HUESO_MARFIL, (150, 140, 120), (60, 55, 65)), 90, 0.32, 3, 260)

    # --- Función alma --- #
    def alma(self, x, y):
        self.emitir(x, y, 14, (VIOLETA, TURQUESA_ÁNIMA, BLANCO, (180, 240, 235)), 160, 0.65, 4, 90)

    # --- Función dash (humo negro + chispa turquesa espectral) --- #
    def dash(self, x, y, direccion):
        # Humo negro denso
        for _ in range(4):
            self.particulas.append(Particula(
                x + random.uniform(-6, 6),
                y + random.uniform(-10, 10),
                -direccion * random.uniform(40, 140),
                random.uniform(-30, 30),
                random.uniform(0.24, 0.42),
                random.choice((NEGRO_NOCHE, (26, 22, 32), (42, 35, 50))),
                random.uniform(4, 7),
                -20,
            ))
        # Destellos espectrales turquesa
        for _ in range(3):
            self.particulas.append(Particula(
                x + random.uniform(-8, 8),
                y + random.uniform(-12, 12),
                -direccion * random.uniform(90, 240),
                random.uniform(-40, 40),
                random.uniform(0.18, 0.35),
                random.choice((TURQUESA_ÁNIMA, (160, 230, 220), BLANCO)),
                random.uniform(2, 4),
                0,
            ))

    # --- Función ataque de pala / guadaña --- #
    def ataque(self, x, y, direccion, mejorado=False):
        if mejorado:
            colores = ((215, 80, 255), (245, 170, 255), (170, 50, 240), BLANCO)
            for _ in range(16):
                self.particulas.append(Particula(
                    x + random.uniform(-4, 4),
                    y + random.uniform(-14, 14),
                    direccion * random.uniform(260, 480),
                    random.uniform(-110, 110),
                    random.uniform(0.18, 0.32),
                    random.choice(colores),
                    random.uniform(3, 6),
                    40,
                ))
        else:
            # Chispas de pala de hierro con filo dorado
            colores = (ORO_LITÚRGICO, (240, 215, 130), (220, 220, 230), BLANCO)
            for _ in range(8):
                self.particulas.append(Particula(
                    x + random.uniform(-5, 5),
                    y + random.uniform(-10, 10),
                    direccion * random.uniform(180, 360),
                    random.uniform(-90, 90),
                    random.uniform(0.12, 0.25),
                    random.choice(colores),
                    random.uniform(2, 4),
                    80,
                ))

    # --- Función pala (impacto) --- #
    def pala(self, x, y):
        self.emitir(x, y, 16, (HUESO_MARFIL, CARMESÍ_SANGRE, SANGRE, ORO_LITÚRGICO, BLANCO), 230, 0.55, 5, 580)

    # --- Función stomp (pisotón aéreo: onda expansiva + esquirlas óseas) --- #
    def stomp(self, x, y):
        # Esquirlas de hueso afiladas
        for _ in range(9):
            ang = random.uniform(0.2, math.pi - 0.2)
            fuerza = random.uniform(140, 300)
            self.particulas.append(Particula(
                x,
                y,
                math.cos(ang) * fuerza,
                -math.sin(ang) * fuerza * 0.7,
                random.uniform(0.35, 0.65),
                random.choice((HUESO_MARFIL, BLANCO, (190, 185, 170))),
                random.uniform(2.5, 4.5),
                gravedad=550.0,
            ))
        # Polvo expansivo radial
        for _ in range(10):
            ang = random.uniform(0, math.pi)
            fuerza = random.uniform(90, 220)
            self.particulas.append(Particula(
                x,
                y,
                math.cos(ang) * fuerza,
                -math.sin(ang) * fuerza * 0.4,
                random.uniform(0.25, 0.50),
                random.choice(((95, 90, 98), (65, 60, 72), (135, 130, 140))),
                random.uniform(3.0, 5.5),
                gravedad=200.0,
            ))

    # --- Función chispas_rebote (inmunidad a pala del Custodio) --- #
    def chispas_rebote(self, x, y, direccion=-1):
        for _ in range(14):
            ang = random.uniform(-0.8, 0.8)
            fuerza = random.uniform(180, 380)
            self.particulas.append(Particula(
                x,
                y,
                direccion * math.cos(ang) * fuerza,
                math.sin(ang) * fuerza,
                random.uniform(0.18, 0.38),
                random.choice((ORO_LITÚRGICO, AMARILLO, (255, 235, 160), BLANCO)),
                random.uniform(2, 4.5),
                gravedad=350.0,
            ))

    # --- Función pluma_cuervo --- #
    def pluma_cuervo(self, x, y):
        if len(self.plumas) < 30:
            self.plumas.append(ParticulaPluma(x, y))

    # --- Función daño --- #
    def daño(self, x, y):
        self.emitir(x, y, 16, (ROJO, CARMESÍ_SANGRE, (215, 65, 55), BLANCO), 250, 0.6, 5, 680)

    # --- Función meta --- #
    def meta(self, x, y):
        self.emitir(x, y, 32, (ORO_LITÚRGICO, BLANCO, TURQUESA_ÁNIMA, VIOLETA_POE), 260, 1.0, 5, 280)

    # --- Función actualizar --- #
    def actualizar(self, dt):
        for particula in self.particulas:
            particula.actualizar(dt)
        self.particulas = [p for p in self.particulas if p.vida > 0]

        for pluma in self.plumas:
            pluma.actualizar(dt)
        self.plumas = [pl for pl in self.plumas if pl.vida > 0]

    # --- Función dibujar --- #
    def dibujar(self, surface, camara):
        for pluma in self.plumas:
            pluma.dibujar(surface, camara)
        for particula in self.particulas:
            particula.dibujar(surface, camara)
