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

#---- Paletas por variante ----#
PALETAS_ESPECTRO = {
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


#---- Clase EntidadPatrullera ----#
class EntidadPatrullera:
    """Clase base para criaturas que patrullan con rebote en limites."""

    _PALETAS_ESPECTRO = PALETAS_ESPECTRO

    def __init__(self, rect, minimo_x, maximo_x):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.minimo_x = int(minimo_x)
        self.maximo_x = int(maximo_x)
        self.reiniciar()

    def reiniciar(self):
        """Restaura posicion, direccion y vida de la entidad."""
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.direccion = 1
        self.vivo = True
        self.tiempo_flash = 0.0

    def actualizar_flash(self, dt):
        """Reduce el temporizador de flash al recibir danio."""
        if getattr(self, "tiempo_flash", 0.0) > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)

    def avanzar_patrulla(self, dt, velocidad):
        """Desplaza horizontalmente y rebota contra los limites de plataforma."""
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

    def _dibujar_flash_espectral(self, surface, rect, salto):
        # Silueta blanca de impacto mientras dura el flash
        if getattr(self, "tiempo_flash", 0.0) <= 0:
            return False
        elipse = (rect.x - 2, rect.y + 4 + salto, rect.width + 4, rect.height - 2)
        pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, elipse)
        pygame.draw.circle(surface, FX_IMPACTO_BLANCO, (rect.centerx, rect.y + 9 + salto), 9)
        return True

    def _dibujar_espectro_nes(self, surface, rect, salto, paleta, ojo_offset, ojo_y):
        # Variante simplificada estilo 8 bits
        centro_x = rect.centerx
        base_y = rect.bottom + salto
        elipse_rim = (rect.x - 2, rect.y + 4 + salto, rect.width + 4, rect.height - 4)
        pygame.draw.ellipse(surface, ENEMIGO_RIM_LUZ, elipse_rim)
        pygame.draw.circle(surface, ENEMIGO_RIM_LUZ, (centro_x, rect.y + 9 + salto), 10)
        elipse_cpo = (rect.x, rect.y + 6 + salto, rect.width, rect.height - 6)
        pygame.draw.ellipse(surface, paleta["nes_cuerpo"], elipse_cpo)
        pygame.draw.circle(surface, HUESO_MARFIL, (centro_x, rect.y + 9 + salto), 8)
        pygame.draw.circle(surface, (10, 8, 14), (centro_x, rect.y + 9 + salto), 8, 1)
        pygame.draw.rect(surface, ENEMIGO_OJO_FUEGO, (centro_x - 4 + ojo_offset, ojo_y - 1, 3, 2))
        pygame.draw.rect(surface, ENEMIGO_OJO_FUEGO, (centro_x + 2 + ojo_offset, ojo_y - 1, 3, 2))
        if paleta["ojo_nes_linea"]:
            p0 = (centro_x - 5 + ojo_offset, ojo_y)
            p1 = (centro_x + 5 + ojo_offset, ojo_y)
            pygame.draw.line(surface, (255, 220, 220), p0, p1, 1)
        for lado in (rect.x + 3, rect.right - 4):
            pygame.draw.line(surface, HUESO_MARFIL, (lado, base_y - 2), (lado, base_y + 4), 2)

    def _dibujar_cuerpo_y_harapos(self, surface, rect, salto, paleta, es_proc):
        # Cuerpo espectral, harapos y craneo con borde de luz
        centro_x = rect.centerx
        sombra_box = (rect.x - 2, rect.y + 8 + salto, rect.width + 4, rect.height - 6)
        pygame.draw.ellipse(surface, paleta["snes_sombra"], sombra_box)
        cpo_box = (rect.x, rect.y + 6 + salto, rect.width, rect.height - 6)
        pygame.draw.ellipse(surface, paleta["cuerpo"], cpo_box)
        if es_proc:
            arco = (rect.x - 2, rect.y + 3 + salto, rect.width + 4, 16)
            pygame.draw.arc(surface, TURQUESA_ÁNIMA, arco, 0, math.pi, 2)
        else:
            arco = (rect.x - 1, rect.y + 4 + salto, rect.width + 2, 14)
            pygame.draw.arc(surface, ENEMIGO_RIM_LUZ, arco, 0, math.pi, 2)

        harapo_osc, harapo_cla = paleta["harapos"]
        pol_1 = [
            (rect.x + 1, rect.y + 14 + salto), (rect.x + 9, rect.y + 22 + salto),
            (rect.x + 5, rect.y + 29 + salto), (rect.x - 1, rect.y + 20 + salto),
        ]
        pol_2 = [
            (rect.x + 3, rect.y + 17 + salto), (rect.x + 10, rect.y + 23 + salto),
            (rect.x + 7, rect.y + 28 + salto), (rect.x + 1, rect.y + 21 + salto),
        ]
        pol_3 = [
            (rect.right - 1, rect.y + 13 + salto), (rect.right - 10, rect.y + 22 + salto),
            (rect.right - 4, rect.y + 28 + salto), (rect.right + 1, rect.y + 19 + salto),
        ]
        pygame.draw.polygon(surface, harapo_osc, pol_1)
        pygame.draw.polygon(surface, harapo_cla, pol_2)
        pygame.draw.polygon(surface, harapo_osc, pol_3)

        pygame.draw.circle(surface, paleta["craneo"], (centro_x, rect.y + 9 + salto), 8)
        pygame.draw.circle(surface, paleta["craneo_borde"], (centro_x, rect.y + 9 + salto), 8, 1)
        col_recorte = MARFIL_XILOGRAFICO if es_proc else ENEMIGO_RIM_LUZ
        box_craneo = (centro_x - 8, rect.y + 1 + salto, 16, 16)
        pygame.draw.arc(surface, col_recorte, box_craneo, 0.2, math.pi - 0.2, 2)

    def _dibujar_rasgos_espectro(self, surface, rect, salto, tiempo, paleta, es_proc, alerta):
        # Ojos, fuego interior, costillas y garras
        centro_x = rect.centerx
        base_y = rect.bottom + salto
        ojo_offset = self.direccion * 2
        ojo_y = rect.y + 8 + salto
        if es_proc:
            trail_dx = -self.direccion * 4
            for ox in (centro_x - 3 + ojo_offset, centro_x + 3 + ojo_offset):
                pygame.draw.line(surface, paleta["estela_ojo"], (ox, ojo_y), (ox + trail_dx, ojo_y), 2)

        for ox in (centro_x - 3 + ojo_offset, centro_x + 3 + ojo_offset):
            if alerta:
                pygame.draw.circle(surface, CARMESÍ_SANGRE, (ox, ojo_y), 3)
                pygame.draw.circle(surface, (255, 40, 50), (ox, ojo_y), 2)
                pygame.draw.circle(surface, BLANCO, (ox, ojo_y), 1)
            else:
                if es_proc:
                    pygame.draw.circle(surface, (180, 20, 30), (ox, ojo_y), 3)
                pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (ox, ojo_y), 2)
                col_brillo = BLANCO if es_proc else (255, 200, 200)
                pygame.draw.circle(surface, col_brillo, (ox + 1, ojo_y - 1), 1)

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
                p0 = (bx + dedo_dx, base_y - 3)
                p1 = (bx + dedo_dx + signo, base_y + 6)
                pygame.draw.line(surface, col_garra, p0, p1, 1)

    def _dibujar_espectro(self, surface, rect, salto, tiempo, estilo, variante, alerta=False):
        # Dibuja espectros patrulleros y melee segun el estilo visual activo
        paleta = self._PALETAS_ESPECTRO[variante]
        sombra = (rect.x + 1, rect.bottom - 4, rect.width - 2, 7)
        pygame.draw.ellipse(surface, paleta["sombra_suelo"], sombra)

        if estilo == "NES":
            self._dibujar_espectro_nes(surface, rect, salto, paleta, self.direccion * 2, rect.y + 8 + salto)
            return

        es_proc = estilo != "SNES"
        self._dibujar_cuerpo_y_harapos(surface, rect, salto, paleta, es_proc)
        self._dibujar_rasgos_espectro(surface, rect, salto, tiempo, paleta, es_proc, alerta)


