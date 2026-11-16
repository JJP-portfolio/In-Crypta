#---- Importamos librerias y configuracion ----#
import math
import random

import pygame

from config import (
    ALTO,
    ANCHO,
    HUD_BORDE,
    HUD_ORO,
    TILE,
    VIRTUAL_ALTO,
    VIRTUAL_ANCHO,
)

#---- Caches de iluminacion y atmosferas ----#
_CACHE_LUCES_JUEGO = {}
_CACHE_HAZ_LUNAR = None


def _obtener_luz_perforacion(radio):
    clave = ("sub", radio)
    surf = _CACHE_LUCES_JUEGO.get(clave)
    if surf is None:
        surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        for r in range(radio, 0, -1):
            norm = r / radio
            factor = max(0.0, (1.0 - norm * norm) ** 2.0)
            alfa = int(45 * factor)
            pygame.draw.circle(surf, (0, 0, 0, alfa), (radio, radio), r)
        _CACHE_LUCES_JUEGO[clave] = surf
    return surf


def _obtener_luz_calida(radio, color=(240, 196, 90), factor_mult=0.14):
    clave = ("add", radio, tuple(color), factor_mult)
    surf = _CACHE_LUCES_JUEGO.get(clave)
    if surf is None:
        surf = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        cr, cg, cb = color
        for r in range(radio, 0, -1):
            norm = r / radio
            factor = max(0.0, (1.0 - norm * norm) ** 2.0)
            pygame.draw.circle(
                surf,
                (
                    int(cr * factor * factor_mult),
                    int(cg * factor * factor_mult),
                    int(cb * factor * factor_mult),
                ),
                (radio, radio),
                r,
            )
        _CACHE_LUCES_JUEGO[clave] = surf
    return surf


