# ============================================================
# camara.py — Cámara con seguimiento y sacudida
# ============================================================
# La cámara guarda cuánto hay que restar a las coordenadas del mundo
# para dibujarlas en pantalla. El HUD NO usa la cámara.
# ============================================================

import math
import random

import pygame

from config import (
    ALTO,
    ANCHO,
    CAMARA_SUAVIZADO,
    SACUDIDA_DURACION,
    SACUDIDA_FUERZA,
    VIRTUAL_ALTO,
    VIRTUAL_ANCHO,
)


# --- Clase Camara --- #
class Camara:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.sacudida_tiempo = 0.0
        self.sacudida_fuerza = 0.0
        self.sacudida_dir_x = 0.0
        self.sacudida_dir_y = 0.0
        self.permitir_sacudida = True

    # --- Función actualizar --- #
    def actualizar(self, jugador, nivel, dt):
        objetivo_x = jugador.rect.centerx - VIRTUAL_ANCHO // 2

        # Encuadre vertical modular por bandas de piso (método de 18*TILE = VIRTUAL_ALTO).
        # Centra perfectamente cada nivel/piso entre su techo y su suelo, agnóstico
        # a cuántos pisos extras se agreguen arriba o abajo.
        if nivel.alto <= VIRTUAL_ALTO:
            objetivo_y = float(nivel.alto - VIRTUAL_ALTO)
        else:
            banda = VIRTUAL_ALTO
            num_pisos = max(1, nivel.alto // banda)
            piso_idx = int(jugador.rect.centery) // banda
            piso_idx = max(0, min(piso_idx, num_pisos - 1))

            # Base ideal del piso: sitúa el techo en Y=0 de la pantalla y el suelo abajo
            base_piso_y = float(piso_idx * banda)

            # Durante desplazamientos normales (correr, saltar), la cámara permanece
            # fija en la base del piso para mostrar techo y suelo perfectamente encuadrados.
            # Si el jugador cae por un pozo o fosa de transición vertical, la cámara lo
            # acompaña fluidamente asegurando que no se escape de la vista.
            margen_inf = 48
            margen_sup = 32
            min_cam_y = jugador.rect.bottom + margen_inf - VIRTUAL_ALTO
            max_cam_y = jugador.rect.top - margen_sup

            objetivo_y = base_piso_y
            if objetivo_y < min_cam_y:
                objetivo_y = min_cam_y
            if objetivo_y > max_cam_y:
                objetivo_y = max_cam_y

        factor_x = min(1.0, CAMARA_SUAVIZADO * dt)
        factor_y = min(1.0, max(CAMARA_SUAVIZADO, 14.0) * dt)
        self.x += (objetivo_x - self.x) * factor_x
        self.y += (objetivo_y - self.y) * factor_y

        max_x = max(0, nivel.ancho - VIRTUAL_ANCHO)
        max_y = max(0, nivel.alto - VIRTUAL_ALTO)
        self.x = max(0.0, min(self.x, max_x))
        self.y = max(0.0, min(self.y, max_y))

        # Garantía estricta de encuadre en caídas verticales extremas
        if nivel.alto > VIRTUAL_ALTO:
            if self.y < jugador.rect.bottom - VIRTUAL_ALTO + 10:
                self.y = jugador.rect.bottom - VIRTUAL_ALTO + 10
            if self.y > jugador.rect.top - 10:
                self.y = jugador.rect.top - 10
            self.y = max(0.0, min(self.y, max_y))

        if nivel.ancho < VIRTUAL_ANCHO:
            self.x = (nivel.ancho - VIRTUAL_ANCHO) / 2
        # Si el nivel es más bajo que la altura de la vista, anclar el suelo abajo
        # para que no haya vacío negro debajo del piso y se aprecie el fondo gótico
        if nivel.alto <= VIRTUAL_ALTO:
            self.y = float(nivel.alto - VIRTUAL_ALTO)

        self.actualizar_sacudida(dt)

    # --- Función sacudir --- #
    def sacudir(self, fuerza=SACUDIDA_FUERZA, duracion=SACUDIDA_DURACION, dir_x=0.0, dir_y=0.0):
        if not self.permitir_sacudida:
            self.offset_x = 0.0
            self.offset_y = 0.0
            self.sacudida_dir_x = 0.0
            self.sacudida_dir_y = 0.0
            return
        self.sacudida_tiempo = max(self.sacudida_tiempo, duracion)
        self.sacudida_fuerza = max(self.sacudida_fuerza, fuerza)
        mag = math.hypot(dir_x, dir_y)
        if mag > 0.001:
            self.sacudida_dir_x = dir_x / mag
            self.sacudida_dir_y = dir_y / mag
        else:
            self.sacudida_dir_x = 0.0
            self.sacudida_dir_y = 0.0

    # --- Función actualizar_sacudida --- #
    def actualizar_sacudida(self, dt):
        if self.sacudida_tiempo <= 0:
            self.offset_x = 0.0
            self.offset_y = 0.0
            self.sacudida_dir_x = 0.0
            self.sacudida_dir_y = 0.0
            return

        self.sacudida_tiempo = max(0.0, self.sacudida_tiempo - dt)
        intensidad = self.sacudida_fuerza * (self.sacudida_tiempo / SACUDIDA_DURACION)
        if self.sacudida_dir_x != 0.0 or self.sacudida_dir_y != 0.0:
            oscilacion = random.uniform(-intensidad, intensidad)
            self.offset_x = self.sacudida_dir_x * oscilacion
            self.offset_y = self.sacudida_dir_y * oscilacion
        else:
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
            and rect.left <= self.x + VIRTUAL_ANCHO + margen
            and rect.bottom >= self.y - margen
            and rect.top <= self.y + VIRTUAL_ALTO + margen
        )