#---- Clase Enemigo ----#
class Enemigo(EntidadPatrullera):
    """Morador de la cripta que patrulla de izquierda a derecha."""

    def actualizar(self, dt):
        """Actualiza flash de impacto y patrulla."""
        if not self.vivo:
            return
        self.actualizar_flash(dt)
        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza el espectro patrullero en pantalla."""
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
    """Enemigo con estocada cuerpo a cuerpo y ciclo aviso-golpe-enfriamiento."""

    def __init__(self, rect, minimo_x, maximo_x):
        super().__init__(rect, minimo_x, maximo_x)
        self.aviso_tiempo = 0.0
        self.estocada_tiempo = 0.0
        self.enfriamiento_tiempo = 0.0
        self.atacando = False

    def reiniciar(self):
        """Restaura temporizadores de estocada ademas de la patrulla base."""
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
        """Avanza patrulla, detecta rango cuerpo a cuerpo y ejecuta estocada."""
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

        if distancia_x <= 70 and distancia_y <= 24:
            if distancia_x > 2:
                self.direccion = 1 if jugador.rect.centerx > self.rect.centerx else -1
            self.aviso_tiempo = 0.28
            return

        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO)

    def _dibujar_mandoble(self, surface, rect, salto, estilo):
        # Espada en guardia, telegrafia o estocada extendida
        centro_x = rect.centerx
        base_y = rect.bottom + salto
        signo = self.direccion
        base_p = (centro_x + signo * 8, rect.y + 14 + salto)
        en_aviso = self.aviso_tiempo > 0
        en_estocada = self.atacando

        if en_estocada:
            punta = (centro_x + signo * 26, rect.y + 12 + salto)
        elif en_aviso:
            punta = (centro_x + signo * 16, rect.y - 6 + salto)
        else:
            punta = (centro_x + signo * 12, base_y - 2)

        if estilo == "NES":
            col_av = ENEMIGO_RIM_LUZ if en_aviso else (180, 190, 210)
            color_hoja = (255, 220, 130) if en_estocada else col_av
            pygame.draw.line(surface, color_hoja, base_p, punta, 3)
            if en_aviso or en_estocada:
                pygame.draw.line(surface, BLANCO, base_p, punta, 1)
            return

        pygame.draw.line(surface, MELEE_ACERO_CLARO, base_p, punta, 3)
        pygame.draw.line(surface, BLANCO, base_p, punta, 1)
        if en_estocada:
            punta_brillo = (punta[0] + signo * 4, punta[1])
            pygame.draw.line(surface, (255, 195, 110), base_p, punta_brillo, 2)
        elif en_aviso:
            arco = (rect.centerx - 14 + signo * 8, rect.y + 2, 28, 28)
            pygame.draw.arc(surface, CARMESÍ_SANGRE, arco, 0, 3.14, 2)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza el guardia con vibracion y arco de aviso si telegrafia."""
        if not self.vivo:
            return
        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 23, 24)
        salto = int(math.sin(tiempo * 7 + rect.x * 0.02) * 2)

        if self.aviso_tiempo > 0:
            rect.x += int(math.sin(tiempo * 55) * 2)
            arco = (rect.centerx - 20, rect.bottom - 4, 40, 8)
            pygame.draw.arc(surface, (210, 28, 50), arco, 0, math.pi, 2)

        if self._dibujar_flash_espectral(surface, rect, salto):
            return

        estilo = resolver_estilo(getattr(config, "ESTILO_ENEMIGOS", "AUTO"))
        alerta = self.aviso_tiempo > 0
        self._dibujar_espectro(surface, rect, salto, tiempo, estilo, "melee", alerta=alerta)
        self._dibujar_mandoble(surface, rect, salto, estilo)


