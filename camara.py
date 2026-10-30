# ============================================================
# camara.py — Cámara con seguimiento y sacudida
# ============================================================
# La cámara guarda cuánto hay que restar a las coordenadas del mundo
# para dibujarlas en pantalla. El HUD NO usa la cámara.
# ============================================================

import random

import pygame

from config import ALTO, ANCHO, CAMARA_SUAVIZADO, SACUDIDA_DURACION, SACUDIDA_FUERZA


# --- Clase Camara --- #
class Camara:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.sacudida_tiempo = 0.0
        self.sacudida_fuerza = 0.0

    # --- Función actualizar --- #
    def actualizar(self, jugador, nivel, dt):
        objetivo_x = jugador.rect.centerx - ANCHO // 2
        objetivo_y = jugador.rect.centery - ALTO // 2

        factor = min(1.0, CAMARA_SUAVIZADO * dt)
        self.x += (objetivo_x - self.x) * factor
        self.y += (objetivo_y - self.y) * factor

        max_x = max(0, nivel.ancho - ANCHO)
        max_y = max(0, nivel.alto - ALTO)
        self.x = max(0.0, min(self.x, max_x))
        self.y = max(0.0, min(self.y, max_y))

        if nivel.ancho < ANCHO:
            self.x = (nivel.ancho - ANCHO) / 2
        if nivel.alto < ALTO:
            self.y = (nivel.alto - ALTO) / 2

        self.actualizar_sacudida(dt)

    # --- Función sacudir --- #
    def sacudir(self, fuerza=SACUDIDA_FUERZA, duracion=SACUDIDA_DURACION):
        self.sacudida_tiempo = max(self.sacudida_tiempo, duracion)
        self.sacudida_fuerza = max(self.sacudida_fuerza, fuerza)

    # --- Función actualizar_sacudida --- #
    def actualizar_sacudida(self, dt):
        if self.sacudida_tiempo <= 0:
            self.offset_x = 0.0
            self.offset_y = 0.0
            return

        self.sacudida_tiempo = max(0.0, self.sacudida_tiempo - dt)
        intensidad = self.sacudida_fuerza * (self.sacudida_tiempo / SACUDIDA_DURACION)
        self.offset_x = random.uniform(-intensidad, intensidad)
        self.offset_y = random.uniform(-intensidad, intensidad)

    # --- Función aplicar_x / aplicar_y --- #
    def aplicar_x(self, x):
        return x - self.x + self.offset_x

    def aplicar_y(self, y):
        return y - self.y + self.offset_y

    # --- Función aplicar_rect --- #
    def aplicar_rect(self, rect):
        return pygame.Rect(
            round(rect.x - self.x + self.offset_x),
            round(rect.y - self.y + self.offset_y),
            rect.width,
            rect.height,
        )

    # --- Función is_on_screen --- #
    def is_on_screen(self, rect, margen=64):
        return (
            rect.right >= self.x - margen
            and rect.left <= self.x + ANCHO + margen
            and rect.bottom >= self.y - margen
            and rect.top <= self.y + ALTO + margen
        )
