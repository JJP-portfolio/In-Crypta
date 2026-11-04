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
    PIEDRA_FRIA,
    ROJO,
    SALITRE_CRIPTA,
    SANGRE,
    TURQUESA,
    TURQUESA_ÁNIMA,
    VIOLETA,
    VIOLETA_POE,
)

FX_IMPACTO_BLANCO = (250, 248, 240)


# --- Clase Particula estándar --- #
class HitSpark:
    """Destello de impacto de combate (Modelos D1 NES, D2 SNES, D3 PROC)."""
    def __init__(self, x, y, direccion=1, mejorado=False):
        self.x = float(x)
        self.y = float(y)
        self.direccion = direccion
        self.mejorado = mejorado
        self.vida = 0.07
        self.vida_inicial = 0.07

    def actualizar(self, dt):
        self.vida -= dt

    def dibujar(self, surface, camara):
        if self.vida <= 0:
            return
        import config
        estilo = config.resolver_estilo(getattr(config, "ESTILO_EFECTOS", "AUTO"))
        cx = int(camara.aplicar_x(self.x))
        cy = int(camara.aplicar_y(self.y))
        progreso = max(0.0, self.vida / self.vida_inicial)
        color_centro = (255, 255, 255)
        color_puntas = (215, 80, 255) if self.mejorado else (216, 180, 104)

        if estilo == "NES":
            # Modelo D1 (NES): Cruz ortogonal 8-bit de 2px
            radio = int(6 * progreso) + 2
            pygame.draw.line(surface, color_puntas, (cx - radio, cy), (cx + radio, cy), 2)
            pygame.draw.line(surface, color_puntas, (cx, cy - radio), (cx, cy + radio), 2)
            pygame.draw.rect(surface, color_centro, (cx - 1, cy - 1, 3, 3))
        elif estilo == "SNES":
            # Modelo D2 (SNES): Destello biseccionado con halo
            radio = int(8 * progreso) + 3
            pygame.draw.line(surface, color_puntas, (cx - radio, cy), (cx + radio, cy), 2)
            pygame.draw.line(surface, color_puntas, (cx, cy - radio), (cx, cy + radio), 2)
            pygame.draw.line(surface, color_centro, (cx - radio // 2, cy - radio // 2), (cx + radio // 2, cy + radio // 2), 1)
            pygame.draw.line(surface, color_centro, (cx - radio // 2, cy + radio // 2), (cx + radio // 2, cy - radio // 2), 1)
            pygame.draw.circle(surface, color_centro, (cx, cy), 2)
        else:
            # Modelo D3 (PROC): Estrella gótica de 4 puntas afiladas con núcleo blanco
            radio = int(10 * progreso) + 4
            puntos = [
                (cx, cy - radio),
                (cx + 2, cy - 2),
                (cx + radio, cy),
                (cx + 2, cy + 2),
                (cx, cy + radio),
                (cx - 2, cy + 2),
                (cx - radio, cy),
                (cx - 2, cy - 2),
            ]
            pygame.draw.polygon(surface, color_puntas, puntos)
            pygame.draw.polygon(surface, color_centro, [
                (cx, cy - radio // 2),
                (cx + 1, cy - 1),
                (cx + radio // 2, cy),
                (cx + 1, cy + 1),
                (cx, cy + radio // 2),
                (cx - 1, cy + 1),
                (cx - radio // 2, cy),
                (cx - 1, cy - 1),
            ])


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
        self.sparks = []
        self.factor_calidad = 1.0

    def emitir_dirigida(self, x, y, vx, vy, color, vida, tamano, gravedad=700.0):
        self.particulas.append(Particula(x, y, vx, vy, vida, color, tamano, gravedad))

    def hit_spark(self, x, y, direccion=1, mejorado=False):
        """Estrella gótica de 4 puntas afiladas + chispas direccionales en cono de 45 grados."""
        self.sparks.append(HitSpark(x, y, direccion, mejorado))
        col_principal = (195, 85, 250) if mejorado else (218, 178, 86)
        # Partícula central de destello estelar
        self.emitir(x, y, 4, (FX_IMPACTO_BLANCO, col_principal), 40, 0.14, 4.5, 0)
        # Esquirlas direccionales en arco de 45 grados
        ang_base = 0.0 if direccion >= 0 else math.pi
        cantidad = max(2, int(10 * getattr(self, "factor_calidad", 1.0)))
        for _ in range(cantidad):
            ang = ang_base + random.uniform(-0.39, 0.39)
            vel = random.uniform(110.0, 260.0)
            self.emitir_dirigida(
                x, y,
                vx=math.cos(ang) * vel,
                vy=math.sin(ang) * vel - 35.0,
                color=random.choice((col_principal, (228, 224, 210), (92, 220, 200))),
                vida=random.uniform(0.18, 0.32),
                tamano=random.uniform(2.0, 3.5),
                gravedad=380.0,
            )

    def disolucion_enemigo(self, x, y, ancho=24, alto=24):
        """Disolución etérea al morir un enemigo: cenizas ascendentes con gravedad negativa."""
        cantidad = max(4, int(16 * getattr(self, "factor_calidad", 1.0)))
        colores = ((92, 220, 200), (181, 185, 194), (68, 62, 82), (228, 224, 210))
        for _ in range(cantidad):
            px = x + random.uniform(-ancho * 0.45, ancho * 0.45)
            py = y + random.uniform(-alto * 0.45, alto * 0.45)
            self.emitir(
                px, py, 1, colores,
                velocidad=35,
                vida=random.uniform(0.45, 0.85),
                tamano=random.uniform(1.8, 3.2),
                gravedad=-95,  # Gravedad negativa: las cenizas ascienden hacia la bóveda
            )

    # --- Función emitir genérica --- #
    def emitir(self, x, y, cantidad, colores, velocidad=180.0, vida=0.45, tamano=4.0, gravedad=700.0):
        cant = max(1, int(round(cantidad * getattr(self, "factor_calidad", 1.0))))
        for _ in range(cant):
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

    # --- Función losa_romper --- #
    def losa_romper(self, x, y, w=32):
        """Estallido de 8 a 10 esquirlas de hueso y piedra al fracturarse una losa."""
        for _ in range(8):
            self.particulas.append(Particula(
                x + random.uniform(-w // 2, w // 2),
                y,
                random.uniform(-80, 80),
                random.uniform(-60, 30),
                random.uniform(0.35, 0.65),
                random.choice((HUESO_MARFIL, SALITRE_CRIPTA, PIEDRA_FRIA, BLANCO)),
                random.uniform(2.5, 4.5),
                gravedad=550.0,
            ))

    # --- Función campana_repique --- #
    def campana_repique(self, x, y):
        """Onda expansiva turquesa y dorada con partículas radiantes al percutir la campana."""
        for _ in range(16):
            ang = random.uniform(0, math.tau)
            vel = random.uniform(80, 220)
            self.particulas.append(Particula(
                x,
                y,
                math.cos(ang) * vel,
                math.sin(ang) * vel,
                random.uniform(0.35, 0.60),
                random.choice((TURQUESA_ÁNIMA, (180, 255, 245), ORO_LITÚRGICO, BLANCO)),
                random.uniform(2.5, 5.0),
                gravedad=80.0,
            ))

    # --- Función consagracion_farol --- #
    def consagracion_farol(self, x, y, tier=1):
        """Columna ascendente de partículas celestes y doradas al consagrar un farol."""
        cantidad = 14 + tier * 8
        colores = (TURQUESA_ÁNIMA, BLANCO, (160, 240, 235)) if tier == 1 else (
            ((120, 220, 255), ORO_LITÚRGICO, BLANCO, (255, 235, 160)) if tier == 2 else
            (ORO_LITÚRGICO, (255, 215, 80), TURQUESA_ÁNIMA, BLANCO, (240, 180, 255))
        )
        for _ in range(cantidad):
            self.particulas.append(Particula(
                x + random.uniform(-10, 10),
                y - random.uniform(4, 16),
                random.uniform(-25, 25),
                random.uniform(-180, -320),
                random.uniform(0.55, 0.95),
                random.choice(colores),
                random.uniform(2.5, 4.5),
                gravedad=-30.0,
            ))

    # --- Función actualizar --- #
    def actualizar(self, dt):
        for particula in self.particulas:
            particula.actualizar(dt)
        self.particulas = [p for p in self.particulas if p.vida > 0]

        for pluma in self.plumas:
            pluma.actualizar(dt)
        self.plumas = [pl for pl in self.plumas if pl.vida > 0]

        for spark in self.sparks:
            spark.actualizar(dt)
        self.sparks = [s for s in self.sparks if s.vida > 0]

    # --- Función dibujar --- #
    def dibujar(self, surface, camara):
        for pluma in self.plumas:
            pluma.dibujar(surface, camara)
        for particula in self.particulas:
            particula.dibujar(surface, camara)
        for spark in self.sparks:
            spark.dibujar(surface, camara)