#---- Clase Cuervo ----#
class Cuervo:
    """Cuervo que orbita en circulo dejando plumas negras."""

    def __init__(self, rect, centro_x, centro_y, radio, velocidad):
        self.rect = pygame.Rect(rect)
        self.inicial_rect = pygame.Rect(rect)
        self.centro_x = centro_x
        self.centro_y = centro_y
        self.radio = radio
        self.velocidad = velocidad
        self.reiniciar()

    def reiniciar(self):
        """Restaura el cuervo al inicio de su orbita y limpia plumas."""
        self.rect = pygame.Rect(self.inicial_rect)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.angulo = 0.0
        self.vivo = True
        self.plumas = []
        self.tiempo_pluma = 0.0
        self.tiempo_flash = 0.0

    def actualizar(self, dt):
        """Avanza la orbita eliptica y emite plumas periodicas."""
        if not self.vivo:
            return
        if getattr(self, "tiempo_flash", 0.0) > 0:
            self.tiempo_flash = max(0.0, self.tiempo_flash - dt)

        self.angulo += self.velocidad * dt
        self.x = self.centro_x + math.cos(self.angulo) * self.radio - self.rect.width // 2
        self.y = self.centro_y + math.sin(self.angulo) * self.radio * 0.5 - self.rect.height // 2
        self.rect.x = round(self.x)
        self.rect.y = round(self.y)

        self.tiempo_pluma += dt
        if self.tiempo_pluma >= 0.38:
            self.tiempo_pluma = 0.0
            if len(self.plumas) < 12:
                self.plumas.append(ParticulaPluma(self.rect.centerx, self.rect.centery))

        for pluma in self.plumas:
            pluma.actualizar(dt)
        self.plumas = [p for p in self.plumas if p.vida > 0]

    def _dibujar_alas_y_cuerpo(self, surface, rect, tiempo):
        # Dibuja sombra, cuerpo y aleteo articulado en fase
        centro_x = rect.centerx
        pygame.draw.ellipse(surface, NEGRO_NOCHE, (rect.x + 2, rect.bottom - 4, rect.width - 4, 5))

        fase_descenso = math.cos(self.angulo) < 0
        aleteo = int(math.sin(tiempo * 16.0) * (3 if fase_descenso else 5))
        pygame.draw.ellipse(surface, (14, 12, 18), (rect.x + 2, rect.y + 4, rect.width - 4, rect.height - 8))
        pygame.draw.ellipse(surface, (25, 22, 32), (rect.x + 4, rect.y + 5, rect.width - 8, rect.height - 10))
        arco_c = (rect.x + 3, rect.y + 3, rect.width - 6, 7)
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, arco_c, 0.2, math.pi - 0.2, 2)

        ext = 4 if fase_descenso else 2
        ala_izq = [
            (centro_x - 2, rect.y + 7),
            (rect.x - ext, rect.y + 1 - aleteo),
            (rect.x + 3, rect.y + 5 - aleteo // 2),
            (centro_x - 2, rect.y + 9),
        ]
        ala_der = [
            (centro_x + 2, rect.y + 7),
            (rect.right + ext, rect.y + 1 - aleteo),
            (rect.right - 3, rect.y + 5 - aleteo // 2),
            (centro_x + 2, rect.y + 9),
        ]
        for pts in (ala_izq, ala_der):
            pygame.draw.polygon(surface, (10, 8, 14), pts)
            pygame.draw.line(surface, ENEMIGO_RIM_LUZ, pts[1], pts[2], 1)

    def _dibujar_cola_y_rostro(self, surface, rect):
        # Dibuja cola en cunia, pico curvado y estela ocular
        centro_x = rect.centerx
        cola = [(centro_x - 3, rect.bottom - 5), (centro_x, rect.bottom), (centro_x + 3, rect.bottom - 5)]
        pygame.draw.polygon(surface, (10, 8, 14), cola)
        pico = [(centro_x, rect.y + 11), (centro_x + 5, rect.y + 14), (centro_x, rect.y + 16)]
        pygame.draw.polygon(surface, (58, 48, 38), pico)

        trail_dx = -4 if math.cos(self.angulo) >= 0 else 4
        ojo_x = centro_x - 2
        ojo_y = rect.y + 10
        pygame.draw.line(surface, (210, 28, 50), (ojo_x, ojo_y), (ojo_x + trail_dx, ojo_y), 1)
        pygame.draw.circle(surface, (235, 180, 40), (ojo_x, ojo_y), 1.5)
        pygame.draw.circle(surface, BLANCO, (ojo_x, ojo_y), 0.5)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza las plumas sueltas y la silueta del cuervo."""
        if not self.vivo:
            return
        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 20, 20)
        if getattr(self, "tiempo_flash", 0.0) > 0:
            pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, rect)
            return
        for pluma in self.plumas:
            pluma.dibujar(surface, camara)
        self._dibujar_alas_y_cuerpo(surface, rect, tiempo)
        self._dibujar_cola_y_rostro(surface, rect)


#---- Clase Polilla ----#
class Polilla(EntidadPatrullera):
    """Polilla que vuela en zigzag lento."""

    def __init__(self, rect, minimo_x, maximo_x):
        super().__init__(rect, minimo_x, maximo_x)
        self.tiempo = 0.0

    def reiniciar(self):
        """Restaura el ciclo vertical ademas de la patrulla."""
        super().reiniciar()
        self.tiempo = 0.0

    def actualizar(self, dt):
        """Actualiza patrulla horizontal y oscilacion sinusoidal."""
        if not self.vivo:
            return
        self.actualizar_flash(dt)
        self.tiempo += dt
        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO * 0.6)
        self.rect.y = round(self.inicial_rect.y + math.sin(self.tiempo * 3) * 8)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza alas, ojos y esporas al borde del recorrido."""
        if not self.vivo:
            return
        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 22, 22)
        if getattr(self, "tiempo_flash", 0.0) > 0:
            pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, rect)
            return

        centro_x = rect.centerx
        cerca_borde = (
            abs(self.rect.left - self.minimo_x) < 16
            or abs(self.rect.right - self.maximo_x) < 16
        )
        if cerca_borde:
            espora_x = centro_x + int(math.sin(tiempo * 14.0) * 8)
            pygame.draw.circle(surface, (92, 220, 200), (espora_x, rect.y + 3), 1)

        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x + 2, rect.bottom - 4, rect.width - 4, 5))
        cpo = (rect.x + 3, rect.y + 4, rect.width - 6, rect.height - 8)
        pygame.draw.ellipse(surface, (28, 38, 48), cpo)
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, (rect.x + 3, rect.y + 3, rect.width - 6, 8), 0.2, math.pi - 0.2, 2)

        for ax in (rect.x, rect.x + rect.width // 2):
            ala = (ax, rect.y + 2, rect.width // 2, rect.height // 2)
            pygame.draw.ellipse(surface, (55, 60, 75), ala)
            pygame.draw.arc(surface, ENEMIGO_RIM_LUZ, ala, 0, math.pi, 1)

        trail_dx = -self.direccion * 4
        for ox in (centro_x - 2, centro_x + 2):
            pygame.draw.line(surface, (210, 28, 50), (ox, rect.y + 8), (ox + trail_dx, rect.y + 8), 1)
            pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (ox, rect.y + 8), 1.5)


#---- Clase Araña ----#
class Araña(EntidadPatrullera):
    """Arana que patrulla por el techo o el suelo."""

    def actualizar(self, dt):
        """Actualiza patrulla rapida horizontal."""
        if not self.vivo:
            return
        self.actualizar_flash(dt)
        self.avanzar_patrulla(dt, VELOCIDAD_ENEMIGO * 0.8)

    def dibujar(self, surface, camara, tiempo):
        """Renderiza el cuerpo y las patas articuladas de la arana."""
        if not self.vivo:
            return
        rect_cam = camara.aplicar_rect(self.rect)
        rect = _escalar_rect_visual_enemigo(rect_cam, 22, 18)
        if getattr(self, "tiempo_flash", 0.0) > 0:
            pygame.draw.ellipse(surface, FX_IMPACTO_BLANCO, rect)
            return

        centro_x = rect.centerx
        pygame.draw.ellipse(surface, (7, 6, 10), (rect.x + 2, rect.bottom - 4, rect.width - 4, 5))
        pygame.draw.ellipse(surface, (18, 14, 24), (rect.x + 3, rect.y + 4, rect.width - 6, rect.height - 7))
        pygame.draw.arc(surface, MARFIL_XILOGRAFICO, (rect.x + 3, rect.y + 3, rect.width - 6, 7), 0.2, math.pi - 0.2, 2)

        vib = int(math.sin(tiempo * 24.0) * 2)
        for i in range(3):
            dx = (i - 1) * 4
            pata_y = rect.y + 13 + (vib if i % 2 == 0 else -vib)
            pygame.draw.line(surface, (24, 20, 32), (centro_x + dx, rect.y + 8), (rect.x + dx - 5, pata_y), 2)
            pygame.draw.line(surface, ENEMIGO_RIM_LUZ, (rect.x + dx - 5, pata_y), (rect.x + dx - 3, pata_y), 1)
            pygame.draw.line(surface, (24, 20, 32), (centro_x + dx, rect.y + 8), (rect.right - dx + 5, pata_y), 2)
            pygame.draw.line(surface, ENEMIGO_RIM_LUZ, (rect.right - dx + 3, pata_y), (rect.right - dx + 5, pata_y), 1)

        trail_dx = -self.direccion * 4
        for ox in (centro_x - 2, centro_x + 2):
            pygame.draw.line(surface, (210, 28, 50), (ox, rect.y + 7), (ox + trail_dx, rect.y + 7), 1)
            pygame.draw.circle(surface, ENEMIGO_OJO_FUEGO, (ox, rect.y + 7), 1.5)
            pygame.draw.circle(surface, ROJO, (ox, rect.y + 7), 1)
