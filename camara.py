#---- Importamos ----#
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


#---- Clase Camara ----#
class Camara:
    def __init__(self):
        # Posicion actual en el mundo
        self.x = 0.0
        self.y = 0.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        # Parametros de sacudida
        self.sacudida_tiempo = 0.0
        self.sacudida_fuerza = 0.0
        self.sacudida_dir_x = 0.0
        self.sacudida_dir_y = 0.0
        self.permitir_sacudida = True

    def actualizar(self, jugador, nivel, dt):
        # Seguimiento horizontal centrado en el jugador
        objetivo_x = jugador.rect.centerx - VIRTUAL_ANCHO // 2

        # Encuadre vertical segun la altura del nivel o los pisos
        if nivel.alto <= VIRTUAL_ALTO:
            objetivo_y = float(nivel.alto - VIRTUAL_ALTO)
        else:
            banda = VIRTUAL_ALTO
            num_pisos = max(1, nivel.alto // banda)
            piso_idx = int(jugador.rect.centery) // banda
            piso_idx = max(0, min(piso_idx, num_pisos - 1))

            base_piso_y = float(piso_idx * banda)
            margen_inf = 48
            margen_sup = 32
            min_cam_y = jugador.rect.bottom + margen_inf - VIRTUAL_ALTO
            max_cam_y = jugador.rect.top - margen_sup

            objetivo_y = base_piso_y
            if objetivo_y < min_cam_y:
                objetivo_y = min_cam_y
            if objetivo_y > max_cam_y:
                objetivo_y = max_cam_y

        # Suavizamos el movimiento de la camara
        factor_x = min(1.0, CAMARA_SUAVIZADO * dt)
        factor_y = min(1.0, max(CAMARA_SUAVIZADO, 14.0) * dt)
        self.x += (objetivo_x - self.x) * factor_x
        self.y += (objetivo_y - self.y) * factor_y

        # Limites del mapa
        max_x = max(0, nivel.ancho - VIRTUAL_ANCHO)
        max_y = max(0, nivel.alto - VIRTUAL_ALTO)
        self.x = max(0.0, min(self.x, max_x))
        self.y = max(0.0, min(self.y, max_y))

        # Ajuste en caidas pronunciadas para no perder al jugador
        if nivel.alto > VIRTUAL_ALTO:
            if self.y < jugador.rect.bottom - VIRTUAL_ALTO + 10:
                self.y = jugador.rect.bottom - VIRTUAL_ALTO + 10
            if self.y > jugador.rect.top - 10:
                self.y = jugador.rect.top - 10
            self.y = max(0.0, min(self.y, max_y))

        if nivel.ancho < VIRTUAL_ANCHO:
            self.x = (nivel.ancho - VIRTUAL_ANCHO) / 2
        if nivel.alto <= VIRTUAL_ALTO:
            self.y = float(nivel.alto - VIRTUAL_ALTO)

        self.actualizar_sacudida(dt)

    def sacudir(self, fuerza=SACUDIDA_FUERZA, duracion=SACUDIDA_DURACION, dir_x=0.0, dir_y=0.0):
        # Dispara la sacudida de pantalla si esta habilitada
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

    def actualizar_sacudida(self, dt):
        # Aplica el temblor aleatorio mientras dure el temporizador
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

    def aplicar_x(self, x):
        # Convierte coordenada x de mundo a pantalla
        return x - self.x + self.offset_x

    def aplicar_y(self, y):
        # Convierte coordenada y de mundo a pantalla
        return y - self.y + self.offset_y

    def aplicar_rect(self, rect):
        # Convierte un rectangulo de mundo a coordenadas de pantalla
        return pygame.Rect(
            round(rect.x - self.x + self.offset_x),
            round(rect.y - self.y + self.offset_y),
            rect.width,
            rect.height,
        )

    def is_on_screen(self, rect, margen=64):
        # Chequea si un objeto esta dentro de la vista actual
        return (
            rect.right >= self.x - margen
            and rect.left <= self.x + VIRTUAL_ANCHO + margen
            and rect.bottom >= self.y - margen
            and rect.top <= self.y + VIRTUAL_ALTO + margen
        )