def _obtener_haz_lunar(h):
    """Caché de haz diagonal de luz lunar volumétrica y translúcida proyectada desde ventanales góticos."""
    global _CACHE_HAZ_LUNAR
    if _CACHE_HAZ_LUNAR is None or _CACHE_HAZ_LUNAR.get_height() != h:
        w_surf = 190
        surf = pygame.Surface((w_surf, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        base_color = (135, 185, 235)
        num_capas = 16
        for i in range(num_capas, 0, -1):
            t = i / float(num_capas)
            top_w = 44 * t
            bot_w = 120 * t
            top_cx = 36
            bot_cx = 125

            alfa_capa = int(22 * (1.0 - t * t))
            if alfa_capa <= 0:
                continue
            pts = [
                (int(top_cx - top_w // 2), 0),
                (int(top_cx + top_w // 2), 0),
                (int(bot_cx + bot_w // 2), h),
                (int(bot_cx - bot_w // 2), h),
            ]
            pygame.draw.polygon(surf, (*base_color, alfa_capa), pts)

        fade = pygame.Surface((w_surf, h), pygame.SRCALPHA)
        for y in range(0, h, 6):
            norm_y = y / float(h)
            fade_a = int(255 * (1.0 - norm_y * 0.78))
            pygame.draw.rect(fade, (255, 255, 255, fade_a), (0, y, w_surf, 6))
        surf.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        _CACHE_HAZ_LUNAR = surf.convert_alpha()
    return _CACHE_HAZ_LUNAR


#---- Particula ambiental por bioma ----#
class ParticulaBioma:
    """Partícula ambiental ligera reciclada en pantalla (máx 25, 60 FPS cero lag)."""

    def __init__(self, pantalla_w=VIRTUAL_ANCHO, pantalla_h=VIRTUAL_ALTO, tema="camposanto"):
        self.w = pantalla_w
        self.h = pantalla_h
        self.tema = tema
        self.reset(random_y=True)

    def reset(self, random_y=False):
        self.x = random.uniform(0, self.w)
        self.fase = random.uniform(0, math.tau)
        self.fase_vel = random.uniform(1.2, 2.5)
        if self.tema == "camposanto":
            self._reset_camposanto(random_y)
        elif self.tema == "cripta":
            self._reset_cripta(random_y)
        else:
            self._reset_osario(random_y)

    def _reset_camposanto(self, random_y):
        self.tipo = "fatuo" if random.random() < 0.6 else "niebla"
        if self.tipo == "fatuo":
            self.y = random.uniform(0, self.h) if random_y else self.h + random.uniform(2, 10)
            self.vx = random.uniform(-10, 10)
            self.vy = random.uniform(-18, -32)
            self.tamano = random.uniform(1.5, 3.0)
            colores = ((70, 235, 220), (140, 240, 255), (90, 190, 220))
            self.color = random.choice(colores)
            self.alfa = random.randint(80, 160)
            return
        self.y = (
            random.uniform(self.h - 50, self.h - 4)
            if random_y
            else self.h - random.uniform(4, 45)
        )
        self.vx = random.uniform(15, 35)
        self.vy = random.uniform(-2, 2)
        self.tamano = random.uniform(8.0, 16.0)
        self.color = (35, 55, 75)
        self.alfa = random.randint(30, 65)

    def _reset_cripta(self, random_y):
        self.tipo = "polvo"
        self.y = (
            random.uniform(0, self.h)
            if random_y
            else (0 if random.random() < 0.5 else self.h)
        )
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-6, 6)
        self.tamano = random.uniform(1.2, 2.4)
        self.color = random.choice(((210, 215, 225), (180, 185, 200), (235, 240, 250)))
        self.alfa = random.randint(70, 150)

    def _reset_osario(self, random_y):
        self.tipo = "brasa" if random.random() < 0.55 else "ceniza"
        self.y = random.uniform(0, self.h) if random_y else self.h + random.uniform(2, 15)
        self.vx = random.uniform(-15, 15)
        if self.tipo == "brasa":
            self.vy = random.uniform(-35, -65)
            self.tamano = random.uniform(1.8, 3.2)
            colores = ((255, 80, 40), (255, 140, 50), (220, 50, 50), (255, 210, 80))
            self.color = random.choice(colores)
            self.alfa = random.randint(110, 210)
            return
        self.vy = random.uniform(-20, -45)
        self.tamano = random.uniform(1.4, 2.5)
        self.color = random.choice(((190, 175, 160), (140, 130, 125), (210, 200, 190)))
        self.alfa = random.randint(70, 140)

    def actualizar(self, dt, intensificar=False):
        self.fase += self.fase_vel * dt
        mult_vel = 1.6 if intensificar else 1.0

        if self.tipo == "niebla":
            self.x += self.vx * dt
            self.y += math.sin(self.fase) * 4.0 * dt
        elif self.tipo == "fatuo":
            self.x += (self.vx + math.sin(self.fase) * 12.0) * dt
            self.y += self.vy * dt
        elif self.tipo == "polvo":
            self.x += (self.vx + math.sin(self.fase) * 8.0) * dt
            self.y += (self.vy + math.cos(self.fase * 0.8) * 6.0) * dt
        else:
            self.x += (self.vx + math.sin(self.fase) * 14.0) * dt
            self.y += self.vy * mult_vel * dt

        if self.y < -15 or self.y > self.h + 15 or self.x < -25 or self.x > self.w + 25:
            self.reset(random_y=False)

    def dibujar(self, surface):
        px = int(self.x)
        py = int(self.y)
        if px < -20 or px > self.w + 20 or py < -20 or py > self.h + 20:
            return

        if self.tipo == "niebla":
            w_n = int(self.tamano * 2)
            h_n = int(self.tamano)
            s_niebla = pygame.Surface((w_n, h_n), pygame.SRCALPHA)
            pygame.draw.ellipse(s_niebla, (*self.color, self.alfa), (0, 0, w_n, h_n))
            surface.blit(s_niebla, (px - w_n // 2, py - h_n // 2))
        elif self.tipo == "fatuo":
            pygame.draw.circle(surface, self.color, (px, py), int(self.tamano))
            pygame.draw.circle(surface, (255, 255, 255), (px, py), max(1, int(self.tamano * 0.5)))
        elif self.tipo == "brasa":
            pygame.draw.circle(surface, self.color, (px, py), int(self.tamano))
            if self.tamano > 2.0:
                pygame.draw.circle(surface, (255, 240, 180), (px, py), 1)
        else:
            pygame.draw.circle(surface, self.color, (px, py), max(1, int(self.tamano)))


#---- Mixin de fondos y atmosfera ----#
class FondosMixin:
    """Generacion y dibujo de fondos paralaje, vinetas, scanlines y particulas."""

    def reiniciar_particulas_bioma(self, tema="camposanto"):
        """Inicializa o recicla las partículas ambientales según la calidad gráfica (60 FPS sin lag)."""
        if getattr(self, "config_calidad_idx", 0) == 2:
            self.particulas_bioma = []
        elif getattr(self, "config_calidad_idx", 0) == 1:
            self.particulas_bioma = [ParticulaBioma(VIRTUAL_ANCHO, VIRTUAL_ALTO, tema) for _ in range(12)]
        else:
            self.particulas_bioma = [ParticulaBioma(VIRTUAL_ANCHO, VIRTUAL_ALTO, tema) for _ in range(25)]

    def _crear_scanlines_goticas(self, ancho, alto):
        surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        for y in range(0, alto, 3):
            pygame.draw.line(surf, (4, 3, 8, 16), (0, y), (ancho, y), 1)
        return surf

    def crear_fondo(self, tema, w=ANCHO, h=ALTO):
        fondo = pygame.Surface((w, h))
        if tema == "cripta":
            arriba, abajo = (6, 5, 10), (16, 14, 20)
        elif tema == "osario":
            arriba, abajo = (9, 5, 8), (22, 10, 14)
        else:
            arriba, abajo = (9, 12, 22), (18, 26, 40)

        for y in range(h):
            proporcion = y / h
            color = tuple(
                int(arriba[i] + (abajo[i] - arriba[i]) * proporcion)
                for i in range(3)
            )
            pygame.draw.line(fondo, color, (0, y), (w, y))

        if tema == "cripta":
            vx = int(w * 0.68)
            pygame.draw.rect(fondo, (16, 15, 22), (vx, 40, 150, 230))
            pygame.draw.arc(fondo, (52, 50, 60), (vx - 10, 10, 170, 110), 0, math.pi, 8)
            pygame.draw.rect(fondo, (40, 52, 58), (vx + 16, 74, 118, 178))
            for x in range(vx + 26, vx + 130, 26):
                pygame.draw.line(fondo, (20, 25, 30), (x, 80), (x, 248), 3)
            pygame.draw.line(fondo, (20, 25, 30), (vx + 16, 166), (vx + 134, 166), 3)
            pygame.draw.arc(fondo, (42, 58, 62), (vx + 10, 48, 130, 70), 0, math.pi, 4)
        elif tema == "osario":
            cx = int(w * 0.76)
            pygame.draw.circle(fondo, (40, 12, 16), (cx, 120), 80)
            pygame.draw.circle(fondo, (68, 18, 24), (cx, 120), 54)
            pygame.draw.circle(fondo, (108, 34, 28), (cx, 120), 28)
        return fondo

    def crear_vineta(self, fuerza):
        vineta = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        small_w, small_h = 160, 90
        small = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
        cx, cy = small_w / 2, small_h / 2
        for y in range(small_h):
            for x in range(small_w):
                dx = (x - cx) / (cx * 0.88)
                dy = (y - cy) / (cy * 0.82)
                dist = math.hypot(dx, dy)
                if dist > 0.65:
                    factor = min(1.0, (dist - 0.65) / 0.60)
                    alfa = int(fuerza * (factor ** 2))
                    small.set_at((x, y), (0, 0, 0, min(255, alfa)))
        pygame.transform.smoothscale(small, (ANCHO, ALTO), vineta)
        return vineta

    def crear_vineta_carmesi(self):
        vineta = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        small_w, small_h = 160, 90
        small = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
        cx, cy = small_w / 2, small_h / 2
        for y in range(small_h):
            for x in range(small_w):
                dx = (x - cx) / (cx * 0.90)
                dy = (y - cy) / (cy * 0.85)
                dist = math.hypot(dx, dy)
                if dist > 0.70:
                    factor = min(1.0, (dist - 0.70) / 0.50)
                    alfa = int(70 * (factor ** 2))
                    small.set_at((x, y), (112, 22, 34, min(255, alfa)))
        pygame.transform.smoothscale(small, (ANCHO, ALTO), vineta)
        return vineta

    def dibujar_marco_heraldico(self, destino, x, y, ancho, alto, color_fondo=(14, 11, 20, 235), color_borde=None):
        """Marco heráldico gótico consistente con esquinas doradas."""
        borde_oro = HUD_ORO
        borde_linea = color_borde if color_borde is not None else (*HUD_BORDE, 200)
        panel = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(panel, color_fondo, (0, 0, ancho, alto), border_radius=12)
        pygame.draw.rect(panel, borde_linea, (0, 0, ancho, alto), 1, border_radius=12)
        pygame.draw.rect(panel, (198, 162, 82, 180), (2, 2, ancho - 4, alto - 4), 1, border_radius=10)
        pygame.draw.line(panel, (*borde_oro, 140), (16, 1), (ancho - 16, 1), 1)
        pygame.draw.line(panel, (*borde_oro, 140), (16, alto - 1), (ancho - 16, alto - 1), 1)
        destino.blit(panel, (x, y))

    def dibujar_fondo(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w = destino.get_width()
        h = destino.get_height()
        tema = self.nivel.tema if self.nivel else "camposanto"

        if self.nivel and getattr(self.nivel, "num_filas", 18) > 18:
            cam = getattr(self, "camara", None)
            if cam and cam.y >= 288:
                tema = "cripta" if self.nivel.tema != "osario" else "osario"

        clave = (tema, w, h)
        if clave not in self.fondos:
            self.fondos[clave] = self.crear_fondo(tema, w, h)
        destino.blit(self.fondos[clave], (0, 0))

        if tema == "camposanto":
            self.dibujar_fondo_camposanto(destino)
        elif tema == "cripta":
            self.dibujar_fondo_cripta(destino)
        else:
            self.dibujar_fondo_osario(destino)

        self.dibujar_niebla(destino, tema)

    def _camposanto_cielo(self, destino, w, h, calidad):
        luna_x = int(w * 0.68) - int(self.camara.x * 0.04)
        luna_y = 72
        if calidad != 2:
            halo_luna = pygame.Surface((160, 160), pygame.SRCALPHA)
            for r in range(76, 20, -4):
                norm = (r - 20) / 56.0
                a = int(24 * (1.0 - norm * norm))
                pygame.draw.circle(halo_luna, (210, 215, 175, a), (80, 80), r)
            destino.blit(halo_luna, (luna_x - 80, luna_y - 80))
        pygame.draw.circle(destino, (236, 230, 196), (luna_x, luna_y), 26)
        pygame.draw.circle(destino, (218, 210, 174), (luna_x + 6, luna_y - 4), 8)

        estrellas = [
            (60, 42), (140, 20), (220, 56), (310, 28), (410, 44),
            (500, 16), (590, 38), (680, 22), (770, 50), (860, 32),
            (940, 18), (1010, 44), (90, 70), (270, 62), (460, 55),
            (640, 75), (820, 65), (980, 80),
        ]
        ox = int(self.camara.x * 0.06) % w
        for sx, sy in estrellas:
            px = (sx - ox) % w
            pygame.draw.circle(destino, (220, 218, 200), (px, sy), 1)

        hill_w = 300
        offset_h = int(self.camara.x * 0.18) % hill_w
        for i in range(-1, int(w / hill_w) + 2):
            bx = i * hill_w - offset_h
            pygame.draw.polygon(
                destino,
                (15, 22, 34),
                [(bx, h), (bx + 150, int(h * 0.52) + 32), (bx + 300, h)],
            )
            pygame.draw.polygon(
                destino,
                (20, 28, 42),
                [(bx + 75, h), (bx + 195, int(h * 0.58) + 32), (bx + 320, h)],
            )

    def _camposanto_rejas_y_siluetas(self, destino, w, h, calidad):
        if calidad in (0, 1):
            fence_w = 240
            offset_f = int(self.camara.x * 0.28) % fence_w
            col_hierro = (18, 22, 32)
            for i in range(-1, int(w / fence_w) + 2):
                fx = i * fence_w - offset_f
                fy_base = h - 52
                pygame.draw.line(
                    destino, col_hierro, (fx, fy_base - 14), (fx + fence_w, fy_base - 14), 2
                )
                pygame.draw.line(
                    destino, col_hierro, (fx, fy_base - 32), (fx + fence_w, fy_base - 32), 2
                )
                for bx in range(fx + 10, fx + fence_w, 20):
                    pygame.draw.line(destino, col_hierro, (bx, fy_base), (bx, fy_base - 38), 2)
                    punta = [(bx - 2, fy_base - 38), (bx + 2, fy_base - 38), (bx, fy_base - 44)]
                    pygame.draw.polygon(destino, col_hierro, punta)
                if i % 2 == 0:
                    cx, cy = fx + 70, fy_base - 22
                    pygame.draw.line(destino, (24, 28, 40), (cx - 4, cy + 18), (cx + 3, cy - 24), 3)
                    pygame.draw.line(destino, (24, 28, 40), (cx - 10, cy - 8), (cx + 9, cy - 5), 3)

        elem_w = 190
        offset_e = int(self.camara.x * 0.38) % elem_w
        for i in range(-1, int(w / elem_w) + 2):
            ex = i * elem_w - offset_e
            idx_mundo = int((self.camara.x * 0.38 + ex) // elem_w)
            if idx_mundo % 2 == 0:
                escala = 0.95 + ((idx_mundo * 7) % 3) * 0.15
                self.dibujar_arbol_muerto(destino, ex + 40, h - 60, escala)
            else:
                escala = 0.85 + ((idx_mundo * 5) % 3) * 0.12
                self.dibujar_tumba_lejana(destino, ex + 60, h - 44, escala)

    def dibujar_fondo_camposanto(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        calidad = getattr(self, "config_calidad_idx", 0)
        self._camposanto_cielo(destino, w, h, calidad)
        self._camposanto_rejas_y_siluetas(destino, w, h, calidad)

    def dibujar_arbol_muerto(self, destino, x, base_y, escala):
        alto = int(150 * escala)
        color = (16, 20, 30)
        pygame.draw.polygon(
            destino,
            color,
            [
                (x - 8 * escala, base_y),
                (x - 3 * escala, base_y - alto),
                (x + 5 * escala, base_y - alto),
                (x + 10 * escala, base_y),
            ],
        )
        for dx, dy, largo in ((-4, -0.55, 54), (3, -0.72, 66), (-1, -0.88, 44)):
            inicio = (x + dx * escala, base_y - alto * (-dy))
            pygame.draw.line(
                destino,
                color,
                inicio,
                (inicio[0] - largo * escala, inicio[1] - 26 * escala),
                max(2, int(4 * escala)),
            )

    def dibujar_tumba_lejana(self, destino, x, base_y, escala):
        ancho = int(32 * escala)
        alto = int(48 * escala)
        c_muro = (16, 22, 32)
        c_marco = (10, 14, 22)
        pygame.draw.rect(destino, c_muro, (x, base_y - alto, ancho, alto), border_radius=2)
        puntos_techo = [
            (x - 2, base_y - alto),
            (x + ancho + 2, base_y - alto),
            (x + ancho // 2, base_y - alto - int(18 * escala)),
        ]
        pygame.draw.polygon(destino, c_muro, puntos_techo)
        pygame.draw.polygon(destino, c_marco, puntos_techo, 1)
        r_rose = max(2, int(6 * escala))
        rose_cy = base_y - alto - int(6 * escala)
        pygame.draw.circle(destino, (8, 10, 16), (x + ancho // 2, rose_cy), r_rose)
        pygame.draw.circle(destino, (24, 32, 46), (x + ancho // 2, rose_cy), r_rose, 1)
        puerta_w = int(14 * escala)
        puerta_h = int(22 * escala)
        px = x + (ancho - puerta_w) // 2
        py = base_y - puerta_h
        pygame.draw.rect(destino, (8, 10, 16), (px, py, puerta_w, puerta_h))
        pygame.draw.arc(destino, (24, 32, 46), (px, py - int(6 * escala), puerta_w, int(12 * escala)), 0.0, 3.14, 1)

    def _cripta_ventanales(self, destino, w, h, calidad):
        win_w = 320
        offset_w = int(self.camara.x * 0.18) % win_w
        haz_lunar = _obtener_haz_lunar(h) if calidad != 2 else None
        for i in range(-1, int(w / win_w) + 2):
            wx = i * win_w - offset_w + 80
            wy, ww, wh = 24, 38, 86
            pygame.draw.rect(destino, (14, 13, 20), (wx - 2, wy + 16, ww + 4, wh - 16))
            pygame.draw.arc(destino, (14, 13, 20), (wx - 2, wy, ww + 4, 36), 0.0, 3.14, 3)
            pygame.draw.rect(destino, (22, 30, 44), (wx, wy + 18, ww, wh - 18))
            pygame.draw.arc(destino, (22, 30, 44), (wx, wy + 2, ww, 34), 0.0, 3.14, 2)
            pygame.draw.line(
                destino, (15, 18, 26), (wx + ww // 2, wy + 6), (wx + ww // 2, wy + wh), 1
            )
            pygame.draw.line(destino, (15, 18, 26), (wx, wy + 42), (wx + ww, wy + 42), 1)
            pygame.draw.circle(destino, (14, 13, 20), (wx + ww // 2, wy + 16), 6)
            pygame.draw.circle(destino, (24, 32, 48), (wx + ww // 2, wy + 16), 6, 1)
            if haz_lunar is not None:
                destino.blit(haz_lunar, (wx - 10, wy + 10))

    def _cripta_columnas_y_cadenas(self, destino, w, h, calidad):
        col_w = 230
        offset_c = int(self.camara.x * 0.28) % col_w
        if calidad in (0, 1):
            for i in range(-1, int(w / col_w) + 2):
                x = i * col_w - offset_c
                rect_arco = pygame.Rect(x + 27, 80, col_w, 140)
                pygame.draw.arc(destino, (20, 18, 26), rect_arco, 0.0, 3.14, 3)
                cx = x + 27 + col_w // 2
                pygame.draw.line(destino, (17, 16, 23), (cx, 80), (cx, 150), 2)

        for i in range(-1, int(w / col_w) + 2):
            x = i * col_w - offset_c
            pygame.draw.rect(destino, (15, 14, 22), (x, 162, 54, h - 162))
            pygame.draw.rect(destino, (24, 23, 30), (x + 6, 168, 42, h - 168), 2)
            pygame.draw.rect(destino, (16, 15, 20), (x - 8, 152, 70, 14))
            pygame.draw.rect(destino, (16, 15, 20), (x - 4, 136, 62, 10))
            for y in range(192, h, 48):
                pygame.draw.line(destino, (20, 19, 28), (x + 8, y), (x + 46, y), 1)

    def _cripta_cadenas_y_antorchas(self, destino, w, h, calidad):
        chain_w = 280
        offset_ch = int(self.camara.x * 0.40) % chain_w
        for i in range(-1, int(w / chain_w) + 2):
            x = i * chain_w - offset_ch + 60
            largo = 100 + ((i * 37) % 60)
            for y in range(0, largo, 12):
                pygame.draw.ellipse(destino, (28, 28, 36), (x - 3, y, 6, 12), 1)
            if calidad in (0, 1) and (i % 2 == 0):
                cy = largo
                pygame.draw.line(destino, (38, 36, 44), (x - 14, cy), (x + 14, cy), 3)
                pygame.draw.line(destino, (38, 36, 44), (x - 14, cy), (x - 14, cy - 6), 2)
                pygame.draw.line(destino, (38, 36, 44), (x + 14, cy), (x + 14, cy - 6), 2)
                pygame.draw.circle(destino, (255, 180, 60), (x - 14, cy - 8), 2)
                pygame.draw.circle(destino, (255, 180, 60), (x + 14, cy - 8), 2)

        torch_w = 360
        offset_t = int(self.camara.x * 0.48) % torch_w
        for i in range(-1, int(w / torch_w) + 2):
            x = i * torch_w - offset_t + 110
            base_y = h - 160
            if calidad == 2:
                pygame.draw.circle(destino, (255, 180, 60), (x, base_y), 3)
                continue
            halo_vela = pygame.Surface((44, 44), pygame.SRCALPHA)
            for r in range(20, 2, -2):
                norm = r / 20.0
                a = int(28 * (1.0 - norm * norm))
                pygame.draw.circle(halo_vela, (255, 180, 60, a), (22, 22), r)
            destino.blit(halo_vela, (x - 22, base_y - 22))

    def dibujar_fondo_cripta(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        calidad = getattr(self, "config_calidad_idx", 0)
        self._cripta_ventanales(destino, w, h, calidad)
        self._cripta_columnas_y_cadenas(destino, w, h, calidad)
        self._cripta_cadenas_y_antorchas(destino, w, h, calidad)

    def _osario_arcos_y_pilares(self, destino, w, h, calidad, offset_y_arc):
        arc_w = 300
        offset_a = int(self.camara.x * 0.22) % arc_w
        for i in range(-1, int(w / arc_w) + 2):
            x = i * arc_w - offset_a
            pygame.draw.arc(
                destino, (36, 22, 24), (x, 182 - offset_y_arc, 280, 320), 3.14, 6.28, 9
            )
            pygame.draw.arc(
                destino, (28, 18, 20), (x + 40, 222 - offset_y_arc, 220, 280), 3.14, 6.28, 5
            )
        if calidad not in (0, 1):
            return
        skull_col_w = 340
        offset_sc = int(self.camara.x * 0.30) % skull_col_w
        for i in range(-1, int(w / skull_col_w) + 2):
            sx = i * skull_col_w - offset_sc + 40
            pygame.draw.rect(
                destino,
                (28, 18, 20),
                (sx - 10, 120 - offset_y_arc, 20, h - 120 + offset_y_arc),
            )
            for sy in range(130, h - 40, 32):
                pygame.draw.circle(destino, (48, 34, 34), (sx, sy - offset_y_arc), 9)
                pygame.draw.circle(destino, (18, 10, 12), (sx - 3, sy - 1 - offset_y_arc), 2)
                pygame.draw.circle(destino, (18, 10, 12), (sx + 3, sy - 1 - offset_y_arc), 2)
                pygame.draw.line(
                    destino,
                    (18, 10, 12),
                    (sx - 3, sy + 4 - offset_y_arc),
                    (sx + 3, sy + 4 - offset_y_arc),
                    1,
                )

    def _osario_cadenas_brasas_y_velo(self, destino, w, h, calidad, tiempo, cam_y):
        offset_y_chain = int(cam_y * 0.26)
        chain_w = 260
        offset_ch = int(self.camara.x * 0.38) % chain_w
        for i in range(-1, int(w / chain_w) + 2):
            x = i * chain_w - offset_ch + 50
            largo = 120 + ((i * 43) % 70)
            p_fin = (x + 8, largo - offset_y_chain)
            pygame.draw.line(destino, (26, 18, 20), (x, -offset_y_chain), p_fin, 5)
            pygame.draw.line(
                destino, (26, 18, 20), p_fin, (x - 12, largo + 24 - offset_y_chain), 3
            )
        if calidad in (0, 1):
            for idx in range(18):
                fase = (tiempo * 0.6 + idx * 0.37) % 1.0
                em_x = int((idx * 73 + self.camara.x * 0.45) % w)
                em_y = int(h - 30 - fase * (h * 0.65))
                rad = 1 if idx % 3 == 0 else 2
                col = (230, 80, 40) if idx % 2 == 0 else (255, 140, 50)
                pygame.draw.circle(destino, col, (em_x, em_y), rad)

        if self.nivel and getattr(self.nivel, "num_filas", 18) > 18 and cam_y < 320:
            x_abismo = int(308 * TILE - self.camara.x)
            if x_abismo < w:
                x_ini = max(0, x_abismo - 32)
                ancho_velo = w - x_ini
                velo = pygame.Surface((ancho_velo, h - 32), pygame.SRCALPHA)
                for vx in range(ancho_velo):
                    mundo_dx = (x_ini + vx) - x_abismo
                    if mundo_dx < 0:
                        alfa_x = int(238 * ((mundo_dx + 32) / 32.0))
                    else:
                        alfa_x = min(246, 238 + int(8 * min(1.0, mundo_dx / 96.0)))
                    pygame.draw.line(
                        velo, (4, 2, 6, max(0, alfa_x)), (vx, 0), (vx, h - 32)
                    )
                destino.blit(velo, (x_ini, 32))

    def dibujar_fondo_osario(self, destino=None):
        if destino is None:
            destino = self.pantalla
        w, h = destino.get_width(), destino.get_height()
        calidad = getattr(self, "config_calidad_idx", 0)
        tiempo = pygame.time.get_ticks() / 1000.0
        cam_y = getattr(self.camara, "y", 0.0)
        self._osario_arcos_y_pilares(destino, w, h, calidad, int(cam_y * 0.16))
        self._osario_cadenas_brasas_y_velo(destino, w, h, calidad, tiempo, cam_y)

    def dibujar_niebla(self, destino=None, tema="camposanto"):
        if destino is None:
            destino = self.pantalla
        if getattr(self, "config_calidad_idx", 0) == 2:
            return
        w, h = destino.get_width(), destino.get_height()
        color = (25, 38, 50) if tema != "osario" else (32, 16, 20)
        alto_niebla = 64
        niebla = pygame.Surface((w, alto_niebla), pygame.SRCALPHA)
        for i in range(alto_niebla):
            alfa = int(20 * (i / alto_niebla))
            pygame.draw.line(niebla, (*color, alfa), (0, i), (w, i))
        destino.blit(niebla, (0, h - alto_niebla))
