#---- Importamos librerias y configuracion ----#
import math

import pygame

from actores.utilidades import _escalar_rect_visual_enemigo, limitar
import config
from config import (
    BLANCO,
    CARMESÍ_SANGRE,
    ENEMIGO_MORTAJA,
    ENEMIGO_OJO_FUEGO,
    ENEMIGO_PURPURA,
    ENEMIGO_RIM_LUZ,
    FX_IMPACTO_BLANCO,
    HUESO,
    HUESO_MARFIL,
    MARFIL_XILOGRAFICO,
    MELEE_ACERO_CLARO,
    NEGRO,
    NEGRO_NOCHE,
    ROJO,
    TURQUESA_ÁNIMA,
    VELOCIDAD_ENEMIGO,
    resolver_estilo,
)
from particulas import ParticulaPluma


#---- Clase EntidadPatrullera ----#
class EntidadPatrullera:
    """Clase base para criaturas que patrullan horizontalmente con rebote contra límites."""

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
        self.tiempo_flash = 0.0

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True
        self.tiempo_flash = 0.0

    def actualizar_flash(self, dt):
        """Reduce el temporizador de damage flash si está activo."""
        if getattr(self, "tiempo_flash", 0.0) > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)

    def avanzar_patrulla(self, dt, velocidad):
        """Cinemática de patrulla horizontal con rebote contra límites y clamping."""
        self.x += self.direccion * velocidad * dt
        self.rect.x = round(self.x)

        if self.rect.left <= self.minimo_x:
            self.rect.left = self.minimo_x
            self.x = float(self.rect.x)
            self.direccion = 1
        elif self.rect.right >= self.maximo_x:
            self.rect.right = self.maximo_x
            self.x = float(self.rect.x)
            self.direccion = -1

    _PALETAS_ESPECTRO = {
        "patrulla": {
            "sombra_suelo": (7, 6, 10),
            "nes_cuerpo": (24, 32, 54),
            "snes_sombra": (20, 26, 40),
            "cuerpo": ENEMIGO_MORTAJA,
            "harapos": ((28, 36, 56), (48, 62, 90)),
            "craneo": HUESO,
            "craneo_borde": NEGRO,
            "garra_snes": HUESO,
            "fuego_base": (60, 210, 190),
            "fuego_amp": (50, 40, 50),
            "estela_ojo": (200, 20, 30),
            "ojo_nes_linea": True,
        },
        "melee": {
            "sombra_suelo": NEGRO_NOCHE,
            "nes_cuerpo": (32, 20, 44),
            "snes_sombra": (26, 16, 32),
            "cuerpo": ENEMIGO_PURPURA,
            "harapos": ((38, 22, 46), (68, 38, 80)),
            "craneo": HUESO_MARFIL,
            "craneo_borde": NEGRO_NOCHE,
            "garra_snes": HUESO_MARFIL,
            "fuego_base": (160, 40, 190),
            "fuego_amp": (50, 30, 50),
            "estela_ojo": CARMESÍ_SANGRE,
            "ojo_nes_linea": False,
        },
    }

    def _dibujar_flash_espectral(self, surface, rect, salto):
        """Dibuja silueta blanca de impacto si hay flash activo y retorna si debe cortar render."""
        if getattr(self, "tiempo_flash", 0.0) <= 0:
            return False
        pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, (rect.x - 2, rect.y + 4 + salto, rect.width + 4, rect.height - 2))
        pygame.draw.circle(surface, FX_IMPACTO_BLANCO, (rect.centerx, rect.y + 9 + salto), 9)
        return True

    def _dibujar_espectro(self, surface, rect, salto, tiempo, estilo, variante, alerta=False):
        """Renderiza el cuerpo esquelético compartido entre espectros patrulleros y melee."""
        paleta = self._PALETAS_ESPECTRO[variante]
        centro_x = rect.centerx
        base_y = rect.bottom + salto
        ojo_offset = self.direccion * 2
        ojo_y = rect.y + 8 + salto

        pygame.draw.ellipse(surface, paleta["sombra_suelo"], (rect.x + 1, rect.bottom - 4, rect.width - 2, 7))

        if estilo == "NES":
            pygame.draw.ellipse(surface, ENEMIGO_RIM_LUZ, (rect.x - 2, rect.y + 4 + salto, rect.width + 4, rect.height - 4))
            pygame.draw.circle(surface, ENEMIGO_RIM_LUZ, (centro_x, rect.y + 9 + salto), 10)
            pygame.draw.ellipse(surface, paleta["nes_cuerpo"], (rect.x, rect.y + 6 + salto, rect.width, rect.height - 6))
            pygame.draw.circle(surface, HUESO_MARFIL, (centro_x, rect.y + 9 + salto), 8)
            pygame.draw.circle(surface, (10, 8, 14), (centro_x, rect.y + 9 + salto), 8, 1)
            pygame.draw.rect(surface, ENEMIGO_OJO_FUEGO, (centro_x - 4 + ojo_offset, ojo_y - 1, 3, 2))
            pygame.draw.rect(surface, ENEMIGO_OJO_FUEGO, (centro_x + 2 + ojo_offset, ojo_y - 1, 3, 2))
            if paleta["ojo_nes_linea"]:
                pygame.draw.line(surface, (255, 220, 220), (centro_x - 5 + ojo_offset, ojo_y), (centro_x + 5 + ojo_offset, ojo_y), 1)
            for lado in (rect.x + 3, rect.right - 4):
                pygame.draw.line(surface, HUESO_MARFIL, (lado, base_y - 2), (lado, base_y + 4), 2)
            return

        es_proc = estilo != "SNES"
        pygame.draw.ellipse(surface, paleta["snes_sombra"], (rect.x - 2, rect.y + 8 + salto, rect.width + 4, rect.height - 6))
        pygame.draw.ellipse(surface, paleta["cuerpo"], (rect.x, rect.y + 6 + salto, rect.width, rect.height - 6))
        if es_proc:
            pygame.draw.arc(surface, TURQUESA_ÁNIMA, (rect.x - 2, rect.y + 3 + salto, rect.width + 4, 16), 0, math.pi, 2)
        else:
            pygame.draw.arc(surface, ENEMIGO_RIM_LUZ, (rect.x - 1, rect.y + 4 + salto, rect.width + 2, 14), 0, math.pi, 2)

        harapo_osc, harapo_cla = paleta["harapos"]
        pygame.draw.polygon(
            surface,
            harapo_osc,
            [(rect.x + 1, rect.y + 14 + salto), (rect.x + 9, rect.y + 22 + salto), (rect.x + 5, rect.y + 29 + salto), (rect.x - 1, rect.y + 20 + salto)],
        )
        pygame.draw.polygon(
            surface,
            harapo_cla,
            [(rect.x + 3, rect.y + 17 + salto), (rect.x + 10, rect.y + 23 + salto), (rect.x + 7, rect.y + 28 + salto), (rect.x + 1, rect.y + 21 + salto)],
        )
        pygame.draw.polygon(
            surface,
            harapo_osc,
            [(rect.right - 1, rect.y + 13 + salto), (rect.right - 10, rect.y + 22 + salto), (rect.right - 4, rect.y + 28 + salto), (rect.right + 1, rect.y + 19 + salto)],
        )

        pygame.draw.circle(surface, paleta["craneo"], (centro_x, rect.y + 9 + salto), 8)
        pygame.draw.circle(surface, paleta["craneo_borde"], (centro_x, rect.y + 9 + salto), 8, 1)
        pygame.draw.arc(
            surface,
            MARFIL_XILOGRAFICO if es_proc else ENEMIGO_RIM_LUZ,
            (centro_x - 8, rect.y + 1 + salto, 16, 16),
            0.2,
            math.pi - 0.2,
            2,
        )

        if es_proc:
            trail_dx = -self.direccion * 4
            pygame.draw.line(surface, paleta["estela_ojo"], (centro_x - 3 + ojo_offset, ojo_y), (centro_x - 3 + ojo_offset + trail_dx, ojo_y), 2)
            pygame.draw.line(surface, paleta["estela_ojo"], (centro_x + 3 + ojo_offset, ojo_y), (centro_x + 3 + ojo_offset + trail_dx, ojo_y), 2)

        for ox in (centro_x - 3 + ojo_offset, centro_x + 3 + ojo_offset):
            if alerta:
                pygame.draw.circle(surface, CARMESÍ_SANGRE, (ox, ojo_y), 3)
                pygame.draw.circle(surface, (255, 40, 50), (ox, ojo_y), 2)
                pygame.draw.circle(surface, BLANCO, (ox, ojo_y), 1)
            else:
                if es_proc:
                    pygame.draw.circle(surface, (180, 20, 30), (ox, ojo_y), 3)
                pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (ox, ojo_y), 2)
                pygame.draw.circle(surface, BLANCO if es_proc else (255, 200, 200), (ox + 1, ojo_y - 1), 1)

        if es_proc:
            pulso = (math.sin(tiempo * 6.0) + 1.0) * 0.5
            fr, fg, fb = paleta["fuego_base"]
            ar, ag, ab = paleta["fuego_amp"]
            col_fuego = (int(fr + ar * pulso), int(fg + ag * pulso), int(fb + ab * pulso))
            pygame.draw.circle(surface, col_fuego, (centro_x, rect.y + 21 + salto), int(2 + 2 * pulso))

        for i in range(3):
            ry = rect.y + 17 + i * 4 + salto
            if not es_proc:
                pygame.draw.line(surface, (10, 8, 14), (rect.x + 8, ry + 1), (rect.right - 8, ry + 1), 1)
            pygame.draw.line(surface, HUESO_MARFIL, (rect.x + 8, ry), (rect.right - 8, ry), 1)

        col_garra = HUESO_MARFIL if es_proc else paleta["garra_snes"]
        for lado, signo in ((4, -1), (rect.width - 5, 1)):
            bx = rect.x + lado
            for dedo_dx in (-2, 0, 2):
                pygame.draw.line(surface, col_garra, (bx + dedo_dx, base_y - 3), (bx + dedo_dx + signo, base_y + 6), 1)


