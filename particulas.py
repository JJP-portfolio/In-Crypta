#---- Importamos librerias y configuracion ----#
import math
import random
import pygame

from config import (
    AMARILLO,
    BLANCO,
    CARMESI_SANGRE,
    FAROL_CALIDO,
    GRIS,
    HUESO,
    HUESO_MARFIL,
    NARANJA,
    NEGRO_NOCHE,
    ORO,
    ORO_LITURGICO,
    PIEDRA_FRIA,
    ROJO,
    SALITRE_CRIPTA,
    SANGRE,
    TURQUESA,
    TURQUESA_ANIMA,
    VIOLETA,
    VIOLETA_POE,
)

FX_IMPACTO_BLANCO = (250, 248, 240)


#---- Chispas de impacto ----#
class HitSpark:
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
            # Cruz sencilla tipo retro
            radio = int(6 * progreso) + 2
            pygame.draw.line(surface, color_puntas, (cx - radio, cy), (cx + radio, cy), 2)
            pygame.draw.line(surface, color_puntas, (cx, cy - radio), (cx, cy + radio), 2)
            pygame.draw.rect(surface, color_centro, (cx - 1, cy - 1, 3, 3))
        elif estilo == "SNES":
            # Destello en diagonal con cruz
            radio = int(8 * progreso) + 3
            pygame.draw.line(surface, color_puntas, (cx - radio, cy), (cx + radio, cy), 2)
            pygame.draw.line(surface, color_puntas, (cx, cy - radio), (cx, cy + radio), 2)
            pygame.draw.line(surface, color_centro, (cx - radio // 2, cy - radio // 2), (cx + radio // 2, cy + radio // 2), 1)
            pygame.draw.line(surface, color_centro, (cx - radio // 2, cy + radio // 2), (cx + radio // 2, cy - radio // 2), 1)
            pygame.draw.circle(surface, color_centro, (cx, cy), 2)
        else:
            # Estrella de cuatro puntas
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


#---- Particula individual ----#
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

    def actualizar(self, dt):
        self.vida -= dt
        self.vy += self.gravedad * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def dibujar(self, surface, camara):
        if self.vida <= 0:
            return

        proporcion = max(0.0, self.vida / self.vida_inicial)
        tamano = max(1, int(self.tamano * proporcion))
        x = int(camara.aplicar_x(self.x))
        y = int(camara.aplicar_y(self.y))
        pygame.draw.circle(surface, self.color, (x, y), tamano)


#---- Plumas de los cuervos ----#
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
        pygame.draw.line(surface, (15, 13, 19), p0, p1, 2)
        pygame.draw.line(surface, (36, 30, 42), (int(cx - dx * 0.4), int(cy - dy * 0.4)), (int(cx + dx * 0.4), int(cy + dy * 0.4)), 1)


#---- Administrador general de particulas ----#
class SistemaParticulas:
    def __init__(self):
        self.particulas = []
        self.plumas = []
        self.sparks = []
        self.factor_calidad = 1.0

    def emitir_dirigida(self, x, y, vx, vy, color, vida, tamano, gravedad=700.0):
        self.particulas.append(Particula(x, y, vx, vy, vida, color, tamano, gravedad))

    def hit_spark(self, x, y, direccion=1, mejorado=False):
        # Efecto de golpe con chispas direccionales
        self.sparks.append(HitSpark(x, y, direccion, mejorado))
        col_principal = (195, 85, 250) if mejorado else (218, 178, 86)
        self.emitir(x, y, 4, (FX_IMPACTO_BLANCO, col_principal), 40, 0.14, 4.5, 0)

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
        # Cenizas que suben cuando muere un enemigo
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
                gravedad=-95,
            )

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

    def salto(self, x, y):
        # Polvo que levanta al saltar
        self.emitir(x, y, 6, (HUESO_MARFIL, (150, 140, 120), (60, 55, 65)), 90, 0.32, 3, 260)

    def alma(self, x, y):
        # Brillo al recoger un alma
        self.emitir(x, y, 14, (VIOLETA, TURQUESA_ANIMA, BLANCO, (180, 240, 235)), 160, 0.65, 4, 90)

    def dash(self, x, y, direccion):
        # Estela y humo al usar dash
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
        for _ in range(3):
            self.particulas.append(Particula(
                x + random.uniform(-8, 8),
                y + random.uniform(-12, 12),
                -direccion * random.uniform(90, 240),
                random.uniform(-40, 40),
                random.uniform(0.18, 0.35),
                random.choice((TURQUESA_ANIMA, (160, 230, 220), BLANCO)),
                random.uniform(2, 4),
                0,
            ))

    def ataque(self, x, y, direccion, mejorado=False):
        # Chispas al atacar con pala o guadana
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
            colores = (ORO_LITURGICO, (240, 215, 130), (220, 220, 230), BLANCO)
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

    def pala(self, x, y):
        # Golpe seco de la pala
        self.emitir(x, y, 16, (HUESO_MARFIL, CARMESI_SANGRE, SANGRE, ORO_LITURGICO, BLANCO), 230, 0.55, 5, 580)

    def stomp(self, x, y):
        # Impacto del pisoton en el aire
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

    def chispas_rebote(self, x, y, direccion=-1):
        # Rebote de pala contra armadura
        for _ in range(14):
            ang = random.uniform(-0.8, 0.8)
            fuerza = random.uniform(180, 380)
            self.particulas.append(Particula(
                x,
                y,
                direccion * math.cos(ang) * fuerza,
                math.sin(ang) * fuerza,
                random.uniform(0.18, 0.38),
                random.choice((ORO_LITURGICO, AMARILLO, (255, 235, 160), BLANCO)),
                random.uniform(2, 4.5),
                gravedad=350.0,
            ))

    def pluma_cuervo(self, x, y):
        if len(self.plumas) < 30:
            self.plumas.append(ParticulaPluma(x, y))

    def daño(self, x, y):
        # Salpicadura al recibir danio
        self.emitir(x, y, 16, (ROJO, CARMESI_SANGRE, (215, 65, 55), BLANCO), 250, 0.6, 5, 680)

    # Alias sin acento
    dano = daño

    def meta(self, x, y):
        # Destello al cruzar el porton
        self.emitir(x, y, 32, (ORO_LITURGICO, BLANCO, TURQUESA_ANIMA, VIOLETA_POE), 260, 1.0, 5, 280)

    def losa_romper(self, x, y, w=32):
        # Fragmentos al romperse una losa
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

    def campana_repique(self, x, y):
        # Onda al golpear una campana
        for _ in range(16):
            ang = random.uniform(0, math.tau)
            vel = random.uniform(80, 220)
            self.particulas.append(Particula(
                x,
                y,
                math.cos(ang) * vel,
                math.sin(ang) * vel,
                random.uniform(0.35, 0.60),
                random.choice((TURQUESA_ANIMA, (180, 255, 245), ORO_LITURGICO, BLANCO)),
                random.uniform(2.5, 5.0),
                gravedad=80.0,
            ))

    def consagracion_farol(self, x, y, tier=1):
        # Rayo de luz hacia arriba al activar farol
        cantidad = 14 + tier * 8
        colores = (TURQUESA_ANIMA, BLANCO, (160, 240, 235)) if tier == 1 else (
            ((120, 220, 255), ORO_LITURGICO, BLANCO, (255, 235, 160)) if tier == 2 else
            (ORO_LITURGICO, (255, 215, 80), TURQUESA_ANIMA, BLANCO, (240, 180, 255))
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

    def dibujar(self, surface, camara):
        for pluma in self.plumas:
            pluma.dibujar(surface, camara)
        for particula in self.particulas:
            particula.dibujar(surface, camara)
        for spark in self.sparks:
            spark.dibujar(surface, camara)
