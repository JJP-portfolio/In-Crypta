"""visual_demo.py — Test room de texturas y animaciones poeanas (v3 rediseño).
Técnicas aplicadas tras investigar fxin5429-oss/AI-generated-game (Dawn Leap):
  - Sprites por character art + palette (PAL), generacion 100% procedimental
  - Atlas de sprites agrupado para blit eficiente
  - anchored_blit: alineacion por bounding box de pixels no transparentes
  - Squash and stretch en salto y aterrizaje (peso y momentum)
  - Fondo procedural: gradiente, estrellas, nubes, colinas
  - Particulas con alpha suave
Solo primitivas pygame.draw + pygame.Surface. Sin imagenes externas.
"""
import math
import random
import sys

import pygame
from pygame.locals import *

ANCHO, ALTO = 960, 540
FPS = 60
TILE = 32

NEGRO = (8, 6, 10)
GRIS_OSCURO = (34, 30, 38)
PURPURA = (38, 22, 38)
VERDE_MUSGO = (52, 72, 60)
BLANCO_HUESO = (212, 202, 182)
ROJO_SANGRE = (124, 28, 38)
ORO_VELA = (210, 170, 70)
AMARILLO_LUZ = (240, 210, 150)
GRIS_CENIZA = (94, 88, 94)
MARRON_PODRE = (78, 58, 46)
AZUL_OSCURO = (52, 66, 92)
GRIS_PIEDRA = (72, 74, 84)

FONDOS = {
    "camposanto": ((6, 8, 16), (18, 26, 38)),
    "cripta": ((12, 8, 14), (28, 18, 24)),
    "osario": ((14, 6, 8), (38, 16, 18)),
}


def degradado_vertical(surface, arriba, abajo):
    for y in range(ALTO):
        p = y / ALTO
        color = tuple(int(arriba[i] + (abajo[i] - abajo[i]) * p) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (ANCHO, y))


def luna(surface, x, y, r):
    pygame.draw.circle(surface, (150, 144, 130), (x, y), r)
    pygame.draw.circle(surface, NEGRO, (x - r // 3, y - r // 3), r // 3)


class Camara:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.sacudida_t = 0.0
        self.sacudida_f = 0.0
        self.offset = (0.0, 0.0)

    def actualizar(self, objetivo, nivel_ancho, nivel_alto, dt):
        tx = objetivo.centerx - ANCHO // 2
        ty = objetivo.centery - ALTO // 2
        f = min(1.0, 7.0 * dt)
        self.x += (tx - self.x) * f
        self.y += (ty - self.y) * f
        mx = max(0, nivel_ancho - ANCHO)
        my = max(0, nivel_alto - ALTO)
        self.x = max(0.0, min(self.x, mx))
        self.y = max(0.0, min(self.y, my))
        self._actualizar_sacudida(dt)

    def sacudir(self, fuerza=5.0, dur=0.14):
        self.sacudida_t = max(self.sacudida_t, dur)
        self.sacudida_f = max(self.sacudida_f, fuerza)

    def _actualizar_sacudida(self, dt):
        if self.sacudida_t <= 0:
            self.offset = (0.0, 0.0)
            return
        self.sacudida_t = max(0.0, self.sacudida_t - dt)
        intensidad = self.sacudida_f * (self.sacudida_t / 0.14)
        self.offset = (random.uniform(-intensidad, intensidad),
                       random.uniform(-intensidad, intensidad))

    def aplicar_rect(self, rect):
        ox, oy = self.offset
        return pygame.Rect(
            round(rect.x - self.x + ox),
            round(rect.y - self.y + oy),
            rect.width,
            rect.height,
        )

    def en_pantalla(self, rect, margen=64):
        return (
            rect.right >= self.x - margen
            and rect.left <= self.x + ANCHO + margen
            and rect.bottom >= self.y - margen
            and rect.top <= self.y + ALTO + margen
        )