#---- Clase Enemigo ----#
class Enemigo(EntidadPatrullera):
    """Morador de la cripta que patrulla de izquierda a derecha."""

    def actualizar(self, dt):
        if not self.vivo:
            return
        self.actualizar_flash(dt)
        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 23, 23)
        salto = int(math.sin(tiempo * 7 + rect.x * 0.02) * 2)
        if self._dibujar_flash_espectral(surface, rect, salto):
            return

        estilo = resolver_estilo(getattr(config, "ESTILO_ENEMIGOS", "AUTO"))
        self._dibujar_espectro(surface, rect, salto, tiempo, estilo, "patrulla")


#---- Clase EnemigoMelee ----#
class EnemigoMelee(EntidadPatrullera):
    """Enemigo que ataca en rango melee (70px) con ciclo aviso -> estocada -> enfriamiento."""

    def __init__(self, rect, minimo_x, maximo_x):
        super().__init__(rect, minimo_x, maximo_x)
        self.aviso_tiempo = 0.0
        self.estocada_tiempo = 0.0
        self.enfriamiento_tiempo = 0.0
        self.atacando = False

    def reiniciar(self):
        super().reiniciar()
        self.aviso_tiempo = 0.0
        self.estocada_tiempo = 0.0
        self.enfriamiento_tiempo = 0.0
        self.atacando = False

    def rect_espada(self):
        """Devuelve el hitbox activo del mandoble durante la estocada."""
        if not (self.vivo and self.atacando):
            return None
        alcance = 20
        x = self.rect.right - 2 if self.direccion > 0 else self.rect.left - alcance + 2
        return pygame.Rect(x, self.rect.y + 4, alcance, max(12, self.rect.height - 8))

    def actualizar(self, dt, jugador):
        if not self.vivo:
            return

        self.actualizar_flash(dt)

        if self.estocada_tiempo > 0:
            self.estocada_tiempo = max(0.0, self.estocada_tiempo - dt)
            self.x += self.direccion * (VELOCIDAD_ENEMIGO * 2.6) * dt
            self.x = limitar(self.x, self.minimo_x, self.maximo_x)
            self.rect.x = round(self.x)
            if self.estocada_tiempo <= 0:
                self.atacando = False
                self.enfriamiento_tiempo = 0.50
            return

        if self.enfriamiento_tiempo > 0:
            self.enfriamiento_tiempo = max(0.0, self.enfriamiento_tiempo - dt)
            return

        distancia_x = abs(self.rect.centerx - jugador.rect.centerx)
        distancia_y = abs(self.rect.centery - jugador.rect.centery)

        if self.aviso_tiempo > 0:
            self.aviso_tiempo = max(0.0, self.aviso_tiempo - dt)
            if distancia_x > 2:
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            if self.aviso_tiempo <= 0:
                self.estocada_tiempo = 0.22
                self.atacando = True
            return

        # Detecta al jugador en rango melee e inicia la telegrafía de estocada.
        if distancia_x <= 70 and distancia_y <= 24:
            if distancia_x > 2:
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            self.aviso_tiempo = 0.28
            return

        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO)

    def _dibujar_mandoble(self, surface, rect, salto, estilo):
        """Dibuja el mandoble del espectro melee según aviso, estocada o guardia."""
        centro_x = rect.centerx
        base_y = rect.bottom + salto
        signo = self.direccion
        espada_base_x = centro_x + signo * 8
        espada_base_y = rect.y + 14 + salto
        en_aviso = self.aviso_tiempo > 0
        en_estocada = self.atacando

        if en_estocada:
            punta_x = centro_x + signo * 26
            punta_y = rect.y + 12 + salto
        elif en_aviso:
            punta_x = centro_x + signo * 16
            punta_y = rect.y - 6 + salto
        else:
            punta_x = centro_x + signo * 12
            punta_y = base_y - 2

        if estilo == "NES":
            color_hoja = (255, 220, 130) if en_estocada else (ENEMIGO_RIM_LUZ if en_aviso else (180, 190, 210))
            pygame.draw.line(surface, color_hoja, (espada_base_x, espada_base_y), (punta_x, punta_y), 3)
            if en_aviso or en_estocada:
                pygame.draw.line(surface, BLANCO, (espada_base_x, espada_base_y), (punta_x, punta_y), 1)
            return

        pygame.draw.line(surface, MELEE_ACERO_CLARO, (espada_base_x, espada_base_y), (punta_x, punta_y), 3)
        pygame.draw.line(surface, BLANCO, (espada_base_x, espada_base_y), (punta_x, punta_y), 1)
        if en_estocada:
            pygame.draw.line(surface, (255, 195, 110), (espada_base_x, espada_base_y), (punta_x + signo * 4, punta_y), 2)
        elif en_aviso:
            pygame.draw.arc(surface, CARMESÍ_SANGRE, (rect.centerx - 14 + signo * 8, rect.y + 2, 28, 28), 0, 3.14, 2)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 23, 24)
        salto = int(math.sin(tiempo * 7 + rect.x * 0.02) * 2)

        if self.aviso_tiempo > 0:
            rect.x += int(math.sin(tiempo * 55) * 2)
            pygame.draw.arc(surface, (210, 28, 50), (rect.centerx - 20, rect.bottom - 4, 40, 8), 0, math.pi, 2)

        if self._dibujar_flash_espectral(surface, rect, salto):
            return

        estilo = resolver_estilo(getattr(config, "ESTILO_ENEMIGOS", "AUTO"))
        self._dibujar_espectro(surface, rect, salto, tiempo, estilo, "melee", alerta=(self.aviso_tiempo > 0))
        self._dibujar_mandoble(surface, rect, salto, estilo)


#---- Clase Cuervo ----#
class Cuervo:
    """Cuervo poeano que vuela en patrón circular con aleteo articulado y plumas negras."""

    def __init__(self, rect, centro_x, centro_y, radio, velocidad):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.centro_x = centro_x
        self.centro_y = centro_y
        self.radio = radio
        self.velocidad = velocidad
        self.angulo = 0.0
        self.vivo = True
        self.plumas = []
        self.tiempo_pluma = 0.0
        self.tiempo_flash = 0.0

    def reiniciar(self):
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.angulo = 0.0
        self.vivo = True
        self.plumas = []
        self.tiempo_pluma = 0.0
        self.tiempo_flash = 0.0

    def actualizar(self, dt):
        if not self.vivo:
            return

        if getattr(self, "tiempo_flash", 0.0) > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)

        self.angulo += self.velocidad * dt
        self.x = self.centro_x + math.cos(self.angulo) * self.radio - self.rect.width // 2
        self.y = self.centro_y + math.sin(self.angulo) * self.radio * 0.5 - self.rect.height // 2
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)

        # Emisión de plumas negras livianas que caen lentamente
        self.tiempo_pluma += dt
        if self.tiempo_pluma >= 0.38:
            self.tiempo_pluma = 0.0
            if len(self.plumas) < 12:
                self.plumas.append(ParticulaPluma(self.rect.centerx, self.rect.centery))

        for pluma in self.plumas:
            pluma.actualizar(dt)
        self.plumas = [p for p in self.plumas if p.vida > 0]

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return

        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 20, 20)
        if getattr(self, "tiempo_flash", 0.0) > 0:
            pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, rect)
            return

        # Dibujar plumas desprendidas primero
        for pluma in self.plumas:
            pluma.dibujar(surface, camara)

        centro_x = rect.centerx
        base_y = rect.bottom

        # Sombra sutil en el suelo
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Aleteo articulado con apertura tensa en fase descendente
        fase_descenso = math.cos(self.angulo) < 0
        aleteo = int(math.sin(tiempo * 16.0) * (3 if fase_descenso else 5))

        # Cuerpo del cuervo (silueta afilada en negro carbón poeano) con recorte cenital marfil de 2px
        pygame.draw.ellipse(surface, (14, 12, 18), (rect.x + 2, rect.y + 4, rect.width - 4, rect.height - 8))
        pygame.draw.ellipse(surface, (25, 22, 32), (rect.x + 4, rect.y + 5, rect.width - 8, rect.height - 10))
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, (rect.x + 3, rect.y + 3, rect.width - 6, 7), 0.2, math.pi - 0.2, 2)

        # Alas articuladas con 3 primarias escalonadas y borde de luz de recorte
        ala_izq_puntos = [
            (rect.centerx - 2, rect.y + 7),
            (rect.x - (4 if fase_descenso else 2), rect.y + 1 - aleteo),
            (rect.x + 3, rect.y + 5 - aleteo // 2),
            (rect.centerx - 2, rect.y + 9),
        ]
        pygame.draw.polygon(surface, (10, 8, 14), ala_izq_puntos)
        pygame.draw.line(surface, ENEMIGO_RIM_LUZ, ala_izq_puntos[1], ala_izq_puntos[2], 1)

        ala_der_puntos = [
            (rect.centerx + 2, rect.y + 7),
            (rect.right + (4 if fase_descenso else 2), rect.y + 1 - aleteo),
            (rect.right - 3, rect.y + 5 - aleteo // 2),
            (rect.centerx + 2, rect.y + 9),
        ]
        pygame.draw.polygon(surface, (10, 8, 14), ala_der_puntos)
        pygame.draw.line(surface, ENEMIGO_RIM_LUZ, ala_der_puntos[1], ala_der_puntos[2], 1)

        # Cola afilada en cuña
        pygame.draw.polygon(surface, (10, 8, 14), [
            (centro_x - 3, rect.bottom - 5),
            (centro_x, rect.bottom),
            (centro_x + 3, rect.bottom - 5),
        ])

        # Pico curvado de cuervo en cuerno oscuro
        pygame.draw.polygon(surface, (58, 48, 38), [
            (rect.centerx, rect.y + 11),
            (rect.centerx + 5, rect.y + 14),
            (rect.centerx, rect.y + 16),
        ])

        # Ojos con estela ocular roja de 4px
        trail_dx = -4 if math.cos(self.angulo) >= 0 else 4
        ojo_x = centro_x - 2
        ojo_y = rect.y + 10
        pygame.draw.line(surface, (210, 28, 50), (ojo_x, ojo_y), (ojo_x + trail_dx, ojo_y), 1)
        pygame.draw.circle(surface, (235, 180, 40), (ojo_x, ojo_y), 1.5)
        pygame.draw.circle(surface, BLANCO, (ojo_x, ojo_y), 0.5)


#---- Clase Polilla ----#
class Polilla(EntidadPatrullera):
    """Polilla que vuela en zigzag lento. Daño por contacto."""

    def __init__(self, rect, minimo_x, maximo_x):
        super().__init__(rect, minimo_x, maximo_x)
        self.tiempo = 0.0

    def reiniciar(self):
        super().reiniciar()
        self.tiempo = 0.0

    def actualizar(self, dt):
        if not self.vivo:
            return
        self.actualizar_flash(dt)
        self.tiempo += dt
        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO * 0.6)
        # Movimiento vertical suave (zigzag).
        self.rect.y = round(self.inicial_rect.y + math.sin(self.tiempo * 3) * 8)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return
        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 22, 22)
        if getattr(self, "tiempo_flash", 0.0) > 0:
            pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, rect)
            return

        centro_x = rect.centerx
        base_y = rect.bottom

        # Esporas lumínicas orgánicas al aproximarse al cambio de vector
        if abs(self.rect.left - self.minimo_x) < 16 or abs(self.rect.right - self.maximo_x) < 16:
            pygame.draw.circle(surface, (92, 220, 200), (centro_x + int(math.sin(tiempo * 14.0) * 8), rect.y + 3), 1)

        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Cuerpo de polilla con borde turquesa y recorte cenital marfil de 2px
        pygame.draw.ellipse(surface, (28, 38, 48), (rect.x + 3, rect.y + 4, rect.width - 6, rect.height - 8))
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, (rect.x + 3, rect.y + 3, rect.width - 6, 8), 0.2, math.pi - 0.2, 2)

        # Alas con borde de luz de recorte
        pygame.draw.ellipse(surface, (55, 60, 75), (rect.x, rect.y + 2, rect.width // 2, rect.height // 2))
        pygame.draw.ellipse(surface, (55, 60, 75), (rect.x + rect.width // 2, rect.y + 2, rect.width // 2, rect.height // 2))
        pygame.draw.arc(surface, ENEMIGO_RIM_LUZ, (rect.x, rect.y + 2, rect.width // 2, rect.height // 2), 0, math.pi, 1)
        pygame.draw.arc(surface, ENEMIGO_RIM_LUZ, (rect.x + rect.width // 2, rect.y + 2, rect.width // 2, rect.height // 2), 0, math.pi, 1)

        # Estela ocular roja de 4px y ojos brillantes
        trail_dx = -self.direccion * 4
        pygame.draw.line(surface, (210, 28, 50), (centro_x - 2, rect.y + 8), (centro_x - 2 + trail_dx, rect.y + 8), 1)
        pygame.draw.line(surface, (210, 28, 50), (centro_x + 2, rect.y + 8), (centro_x + 2 + trail_dx, rect.y + 8), 1)
        pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (centro_x - 2, rect.y + 8), 1.5)
        pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (centro_x + 2, rect.y + 8), 1.5)


#---- Clase Araña ----#
class Araña(EntidadPatrullera):
    """Araña que se mueve por el techo o suelo. Daño por contacto."""

    def actualizar(self, dt):
        if not self.vivo:
            return
        self.actualizar_flash(dt)
        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO * 0.8)

    def dibujar(self, surface, camara, tiempo):
        if not self.vivo:
            return
        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 22, 18)
        if getattr(self, "tiempo_flash", 0.0) > 0:
            pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, rect)
            return

        centro_x = rect.centerx
        base_y = rect.bottom

        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x + 2, base_y - 4, rect.width - 4, 5))

        # Cuerpo de araña con recorte cenital marfil de 2px
        pygame.draw.ellipse(surface, (18, 14, 24), (rect.x + 3, rect.y + 4, rect.width - 6, rect.height - 7))
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, (rect.x + 3, rect.y + 3, rect.width - 6, 7), 0.2, math.pi - 0.2, 2)

        # Patas articuladas con vibración rápida
        vib = int(math.sin(tiempo * 24.0) * 2)
        for i in range(3):
            dx = (i - 1) * 4
            pata_y = rect.y + 13 + (vib if i % 2 == 0 else -vib)
            pygame.draw.line(surface, (24, 20, 32), (centro_x + dx, rect.y + 8), (rect.x + dx - 5, pata_y), 2)
            pygame.draw.line(surface, ENEMIGO_RIM_LUZ, (rect.x + dx - 5, pata_y), (rect.x + dx - 3, pata_y), 1)
            pygame.draw.line(surface, (24, 20, 32), (centro_x + dx, rect.y + 8), (rect.right - dx + 5, pata_y), 2)
            pygame.draw.line(surface, ENEMIGO_RIM_LUZ, (rect.right - dx + 3, pata_y), (rect.right - dx + 5, pata_y), 1)

        # Ojos con estela ocular roja de 4px
        trail_dx = -self.direccion * 4
        pygame.draw.line(surface, (210, 28, 50), (centro_x - 2, rect.y + 7), (centro_x - 2 + trail_dx, rect.y + 7), 1)
        pygame.draw.line(surface, (210, 28, 50), (centro_x + 2, rect.y + 7), (centro_x + 2 + trail_dx, rect.y + 7), 1)
        pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (centro_x - 2, rect.y + 7), 1.5)
        pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (centro_x + 2, rect.y + 7), 1.5)
        pygame.draw.circle(surface, ROJO, (centro_x - 2, rect.y + 7), 1)
        pygame.draw.circle(surface, ROJO, (centro_x + 2, rect.y + 7), 1)
